import subprocess
import re

def connect(dev, ssid, password, ip):
    if dev.startswith("wlan"):
        try:
            subprocess.run(["sudo", "nmcli", "connection", "delete", ssid], 
                        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": e.stderr.strip()}
        try:
            result = subprocess.run(
                ["sudo", "nmcli", "dev", "wifi", "connect", ssid, "password", password, "ifname", dev],
                capture_output=True,
                text=True,
                check=True
            )
            return {"status": "success", "message": result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": e.stderr.strip()}
    
    if dev.startswith("eth"):
        connection_name = f"{dev}_wired_conncetion"
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "NAME", "connection", "show"],
                capture_output=True,
                text=True,
                check=True)
            if any([connection_name in f for f in result.stdout.strip().split('\n')]):
                result = subprocess.run(["sudo", "nmcli", "dev", "connect", dev], 
                    capture_output=True,
                    text=True,
                    check=True)
                return {"status": "success", "message": result.stdout.strip()}
            else:
                ip = ip if ip else f'192.168.1.1{dev[-1]}'
                result = subprocess.run(["sudo", "nmcli", "connection",
                    "add", "ifname", dev,
                    "type", "ethernet",
                    "con-name", connection_name,
                    "ipv4.method", "manual",
                    "ipv4.addresses", f"{ip}/24"], 
                    capture_output=True,
                    text=True,
                    check=True)
                result = subprocess.run(["sudo", "nmcli", "dev", "connect", dev], 
                    capture_output=True,
                    text=True,
                    check=True)
                return {"status": "success", "message": result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": e.stderr.strip()}

def disconnect(dev):
    try:
        result = subprocess.run(
            ["sudo", "nmcli", "dev", "disconnect", dev],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "success", "message": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}
    

def change_ip(connection_name, ip, dhcp):
    if dhcp:
        try:
            result = subprocess.run(
                ["nmcli", "connection", "modify", connection_name, "ipv4.method", "auto"],
                capture_output=True,
                text=True,
                check=True
            )
            return {"status": "success", "message": result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": e.stderr.strip()}
    ip = ip if ip.endswith("/24") else f"{ip}/24"
    try:
        result = subprocess.run(
            ["sudo", "nmcli", "connection", "modify", connection_name, "ipv4.addresses", ip],
            capture_output=True,
            text=True,
            check=True
        )
        result = subprocess.run(
            ["sudo", "nmcli", "connection", "up", connection_name],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "success", "message": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}

def device_status(dev):
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,STATE,CONNECTION", "dev"],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.strip().split('\n'):
            if line.startswith(dev):
                state = line.split(":")[1]
                connection = line.split(":")[2]
                return {"status": "success",
                        "device_state": state,
                        "connection": connection,
                        "ip_address": get_ip_address(dev).get("ip_address", "")}
        return {"status": "error", "message": f"Device {dev} not found"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}
def list_wifi_networks_nmcli():
    try:
        command = ["nmcli", "-t", "-f", "ssid", "dev", "wifi", "list"]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        ssids = set()
        for line in output.strip().split('\n'):
            if line:
                ssids.add(line.strip())
        
        return {"status": "success", "ssids": sorted(ssids)}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.output.strip()}


def list_devices_nmcli():
    try:
        command = ["nmcli", "-t", "-f", "DEVICE", "dev"]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        devices = []
        for line in output.strip().split('\n'):
            if line and any([line.startswith(type) for type in ["eth", "wlan"]]):
                devices.append(line.strip())
        
        return {"status": "success", "devices": devices}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.output.strip()}
    
def get_ip_address(dev):
    try:
        command = ["nmcli", "-g", "ip4.address", "device", "show", dev]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        return {"status": "success", "ip_address": output.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.output.strip()}
    
def get_route():
    try:
        who_output = subprocess.check_output(['who']).decode().strip()
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}
    client_ip_pattern = re.compile(r'\(([^)]+)\)')
    client_ip = client_ip_pattern.search(who_output).group(1)
    if not client_ip:
        return {"status": "error", "message": "IP address not found"}
    try:
        routes = subprocess.check_output(['ip', 'route', 'get', client_ip]).decode().strip()
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}
    host_pattern = re.compile(r'dev\s+(\S+)\s+src\s+(\S+)')
    dev = host_pattern.search(routes).group(1)
    host = host_pattern.search(routes).group(2)
    return {"status": "success", "dev": dev, "host_ip": host, "client_ip": client_ip}