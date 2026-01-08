from fastapi import APIRouter, HTTPException, Depends
from dto.dtos import *
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session

from service.schedule_service import *

router = APIRouter(prefix = "/schedules", tags = ["schedules"])

@router.post("", response_model = ScheduleCreateResponse, status_code = 201)
async def create_schedule(body: ScheduleCreateRequest, session: AsyncSession = Depends(get_session)):
    schedule_id = await createSchedule(session, **body.dict())
    return ScheduleCreateResponse(scheduleId = schedule_id)

@router.delete("/{schedule_id}", response_model = ScheduleDeleteResponse, status_code = 200)
async def delete_schedule(schedule_id: int, session: AsyncSession = Depends(get_session)):
    await deleteSchedule(session, schedule_id)
    return ScheduleDeleteResponse(deletedScheduleId = schedule_id)