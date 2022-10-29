import sqlite3


conn = sqlite3.connect('stats.sqlite')
c = conn.cursor()

c.execute('''
CREATE TABLE stats
(id INTEGER PRIMARY KEY ASC,
num_step_readings INTEGER NOT NULL,
avg_num_steps INTEGER NOT NULL,
avg_floors_climbed INTEGER NOT NULL,
avg_elevation INTEGER NOT NULL,
max_distance INTEGER NOT NULL,
num_weight_readings INTEGER NOT NULL,
avg_weight_lost INTEGER NOT NULL,
avg_calories_burned INTEGER NOT NULL,
max_weight_lost INTEGER NOT NULL,
last_updated VARCHAR(100) NOT NULL)
''')


conn.commit()
conn.close()