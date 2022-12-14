import datetime
import json
import logging
import logging.config
import os
import time
import uuid

import connexion
import requests
import yaml
from connexion import NoContent
from pykafka import KafkaClient

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

current_tries = 0
max_retries = app_config["connection"]["retries"]
while current_tries < max_retries:
    logger.info(f"Trying to connect to Kafka ATTEMPT {current_tries}")
    try:
        client = KafkaClient(
            hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}"
        )
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        break
    except:
        current_tries += 1
        logger.error(f"Connection to Kafka failed ATTEMPT {current_tries}")
        time.sleep(app_config["scheduler"]["sleep"])
        # continue


def addStepInfo(body):
    """Recieves step count information"""
    trace_id = str(uuid.uuid4())

    logger.info(f"Received event addStepInfo request with a trace id of {trace_id}")

    body["traceID"] = trace_id

    producer = topic.get_sync_producer()
    msg = {
        "type": "addStepInfo",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        "payload": body,
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(f"Returned event addStepInfo response (Id: {trace_id}) with status 201")

    return NoContent, 201


def addWeightInfo(body):
    """Recieves weight information"""
    trace_id = str(uuid.uuid4())

    logger.info(f"Received event addWeightInfo request with a trace id of {trace_id}")

    body["traceID"] = trace_id

    producer = topic.get_sync_producer()
    msg = {
        "type": "addWeightInfo",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        "payload": body,
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(
        f"Returned event addWeightInfo response (Id: {trace_id}) with status 201"
    )

    return NoContent, 201


def getHealth():
    """Returns the health of the system"""
    return {"reciever": "running"}, 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml",base_path="/reciever", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)
