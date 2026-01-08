from fastapi import FastAPI
from contextlib import asynccontextmanager
from exception.exceptions import *

from fastapi.responses import JSONResponse
from controller.schedule_routers import router as schedule_router

def start():
    print("started service.")

def shutdown():
    print("end service.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    start()
    yield
    shutdown()

app = FastAPI(lifespan = lifespan)

@app.exception_handler(EndStartReversedException)
async def invalid_end_start(_, e):
    return JSONResponse(status_code = 400, content = {"detail": str(e)})

@app.exception_handler(ScheduleNotFoundException)
async def invalid_schedule(_, e):
    return JSONResponse(status_code = 400, content = {"detail": str(e)})

# router
app.include_router(schedule_router)