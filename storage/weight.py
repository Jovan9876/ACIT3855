from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Weight(Base):
    """Weight Class"""

    __tablename__ = "weight"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    calories_burned = Column(Integer, nullable=False)
    weight_lost = Column(Integer, nullable=False)
    new_weight = Column(Integer, nullable=False)
    fitness_score = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    timestamp = Column(String(100), nullable=False)
    trace_id = Column(String(100), nullable=False)

    def __init__(
        self,
        user_id,
        calories_burned,
        weight_lost,
        new_weight,
        fitness_score,
        timestamp,
        trace_id,
    ):
        """Initializes weight information"""
        self.user_id = user_id
        self.calories_burned = calories_burned
        self.weight_lost = weight_lost
        self.new_weight = new_weight
        self.fitness_score = fitness_score
        self.date_created = datetime.datetime.now()
        self.timestamp = timestamp
        self.trace_id = trace_id

    def to_dict(self):
        """Dictionary Representation of weight information"""
        dict = {}
        dict["id"] = self.id
        dict["userID"] = self.user_id
        dict["caloriesBurned"] = self.calories_burned
        dict["weightLost"] = self.weight_lost
        dict["newWeight"] = self.new_weight
        dict["fitnessScore"] = self.fitness_score
        dict["date_created"] = self.date_created
        dict["timestamp"] = self.timestamp
        dict["traceID"] = self.trace_id

        return dict
