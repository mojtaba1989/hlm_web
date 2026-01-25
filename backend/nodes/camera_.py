import threading
import signal
import subprocess
import zmq
import struct

CAMERA_TCP_STREAM = False

class video_recorder:
    def __init__(self, logger=None):
        self.logger = logger
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
        self.logger.logger.info("[NODE-INFO] Video recorder node initialized")

    def init_socket(self):
        if not CAMERA_TCP_STREAM:
            self.logger.logger.warning("TCP-Camera socket not enabled")
            return
        self.logger.logger.info("Initializing TCP-Camera socket")
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5556")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.rec_thread = threading.Thread(target=self.loop_, daemon=True)
        self.logger.logger.info("TCP-Camera socket initialized")
        
    def loop_(self):
        while self.recording:
            msg = self.socket.recv()
            if len(msg) != self.size:
                continue
            with self.lock:
                self.frame_id, self.frame_unix_time = struct.unpack(self.format, msg)

    def start(self):
        self.logger.logger.info("Initializing video recorder")
        if self.recording:
            self.logger.logger.warning("Video recorder already started")
            return
        if not self.file_name:
            self.logger.logger.error("Video recorder file name not set")
            return
        avi_file = self.file_name.replace(".mp4", ".avi")
        if CAMERA_TCP_STREAM:
            self.recording = True
            self.init_socket()
            self.rec_thread.start()
        self.proc = subprocess.Popen([self.node, avi_file])
        self.logger.logger.info("Video recorder started")
    
    def stop(self):
        self.logger.logger.info("Stopping video recorder")
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
        self.logger.logger.info("Video recorder stopped")
    
    def get(self):
        with self.lock:
            return self.frame_id, self.frame_unix_time

    def convert_to_mp4(self):
        self.logger.logger.info("AVI -> MP4: Converting to MP4...")
        if not self.file_name:
            self.logger.logger.error("AVI -> MP4: Video recorder file name not set")
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
        self.logger.logger.info("AVI -> MP4: Conversion complete")