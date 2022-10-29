import yaml
import mysql.connector


with open("app_conf.yml", "r") as f:
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
