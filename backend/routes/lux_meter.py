from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import time
import json
import random

from nodes.core import core_ as core
from nodes.constants import SPS_INVERSE

router = APIRouter()

def save_sensor_row(row):
    if core.writer:
        core.writer.writerow(row)

def number_generator():
    while True:
        yield f"data: {random.random()}\n\n"
        time.sleep(SPS_INVERSE)

def sensor_loop():
    while True:
        ts = time.time()
        frame_id, _ = core.video_recorder.get()
        data = {
            "ts": ts,
            "frame_id": frame_id,
            "s1": random.random()+0,
            "s2": random.random()+1,
            "s3": random.random()+2,
            "s4": random.random()+3,
        }
        if core.recording:
            save_sensor_row(data)
        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(SPS_INVERSE)

@router.get("/stream")
def stream():
    return StreamingResponse(
        sensor_loop(),
        media_type="text/event-stream")