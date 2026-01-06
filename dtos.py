from pydantic import BaseModel
from datetime import datetime

class ScheduleCreateRequest(BaseModel):
    title: str
    location: str
    startAt: datetime
    endAt: datetime

class ScheduleCreateResponse(BaseModel):
    scheduleId: int

class ScheduleDeleteResponse(BaseModel):
    deletedScheduleId: int

class ScheduleAlarmOut(BaseModel):
    id: int
    title: str
    location: str
    startAt: datetime
    endAt: datetime