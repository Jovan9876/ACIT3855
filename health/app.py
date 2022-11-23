import datetime
import json
import logging
import logging.config
import os
import time

import connexion
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
from requests.adapters import HTTPAdapter, Retry

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


def checkHealth():
    logger.info("Checking health of services")
    statusObj = {}
    # Loop over services in config
    for service in app_config["services"]:
        logger.info(f"Checking health of {service}")
        # Try to get the health of the service if error its down
        try:
            res = requests.get(f"{app_config['services'][service]}/health", timeout=5)
            if res.status_code == 200:
                statusObj[service] = "Running"
            else:
                statusObj[service] = "Down"
        except requests.exceptions.ConnectionError as e:
            logger.info(f"Error connecting to {service}")
            if service not in statusObj:
                statusObj[service] = "Something went wrong"
    # Add the last updated time to the current time
    statusObj["lastUpdate"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    logger.info(f"Appending {statusObj} to status.json")

    # Write the status to the status.json file
    with open("status.json", "a") as f:
        json.dump(statusObj, f)

    logger.info("Health check complete")

    return statusObj, 200


def initScheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        checkHealth, "interval", seconds=app_config["scheduler"]["period_sec"]
    )
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", base_path="/health", strict_validation=True, validate_responses=True)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    initScheduler()
    app.run(port=8120, debug=True, use_reloader=False)
