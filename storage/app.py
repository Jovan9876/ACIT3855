import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from weight import Weight
from step import Step
import logging, logging.config
import yaml
import datetime
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import json
from sqlalchemy.exc import IntegrityError
from create_tables_mysql import create_tables
import time

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

DB_ENGINE = create_engine(
    f"mysql+pymysql://{app_config['mysql']['user']}:{app_config['mysql']['password']}@{app_config['mysql']['hostname']}:{app_config['mysql']['port']}/{app_config['mysql']['db']}"
)

Base.metadata.bind = DB_ENGINE

DB_SESSION = sessionmaker(bind=DB_ENGINE)

session = DB_SESSION()
try:
    exists = session.query(Step).first()
except:
    create_tables()
    session.close()

logger = logging.getLogger("basicLogger")

logger.info(f"Connecting to DB, Hostname: {app_config['mysql']['hostname']}, Port:{app_config['mysql']['port']}")


def getStepInfo(start_timestamp, end_timestamp):
    """Gets new step information after the timestamp"""
    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    readings = session.query(Step).filter(Step.date_created >= start_timestamp, Step.date_created < end_timestamp)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info(
        f"Query for Step Information after {start_timestamp_datetime} and before {end_timestamp_datetime} returns {len(results_list)} results"
    )

    return results_list, 200



def getWeightInfo(start_timestamp, end_timestamp):
    """Gets new step information after the timestamp"""
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    readings = session.query(Weight).filter(Weight.date_created >= start_timestamp, Weight.date_created < end_timestamp)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info(
        f"Query for Weight Information after {start_timestamp_datetime} and before {end_timestamp_datetime} returns {len(results_list)} results"
    )
    
    return results_list, 200


def process_messages():
    """ Process event messages """
    max_retries = app_config['connection']['retries']
    current_tries = 0
    while current_tries < max_retries:
        logger.info(f"Trying to connect to Kafka ATTEMPT {current_tries}")
        try:
            client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
            topic = client.topics[str.encode(app_config["events"]["topic"])]
        except:
            current_tries += 1
            logger.error(f"Connection to Kafka failed ATTEMPT {current_tries}")
            time.sleep(app_config['scheduler']['sleep'])
            continue
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
    reset_offset_on_start=False,
    auto_offset_reset=OffsetType.LATEST)
    
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "addWeightInfo":
            session = DB_SESSION()

            weight = Weight(
                payload["userID"],
                payload["caloriesBurned"],
                payload["weightLost"],
                payload["newWeight"],
                payload["fitnessScore"],
                payload["timestamp"],
                payload["traceID"],
            )
            try:
                session.add(weight)
                session.commit()
                session.close()
                logger.debug(
                    f"Stored event addWeightInfo request with a trace id of {payload['traceID']}"
                )
            except IntegrityError:
                session.rollback()
                print("Duplicate entry detected!")

        elif msg["type"] == "addStepInfo":
            session = DB_SESSION()

            step = Step(
                payload["userID"],
                payload["numSteps"],
                payload["totalDistance"],
                payload["elevation"],
                payload["floorsClimbed"],
                payload["timestamp"],
                payload["traceID"],
            )
            try:
                session.add(step)
                session.commit()
                session.close()
                logger.debug(
                    f"Stored event addStepInfo request with a trace id of {payload['traceID']}"
                )
            except IntegrityError: 
                session.rollback()
                print("Duplicate entry detected!")
            
        # Commit the new message as being read
        consumer.commit_offsets()

def getHealth():
    """Returns the health of the system"""
    return {"storage": "running"}, 200

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, debug=True)
