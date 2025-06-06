import datetime
import logging
import logging.config
import os
import os.path
from statistics import mean

import connexion
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from base import Base
from connexion import NoContent
from create_tables import create_tables
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stats import Stats

if os.path.isfile('/data/stats.sqlite') == True:
    print("Stats sqllite exists")
else:
    create_tables()
    print("Created stats sql lite file")

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, "r") as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine(f"sqlite:///{app_config['datastore']['filename']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def getStats():
    """ Get latest statistics from database """
    session = DB_SESSION()
    logger.info("Request for statistics has started")
    latest_stats = session.query(Stats).order_by(Stats.id.desc()).first()

    if latest_stats is None:
        logger.error("Statistics do not exist")

        return "Statistics do not exist", 404
    else:
        stat_obj = latest_stats.to_dict()
        logger.debug(f"Recieved Stats object {stat_obj}")
        logger.info("Request for statistics completed")

        return stat_obj, 200


def populateStats():
    """ Periodically update stats """
    
    session = DB_SESSION()
    logger.info("Periodic processing has started")
    last_datetime = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if last_datetime is None:
        # If nothing in the database add this value
        stats = Stats(
            12488,
            4000,
            12,
            8,
            20,
            13488,
            32,
            800,
            40,
            datetime.datetime.strptime(
                "2022-10-05 20:30:00.000000", "%Y-%m-%d %H:%M:%S.%f"
            ),
        )
        session.add(stats)
        session.commit()
    else:
        # Get last_datetime stamp from latest stats object
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        last_datetime = last_datetime.to_dict()["lastUpdated"]

        # Send a request for step and weight information from the last_updateed time
        steps = requests.get(
            f"{app_config['eventstore']['url']}/read/steps?start_timestamp={last_datetime}&end_timestamp={current_time}"
        )
        weight = requests.get(
            f"{app_config['eventstore']['url']}/read/weight?start_timestamp={last_datetime}&end_timestamp={current_time}"
        )

        if (len(steps.json()) == 0) or (len(weight.json()) == 0):
            # If the steps or weight request doesnt return 200 log an error and end processing
            logger.error(
                f"Steps request returned {steps.json()} Weight request returned {weight.json()}"
            )
        else:
            # Assign lists to perform calculations later
            avg_num_steps = []
            avg_floors_climbed = []
            avg_elevation = []
            max_distance = []
            avg_weight_lost = []
            avg_calories_burned = []
            max_weight_lost = []
            # How many total requests were returned
            logger.info(
                f"Query for step and weight information recieved {len(steps.json()) + len(weight.json())} events"
            )

            if len(steps.json()) + len(weight.json()) != 0:
                # If steps or weight returned something
                for item in steps.json():
                    logger.debug(f"Processed Step event with traceID {item['traceID']}")
                    avg_num_steps.append(item["numSteps"])
                    avg_floors_climbed.append(item["floorsClimbed"])
                    avg_elevation.append(item["elevation"])
                    max_distance.append(item["totalDistance"])
                for item in weight.json():
                    logger.debug(
                        f"Processed Weight event with traceID {item['traceID']}"
                    )
                    avg_weight_lost.append(item["weightLost"])
                    avg_calories_burned.append(item["caloriesBurned"])
                    max_weight_lost.append(item["weightLost"])
                    stats = Stats(
                        len(steps.json()),
                        mean(avg_num_steps),
                        mean(avg_floors_climbed),
                        mean(avg_elevation),
                        max(max_distance),
                        len(weight.json()),
                        mean(avg_weight_lost),
                        mean(avg_calories_burned),
                        max(max_weight_lost),
                        datetime.datetime.strptime(
                            current_time, "%Y-%m-%d %H:%M:%S.%f"
                        ),
                    )
                session.add(stats)
                session.commit()
                session.close()
                logger.debug(
                    f"Number of step readings: {len(steps.json())}, Average number of steps: {mean(avg_num_steps)}, Average floors climbed: {mean(avg_floors_climbed)}, Average elevation: {mean(avg_elevation)}, Max distance: {max(max_distance)}, Number of weight readings: {len(weight.json())}, Average weight lost: {mean(avg_weight_lost)}, Average calories burned: {mean(avg_calories_burned)}, Max weight lost: {max(max_weight_lost)}, Last updated at: {current_time}"
                )
    logger.info("Processing period has ended")


def getHealth():
    """Returns the health of the system"""
    return {"processing": "running"}, 200


def initScheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        populateStats, "interval", seconds=app_config["scheduler"]["period_sec"]
    )
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml",base_path="/processing", strict_validation=True, validate_responses=True)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == "__main__":
    initScheduler()
    app.run(port=8100, use_reloader=False)
