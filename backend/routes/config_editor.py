from fastapi import APIRouter
from typing import Dict
import json
import time

from nodes.core import core_ as core
from nodes.network_manager_ import *

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

@router.get("/network_devices")
def get_wifi_devices():
    time.sleep(.1)
    return list_devices_nmcli()

@router.post("/connect")
def connect_(request: Dict):
    ssid = request.get("ssid")
    password = request.get("password")
    dev = request.get("dev")
    ip = request.get("ip")
    return connect(dev, ssid, password, ip)

@router.post("/disconnect")
def disconnect_(request: Dict):
    dev = request.get("dev")
    return disconnect(dev)

@router.post("/change_ip")
def change_ip_(request: Dict):
    dev = request.get("dev")
    ip = request.get("ip")
    dhcp = request.get("dhcp")
    return change_ip(dev, ip, dhcp)

@router.post("/device_status")
def device_status_(request: Dict):
    dev = request.get("dev")
    return device_status(dev)

@router.get("/route")
def get_route_():
    return get_route()

@router.get("/test_catalog")
def get_test_catalog():
    with open(TEST_CATALOG_PATH, "r") as f:
        catalog = json.load(f)
    catalog = catalog.get("scenario_configs", {})
    listed_catalog = [catalog[key]['description'] for key in catalog.keys()]
    return {"scenarios": (listed_catalog)}

@router.post("/set_scenario")
def set_scenario_(request: Dict):
    scenario = request.get("scenario")
    if scenario:
        core.current_scenario = str(int(scenario)+1)
    else:
        core.current_scenario = 'unknown'
    return {"status": "ok", "scenario": scenario}

@router.post("/postprocess_toggle")
def postprocess_toggle(request: Dict):
    enabled = request.get("enabled")
    core.postprocess_enabled = enabled
    return {"status": "ok", "enabled": core.postprocess_enabled}