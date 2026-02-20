from functools import wraps
import inspect
import os
import threading
import socket
import struct
import time
import os
from enum import IntEnum
import subprocess

class ErrorCodes(IntEnum):
    SUCCESS = 0
    ADDRESS_ALREADY_IN_USE = 1
    RECEVEIVED_INVALID_DATA = 2
    TIMEOUT = 3
    NOT_FOUND = 4
    UNKNOWN_ERROR = 5

    def desc(error_code):
        return ErrorCodes(error_code).name
    
class CameraErrorCodes(IntEnum):
    SUCCESS = 0
    CAMERA_DISABLED = 1
    CAMERA_NOT_FOUND = 2
    CAMERA_NOT_WORKING = 3
    UNKNOWN_ERROR = 4

    def desc(error_code):
        return CameraErrorCodes(error_code).name

def try_except(func):
    @wraps(func)
    def wrapper(*args, default=None, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = None
            if args and hasattr(args[0], "logger"):
                logger = args[0].logger
            if logger:
                logger.logger.error(
                    f"Exception in {func.__qualname__}: {e}"
                )
            return default
    return wrapper

def safe_call(method, *args, label=None, default=None, **kwargs):
    try:
        return method(*args, **kwargs)
    except Exception:
        self = getattr(method, "__self__", None)

        logger = (
            getattr(self, "logger", None)
            if self is not None
            else None
        ) or None
        if logger is None:
            return default
        
        frame = inspect.currentframe().f_back
        caller_func = frame.f_code.co_name
        caller_file = frame.f_code.co_filename
        caller_line = frame.f_lineno

        cmd_name = label or getattr(method, "__qualname__", repr(method))

        logger.logger.error(
            "Step failed: %s | called from %s (%s:%d)",
            cmd_name,
            caller_func,
            caller_file,
            caller_line
        )

        return default

def get_size(file_name):
    s = os.path.getsize(file_name)
    ord = 0
    while int(s / 1024) > 1:
        s /= 1024
        ord += 1
    return f"{s:.2f} {['B', 'KB', 'MB', 'GB', 'TB'][ord]}"

class failed_loop_ctrl:
    def __init__(self, max_failed=None):
        if isinstance(max_failed, int) and max_failed > 0:
            self.max_failed = max_failed 
        else:
            self.max_failed = -1
        self.reset()

    def is_failed(self):
        return self.max_failed != -1 and self.failed_to_get >= self.max_failed
    
    def reset(self):
        self.failed_to_get = 0

    def increment(self):
        self.failed_to_get += 1

class socket_recorder:
    def __init__(
            self,
            host,
            port,
            name,
            logger=None,
            max_failed=-1,
            packet_size=-1,
        ):
        self.set_logger(logger)
        self.name = name
        self.host = host.split("/")[0]
        self.port = port
        self.socket = None
        self.file_name = None
        self.running = False
        self.packet_size = packet_size
        self.flc = failed_loop_ctrl(max_failed=max_failed)
        self.thread = None

    def is_duplicate(self, obj_dict: dict):
        for key in obj_dict.keys():
            obj = obj_dict[key]['recorder']
            if obj.host == self.host and obj.port == self.port:
                return True
        return False
    
    def set_file_name(self, file_name):
        self.file_name = file_name.replace(file_name.split(".")[-1], "bin")

    def is_healthy(self):
        if self.socket:
            return ErrorCodes.ADDRESS_ALREADY_IN_USE
        socket_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_temp.bind((self.host, self.port))
        socket_temp.settimeout(1)
        try:
            msg, addr = socket_temp.recvfrom(1024)
        except socket.timeout:
            socket_temp.close()
            return ErrorCodes.TIMEOUT
        if len(msg) == self.packet_size:
            socket_temp.close()
            return ErrorCodes.SUCCESS
        socket_temp.close()
        return ErrorCodes.RECEVEIVED_INVALID_DATA

    def set_logger(self, logger):
        def _noop(*args, **kwargs):
            pass
        base = getattr(logger, "logger", None)
        self.info = getattr(base, "info", _noop)
        self.warning = getattr(base, "warning", _noop)
        self.error = getattr(base, "error", _noop)

    @try_except
    def init_socket(self, timeout=1):
        self.info(f"Initializing {self.name} socket")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(timeout)
        self.info(f"{self.name} socket initialized at {self.host}:{self.port}")
        return True

    def loop(self):
        if not self.file_name:
            self.error(f"File name not set for {self.name} recorder")
            return
        if not self.socket:
            self.error(f"Socket not initialized for {self.name} recorder")
            return
        with open(self.file_name, "wb") as f:
            while self.running:
                try:
                    msg, addr = self.socket.recvfrom(65535)
                except socket.timeout:
                    if self.flc.is_failed():
                        self.error(f"{self.name}: Maximum attempts reached - Closing socket")
                        return
                    self.flc.increment()
                    self.warning(f"{self.name}: Attempt - Failed to get data")
                    continue
                if self.packet_size !=-1 and len(msg) != self.size:
                    continue
                header = struct.pack("<QI", time.time_ns(), len(msg))
                f.write(header)
                f.write(msg)
                self.failed_to_get = 0

    def start(self):
        self.running = True
        if not self.init_socket():
            self.error(f"Failed to initialize {self.name}-{(self.host, self.port)} socket")
            return
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        self.info(f"{self.name} recorder initialized")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None
        if self.socket:
            self.socket.close()
            self.socket = None
        self.info(f"{self.name} recorder stopped")