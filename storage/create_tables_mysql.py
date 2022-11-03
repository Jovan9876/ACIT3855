import yaml
import mysql.connector


with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())


def create_tables():
    db_conn = mysql.connector.connect(
        host=app_config["mysql"]["hostname"],
        user=app_config["mysql"]["user"],
        password=app_config["mysql"]["password"],
        database=app_config["mysql"]["db"],
    )

    db_cursor = db_conn.cursor()


    db_cursor.execute(
            """
            CREATE TABLE step
            (id INT NOT NULL AUTO_INCREMENT, 
            user_id INTEGER NOT NULL,
            num_steps INTEGER NOT NULL,
            total_distance INTEGER NOT NULL,
            elevation INTEGER NOT NULL,
            floors_climbed INTEGER NOT NULL,
            trace_id VARCHAR(100) NOT NULL,
            timestamp VARCHAR(100) NOT NULL,
            date_created VARCHAR(100) NOT NULL,
            CONSTRAINT trace_id_UNIQUE UNIQUE (`trace_id`),
            CONSTRAINT user_id_pk PRIMARY KEY (id))
            """
    )


    db_cursor.execute(
            """
            CREATE TABLE weight
            (id INT NOT NULL AUTO_INCREMENT, 
            user_id INTEGER NOT NULL,
            calories_burned INTEGER NOT NULL,
            weight_lost INTEGER NOT NULL,
            new_weight INTEGER NOT NULL,
            fitness_score INTEGER NOT NULL,
            trace_id VARCHAR(100) NOT NULL,
            timestamp VARCHAR(100) NOT NULL,
            date_created VARCHAR(100) NOT NULL,
            CONSTRAINT trace_id_UNIQUE UNIQUE (`trace_id`),
            CONSTRAINT user_id_pk PRIMARY KEY (id))
            """
    )



    db_conn.commit()
    db_conn.close()
