import threading
import signal
import subprocess
import zmq
import struct

class video_recorder:
    def __init__(self):
        self.proc = None
        self.node = "/home/dev/hlm_web/backend/nodes/rec"
        self.frame_id = -1
        self.frame_unix_time = -1
        self.recording = False
        self.lock = threading.Lock()
        self.rec_thread = None
        self.socket = None
        self.file_name = None
        self.format = '<IQ'
        self.size = struct.calcsize(self.format)

    def init_socket(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5556")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.rec_thread = threading.Thread(target=self.loop_, daemon=True)  
        
    def loop_(self):
        while self.recording:
            msg = self.socket.recv()
            if len(msg) != self.size:
                continue
            with self.lock:
                self.frame_id, self.frame_unix_time = struct.unpack(self.format, msg)

    def start(self):
        if self.recording:
            return
        if not self.file_name:
            return
        avi_file = self.file_name.replace(".mp4", ".avi")
        self.recording = True
        self.init_socket()
        self.rec_thread.start()
        self.proc = subprocess.Popen([self.node, avi_file])
    
    def stop(self):
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
    
    def get(self):
        with self.lock:
            return self.frame_id, self.frame_unix_time

    def convert_to_mp4(self):
        if not self.file_name:
            return
        avi_file = self.file_name.replace(".mp4", ".avi")
        print("Converting to MP4...")

        cmd = [
            "ffmpeg", "-y",
            "-i", avi_file,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            self.file_name
        ]

        subprocess.run(cmd, check=True)