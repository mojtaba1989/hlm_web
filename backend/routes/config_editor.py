from fastapi import APIRouter
from typing import Dict
import json
import time

from nodes.core import core_ as core
from nodes.wifi_ import *

router = APIRouter()
TEST_CATALOG_PATH = "/home/dev/hlm_web/backend/.configs/test_catalog.json"

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
    time.sleep(.1)
    return list_wifi_networks_nmcli()

@router.get("/wifi_devices")
def get_wifi_devices():
    time.sleep(.1)
    return list_wifi_devices_nmcli()

@router.post("/connect_wifi")
def wifi_connect_(request: Dict):
    ssid = request.get("ssid")
    password = request.get("password")
    dev = request.get("dev")
    return wifi_connect(ssid, password, dev)

@router.post("/disconnect_wifi")
def wifi_disconnect_(request: Dict):
    dev = request.get("dev")
    return wifi_disconnect(dev)

@router.post("/wifi_status")
def wifi_status_(request: Dict):
    dev = request.get("dev")
    return wifi_status(dev)

@router.post("/wifi_on")
def wifi_on():
    return radio_on()

@router.post("/wifi_off")
def wifi_off():
    return radio_off()

@router.post("/wifi_ip")
def get_wifi_ip(request: Dict):
    dev = request.get("dev")
    return get_ip_address(dev)

@router.get("/test_catalog")
def get_test_catalog():
    with open(TEST_CATALOG_PATH, "r") as f:
        catalog = json.load(f)
    catalog = catalog.get("scenario_configs", {})
    listed_catalog = [catalog[key]['description'] for key in catalog.keys()]
    return {"scenarios": sorted(listed_catalog)}