from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import utils
import time
import json
import random

router = APIRouter()

def save_sensor_row(row):
    if utils.core_.writer:
        utils.core_.writer.writerow(row)

def number_generator():
    while True:
        yield f"data: {random.random()}\n\n"
        time.sleep(utils.SPS_INVERSE)

def sensor_loop():
    while True:
        ts = time.time()
        with utils.lock:
            frame_id = utils.latest_frame['frame_id']

        data = {
            "ts": ts,
            "frame_id": frame_id,
            "s1": random.random()+0,
            "s2": random.random()+1,
            "s3": random.random()+2,
            "s4": random.random()+3,
        }
        if utils.core_.recording:
            save_sensor_row(data)
        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(utils.SPS_INVERSE)

@router.get("/stream")
def stream():
    return StreamingResponse(
        sensor_loop(),
        media_type="text/event-stream")