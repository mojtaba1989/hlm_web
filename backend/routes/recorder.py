from fastapi import APIRouter
from nodes.core import core_ as core

router = APIRouter()

@router.get("/start")
def start_record():
    if not core.init_recording():
        return {"status": "Error initializing recording"}
    core.recording = True
    return {"status": "recording started"}

@router.get("/stop")
def stop_record():
    core.close_recording()
    return {"status": "recording stopped"}

