import datetime
import logging
import logging.config

import connexion
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

# from flask_cors import CORS, cross_origin
import json


with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger("basicLogger")


def checkHealth():
    logger.info("Checking health of services")
    statusObj = {}
    for service in app_config['services']:
        logger.info(f"Checking health of {service}")
        try:
            res = requests.get(f"{app_config['services'][service]}/health", timeout=5)
            if res.status_code == 200:
                statusObj[service] = "Running"
            else:
                statusObj[service] = "Down"
        except requests.exceptions.ConnectionError:
            if service not in statusObj:
                statusObj[service] = "Down"


    statusObj["lastUpdate"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Appending {statusObj} to status.json")
    with open("status.json", "a") as f:
        json.dump(statusObj, f)
    logger.info("Health check complete")

    return statusObj




def initScheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(checkHealth, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()
app = connexion.FlaskApp(__name__, specification_dir='')
# CORS(app.app)
# app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    initScheduler()
    app.run(port=8120, debug=True, use_reloader=False)