import threading
import signal
import subprocess
import zmq
import struct
import time
import cv2
import os

CAMERA_TCP_STREAM = False

class video_recorder:
    def __init__(self, logger=None):
        self.set_logger(logger)
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
        self.set_camera('/dev/video0')

    def set_logger(self, logger):
        def _noop(*args, **kwargs):
            pass
        base = getattr(logger, "logger", None)
        self.info = getattr(base, "info", _noop)
        self.warning = getattr(base, "warning", _noop)
        self.error = getattr(base, "error", _noop)

    def set_camera(self, camera_device: str=None):
        self.camera_device = camera_device
        self.is_healthy = self.check_camera()

    def set_file_name(self, file_name):
        self.file_name = file_name

    def check_camera(self):
        cam = self.camera_device
        cap = cv2.VideoCapture(cam, cv2.CAP_V4L2)
        time.sleep(.1)
        check = cap.isOpened()
        cap.release()
        del cap
        return check

    def init_socket(self):
        if not CAMERA_TCP_STREAM:
            self.warning("TCP-Camera socket not enabled")
            return
        self.info("Initializing TCP-Camera socket")
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5556")
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
        self.info("Initializing video recorder")
        if self.recording:
            self.warning("Video recorder already started")
            return
        if not self.file_name:
            self.error("Video recorder file name not set")
            return
        avi_file = self.file_name.replace(".mp4", ".avi")
        if CAMERA_TCP_STREAM:
            self.recording = True
            self.init_socket()
            self.rec_thread.start()
        if self.camera_device:
            self.proc = subprocess.Popen([self.node, avi_file, self.camera_device])
        else:
            self.proc = subprocess.Popen([self.node, avi_file])
        time.sleep(.5)
        if self.proc.poll() is not None:
            self.error("Video recorder failed to start")
            return
        self.info("Video recorder started")
    
    def stop(self):
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
            real_cams.append((dev_path, name))
        cap.release()

    return real_cams