import datetime
import json
import logging
import logging.config
import uuid

import connexion
import requests
import yaml
from connexion import NoContent
from pykafka import KafkaClient

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")


def addStepInfo(body):
    """Recieves step count information"""
    trace_id = str(uuid.uuid4())
    
    logger.info(f"Received event addStepInfo request with a trace id of {trace_id}")

    body["traceID"] = trace_id
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = { "type": "addStepInfo", "datetime" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(
        f"Returned event addStepInfo response (Id: {trace_id}) with status 201"
    )

    return NoContent, 201


def addWeightInfo(body):
    """Recieves weight information"""
    trace_id = str(uuid.uuid4())

    logger.info(f"Received event addWeightInfo request with a trace id of {trace_id}")

    body["traceID"] = trace_id
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = { "type": "addWeightInfo", "datetime" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(
        f"Returned event addWeightInfo response (Id: {trace_id}) with status 201"
    )

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080, debug=True)
