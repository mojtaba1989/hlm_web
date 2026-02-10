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
    def __init__(self, logger=None, config=None):
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
        self.file_name = file_name

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
        
        # Check if video recorder is already running
        self.info("Initializing video recorder")
        if self.recording:
            self.warning("Video recorder already started")
            return
        
        # Check if file name is set
        if not self.file_name:
            self.error("Video recorder file name not set")
            return
        
        avi_file = self.file_name.replace(".mp4", ".avi")
        self.recording = True
        # Check if TCP-Camera socket is enabled
        if self.config.get('camera.tcp_stream'):
            self.init_socket()
            self.rec_thread.start()

        self.proc = subprocess.Popen([self.node, avi_file, self.camera_device])
        time.sleep(.5)

        # Check if video recorder started successfully
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

    def convert_to_mp4(self):
        self.info("AVI -> MP4: Converting to MP4...")
        if not self.file_name:
            self.error("AVI -> MP4: Video recorder file name not set")
            return
        avi_file = self.file_name.replace(".mp4", ".avi")
        if not os.path.exists(avi_file):
            self.error("AVI -> MP4: Video recorder file not found")
            return
        cmd = [
            "ffmpeg", "-y",
            "-i", avi_file,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            self.file_name
        ]
        subprocess.run(cmd, check=True)
        self.info("AVI -> MP4: Conversion complete")

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

        # Skip virtual / encoder devices
        if "pispbe" in name or "rpi" in name:
            continue

        # Optional: check if OpenCV can open it
        cap = cv2.VideoCapture(dev_path, cv2.CAP_V4L2)
        if cap.isOpened():
            real_cams.append({"id": f"usb_{name}", "path": dev_path, "name": name})
        cap.release()

    return real_cams