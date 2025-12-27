from fastapi import APIRouter
import utils
import cv2, csv

router = APIRouter()

@router.post("/start")
def start_record():
    utils.core_.logger.logger.info("Initializing recording")
    if not utils.core_.init_recording():
        utils.core_.logger.logger.error("Error initializing recording")
        return {"status": "Error initializing recording"}
    utils.core_.recording = True
    utils.core_.logger.logger.info("Start recording")
    return {"status": "recording started"}

@router.post("/stop")
def stop_record():
    utils.core_.close_recording()
    utils.core_.logger.logger.info("Stop recording")
    return {"status": "recording stopped"}