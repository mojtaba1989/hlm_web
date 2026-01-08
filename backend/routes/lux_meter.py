from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import utils
import time
import json
import random
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

router = APIRouter()
I2C = busio.I2C(board.SCL, board.SDA)
x48

DFR0553 = {
    'x48A0': [0x48, 0],
    'x48A1': [0x48, 1],
    'x48A2': [0x48, 2],
    'x48A3': [0x48, 3],
    'x49A0': [0x49, 0],
    'x49A1': [0x49, 1],
    'x49A2': [0x49, 2],
    'x49A3': [0x49, 3]
}

GAINS = [2/3, 1, 2, 4, 8, 16]
DATA_RATE = [8, 16, 32, 64, 128, 250, 475, 860]




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
        frame_id, _ = utils.core_.counter.get()
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