from sqlalchemy import Column, Integer, String, DateTime
from base import Base

class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    num_step_readings = Column(Integer, nullable=False)
    avg_num_steps = Column(Integer, nullable=False)
    avg_floors_climbed = Column(Integer, nullable=True)
    avg_elevation = Column(Integer, nullable=False)
    max_distance = Column(Integer, nullable=False)
    num_weight_readings = Column(Integer, nullable=False)
    avg_weight_lost = Column(Integer, nullable=False)
    avg_calories_burned = Column(Integer, nullable=False)
    max_weight_lost = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)


    def __init__(self, num_step_readings, avg_num_steps, avg_floors_climbed, avg_elevation, max_distance, num_weight_readings, 
    avg_weight_lost, avg_calories_burned, max_weight_lost, last_updated):
        """ Initializes a processing statistics object """
        self.num_step_readings = num_step_readings
        self.avg_num_steps = avg_num_steps
        self.avg_floors_climbed = avg_floors_climbed
        self.avg_elevation = avg_elevation
        self.max_distance = max_distance
        self.num_weight_readings = num_weight_readings
        self.avg_weight_lost = avg_weight_lost
        self.avg_calories_burned = avg_calories_burned
        self.max_weight_lost = max_weight_lost
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['numStepReadings'] = self.num_step_readings
        dict['avgNumSteps'] = self.avg_num_steps
        dict['avgFloorsClimbed'] = self.avg_floors_climbed
        dict['avgElevation'] = self.avg_elevation
        dict['maxDistance'] = self.max_distance
        dict['numWeightReadings'] = self.num_weight_readings
        dict['avgWeightLost'] = self.avg_weight_lost
        dict['avgCaloriesBurned'] = self.avg_calories_burned
        dict['maxWeightLost'] = self.max_weight_lost
        dict['lastUpdated'] = self.last_updated.strftime("%Y-%m-%d %H:%M:%S.%f")

        return dict