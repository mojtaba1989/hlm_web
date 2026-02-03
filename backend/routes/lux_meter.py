from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import time
import json

from nodes.core import logger_ as logger
from nodes.core import core_ as core
from nodes.core import config_ as config
from nodes.lux_ import lux_streamer
from nodes.utils import ErrorCodes



sensor_running = False
router = APIRouter()
lux_streamer = lux_streamer(logger=logger, config=config)

def sensor_loop():
    global sensor_running, lux_streamer
    while sensor_running:
        yield f"data: {json.dumps(lux_streamer.get())}\n\n"
        time.sleep(1/core.config.get('DAQ.Streaming_rate'))


@router.get("/stream")
def stream():
    global sensor_running
    if not config.get('DAQ.ENABLED'):
        return {"message": "DAQ not enabled"}
    sensor_running = True
    return StreamingResponse(
        sensor_loop(),
        media_type="text/event-stream")

@router.get("/stop")
def stop():
    global sensor_running, lux_streamer
    if not config.get('DAQ.ENABLED'):
        return {"message": "DAQ not enabled"}
    sensor_running = False
    lux_streamer.stop()
    return {"message": "Sensor stopped!"}

@router.get("/is_healthy")
async def is_healthy():
    report = {}
    if 'lux' in core.socket_recorders.keys():
        ret = core.socket_recorders['lux']['recorder'].is_healthy()
        report['lux']  = ErrorCodes.desc(ret)
    else:
        report['lux'] = ErrorCodes.NOT_FOUND._name_
    return {"message": report}