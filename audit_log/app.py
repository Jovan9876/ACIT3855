import datetime
import json
import logging
import logging.config
from threading import Thread

import connexion
import yaml
from base import Base
from connexion import NoContent
from flask_cors import CORS, cross_origin
from pykafka import KafkaClient
from pykafka.common import OffsetType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

logger = logging.getLogger("basicLogger")

logger.info(
    f"Connecting to DB, Hostname: {app_config['mysql']['hostname']}, Port:{app_config['mysql']['port']}"
)


def getStepReading(index):
    """ Get Step Reading in History """
    client = KafkaClient(
        hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    )
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    logger.info(f"Retrieving Step at index {index}")
    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)
            if count == index and msg["type"] == "addStepInfo":
                return msg, 200
            if msg["type"] == "addWeightInfo":
                count -= 1
            count += 1

    except:
        logger.error("No more messages found")
    logger.error(f"Could not find Step at index {index}")
    return {"message": "Not Found"}, 404


def getWeightReading(index):
    """ Get Weight Reading in History """
    client = KafkaClient(
        hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    )
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    logger.info(f"Retrieving Weight at index {index}")
    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)

            if count == index and msg["type"] == "addWeightInfo":
                return msg, 200
            if msg["type"] == "addStepInfo":
                count -= 1
            count += 1
    except:
        logger.error("No more messages found")
    logger.error(f"Could not find Weight at index {index}")
    return {"message": "Not Found"}, 404


def getHealth():
    """Returns the health of the system"""
    return {"audit": "running"}, 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config["CORS_HEADERS"] = "Content-Type"

if __name__ == "__main__":
    app.run(port=8110, debug=True)
