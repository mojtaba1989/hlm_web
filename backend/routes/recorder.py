from fastapi import APIRouter
from nodes.core import core_ as core
from nodes.logger_ import logger_ as logger

router = APIRouter()

@router.get("/start")
def start_record():
    if not core.init_recording():
        logger.logger.error("Error initializing recording")
        return {"status": "Error initializing recording"}
    core.recording = True
    logger.logger.info("Recording started")
    return {"status": "recording started"}

@router.get("/stop")
def stop_record():
    core.close_recording()
    logger.logger.info("Recording stopped")
    return {"status": "recording stopped"}

