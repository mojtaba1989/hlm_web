from fastapi import APIRouter
from nodes.core import core_ as core

router = APIRouter()

@router.get("/start")
def start_record():
    if not core.init_recording():
        core.logger.logger.error("Error initializing recording")
        return {"status": "Error initializing recording"}
    core.recording = True
    core.logger.logger.info("Recording started")
    return {"status": "recording started"}

@router.get("/stop")
def stop_record():
    core.close_recording()
    core.logger.logger.info("Recording stopped")
    return {"status": "recording stopped"}

