from fastapi import APIRouter
from typing import Dict

router = APIRouter()

CONFIG = {}  # in-memory or loaded from file

@router.get("/config")
def get_config():
    return CONFIG

@router.post("/config")
def save_config(cfg: Dict):
    global CONFIG
    CONFIG = cfg
    
    return {"status": "ok"}
