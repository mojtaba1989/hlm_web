from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import time
import json
import random

from nodes.core import logger_ as logger
from nodes.lux_ import lux_recorder


sensor_running = False
router = APIRouter()
lux_streamer = lux_recorder(logger=logger)

def sensor_loop():
    global sensor_running, lux_streamer
    logger.logger.info("DAQ Stream: DAQ Node initialized in stream mode")
    while sensor_running:
        yield f"data: {json.dumps(lux_streamer.get())}\n\n"
        time.sleep(1)


@router.get("/stream")
def stream():
    global sensor_running
    sensor_running = True
    logger.logger.info("DAQ Stream: daq stream started")
    return StreamingResponse(
        sensor_loop(),
        media_type="text/event-stream")

@router.get("/stop")
def stop():
    global sensor_running, lux_streamer
    sensor_running = False
    lux_streamer.stop()
    logger.logger.info("DAQ Stream: daq stream stopped")
    return {"message": "Sensor stopped!"}