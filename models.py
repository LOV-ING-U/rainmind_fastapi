from sqlalchemy import Column, Integer, String, DateTime
from db import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key = True, index = True, nullable = True)
    title = Column(String, nullable = False)
    location = Column(String, nullable = False)
    startAt = Column(DateTime, nullable = False)
    endAt = Column(DateTime, nullable = False)