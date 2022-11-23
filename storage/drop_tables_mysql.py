import yaml
import mysql.connector
import os

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


db_conn = mysql.connector.connect(
    host=app_config["mysql"]["hostname"],
    user=app_config["mysql"]["user"],
    password=app_config["mysql"]["password"],
    database=app_config["mysql"]["db"],
)


db_cursor = db_conn.cursor()
db_cursor.execute(
    """
    DROP TABLE weight, step
    """
)

db_conn.commit()
db_conn.close()
