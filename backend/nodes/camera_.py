import threading
import signal
import subprocess
import zmq
import struct
import time
import cv2
import os

from nodes.utils import CameraErrorCodes

class video_recorder:
    def __init__(self, logger=None, config=None,):
        self.set_logger(logger)
        self.config = config
        self.proc = None
        self.node = "/home/dev/hlm_web/backend/nodes/build/rec"
        self.frame_id = -1
        self.frame_unix_time = -1
        self.recording = False
        self.lock = threading.Lock()
        self.rec_thread = None
        self.socket = None
        self.file_name = None
        self.format = '<IQ'
        self.size = struct.calcsize(self.format)
        self.info("[NODE-INFO] Video recorder node initialized")
        self.camera_device = None
        self.status = self.get_status()

    def set_logger(self, logger):
        def _noop(*args, **kwargs):
            pass
        base = getattr(logger, "logger", None)
        self.info = getattr(base, "info", _noop)
        self.warning = getattr(base, "warning", _noop)
        self.error = getattr(base, "error", _noop)

    def set_file_name(self, file_name):
        self.file_name = file_name.replace(file_name.split(".")[-1], "avi")

    def get_status(self):
        if not self.config.get('CAMERA.ENABLED'):
            return CameraErrorCodes.CAMERA_DISABLED
        self.camera_device = None if self.config.get('CAMERA.Device_ID') == "" else self.config.get('CAMERA.Device_ID')
        if self.camera_device is None:
            return CameraErrorCodes.CAMERA_NOT_FOUND
        if not self.check_camera():
            return CameraErrorCodes.CAMERA_NOT_WORKING
        return CameraErrorCodes.SUCCESS

    def check_camera(self):
        if not self.camera_device:
            return False
        cam = self.camera_device
        cap = cv2.VideoCapture(cam, cv2.CAP_V4L2)
        time.sleep(.1)
        check = cap.isOpened()
        cap.release()
        del cap
        return check

    def init_socket(self):
        # TODO: socket recoreder is permanently disabled
        return
        if not self.config.get('camera.tcp_stream'):
            self.warning("TCP-Camera socket not enabled")
            return
        self.info("Initializing TCP-Camera socket")
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{self.config.get('camera.tcp_ip')}:{self.config.get('camera.tcp_port')}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.rec_thread = threading.Thread(target=self.loop_, daemon=True)
        self.info("TCP-Camera socket initialized")
        
    def loop_(self):
        while self.recording:
            msg = self.socket.recv()
            if len(msg) != self.size:
                continue
            with self.lock:
                self.frame_id, self.frame_unix_time = struct.unpack(self.format, msg)

    def start(self):
        self.status = self.get_status()
        if self.status != CameraErrorCodes.SUCCESS:
            self.error(f"Video recorder failed to start: {self.status.name}")
            return
        
        self.info("Initializing video recorder")
        if self.recording:
            self.warning("Video recorder already started")
            return
        
        if not self.file_name:
            self.error("Video recorder file name not set")
            return
        
        self.recording = True
        if self.config.get('camera.tcp_stream'):
            self.init_socket()
            self.rec_thread.start()

        self.proc = subprocess.Popen([self.node, self.file_name, self.camera_device])
        time.sleep(.5)
        if self.proc.poll() is not None:
            self.error("Video recorder failed to start")
            self.recording = False
            return
        
        self.info("Video recorder started")
    
    def stop(self):
        if self.status != CameraErrorCodes.SUCCESS:
            return
        
        if not self.recording:
            return
        
        self.info("Stopping video recorder")
        self.recording = False
        if self.proc:
            self.proc.send_signal(signal.SIGINT)
            self.proc.wait()
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.rec_thread:
            self.rec_thread.join()
            self.rec_thread = None
        self.frame_id = -1
        self.frame_unix_time = -1
        self.info("Video recorder stopped")
    
    def get(self):
        with self.lock:
            return self.frame_id, self.frame_unix_time

def list_real_cameras(max_devices=64):
    base = "/sys/class/video4linux"
    real_cams = []

    for dev in os.listdir(base):
        dev_path = f"/dev/{dev}"
        name_file = os.path.join(base, dev, "name")
        if not os.path.exists(dev_path) or not os.path.exists(name_file):
            continue

        with open(name_file) as f:
            name = f.read().strip().lower()

        if "pispbe" in name or "rpi" in name:
            continue

        cap = cv2.VideoCapture(dev_path, cv2.CAP_V4L2)
        if cap.isOpened():
            real_cams.append({"id": f"usb_{name}", "path": dev_path, "name": name})
        cap.release()

    return real_cams

def convert_to_mp4(file_name=None, config=None, replace=True):
    # COonfig is not used -> just for compatibility
    avi_file = file_name.replace(".mp4", ".avi")
    if not os.path.exists(avi_file):
        return {"status": "success", "message": "AVI file not found"}
    cmd = [
        "ffmpeg", "-y",
        "-i", avi_file,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        file_name
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if replace and os.path.getsize(file_name) >= 0:
            os.remove(avi_file)
        return {"status": "success", "message": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}
