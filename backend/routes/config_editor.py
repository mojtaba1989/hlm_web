from fastapi import APIRouter
from typing import Dict
import json

from nodes.core import core_ as core

router = APIRouter()

@router.get("/default")
def get_default_config():
    core.config.load()
    return core.config.configs

@router.get("/config")
def get_config():
    return core.config.configs

@router.post("/config")
def save_config(cfg: Dict):
    core.config.save(cfg)
    return {"status": "ok"}

@router.post("/check_unsaved")
def check_unsaved(cfg: Dict):
    return {"unsaved": cfg != core.config.configs}

@router.get("/wifi_ssids")
def get_wifi_ssids():
    return core.config.get_wifi_ssids()

@router.post("/connect_wifi")
def connect_wifi(ssid: str, password: str):
    return core.config.connect_wifi(ssid, password)