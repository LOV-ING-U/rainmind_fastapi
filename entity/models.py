from sqlalchemy import Column, Integer, String, DateTime
from db import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    location = Column(String, nullable = False)
    startAt = Column(DateTime, nullable = False)
    endAt = Column(DateTime, nullable = False)

class Outbox(Base):
    __tablename__ = "alarm_outbox"

    id = Column(Integer, primary_key = True, index = True)
    scheduleId = Column(Integer, nullable = False)
    payload = Column(String, nullable = False)
    status = Column(String, nullable = False)
    createdAt = Column(DateTime, nullable = False)
    alarmAt = Column(DateTime, nullable = False)