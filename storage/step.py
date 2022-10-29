from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Step(Base):
    """Step Class"""

    __tablename__ = "step"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    num_steps = Column(Integer, nullable=False)
    total_distance = Column(Integer, nullable=False)
    elevation = Column(String(100), nullable=False)
    floors_climbed = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    timestamp = Column(String(100), nullable=False)
    trace_id = Column(String(100), nullable=False)

    def __init__(self, user_id, num_steps, total_distance, elevation, floors_climbed, timestamp, trace_id):
        """Initializes step information"""
        self.user_id = user_id
        self.num_steps = num_steps
        self.total_distance = total_distance
        self.elevation = elevation
        self.floors_climbed = floors_climbed
        self.date_created = datetime.datetime.now()
        self.timestamp = timestamp
        self.trace_id = trace_id

    def to_dict(self):
        """Dictionary Representation of step information"""
        dict = {}
        dict["id"] = self.id
        dict["userID"] = self.user_id
        dict["numSteps"] = self.num_steps
        dict["totalDistance"] = self.total_distance
        dict["elevation"] = self.elevation
        dict["floorsClimbed"] = self.floors_climbed
        dict['date_created'] = self.date_created
        dict["timestamp"] = self.timestamp
        dict["traceID"] = self.trace_id

        return dict
