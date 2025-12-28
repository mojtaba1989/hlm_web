import itertools
import threading
import datetime
import os, sys
import logging
from functools import wraps
import json
import jsonpatch
from copy import deepcopy
import csv
import cv2
import inspect
import queue

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

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
    
class QueueLogHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        msg = self.format(record)
        self.log_queue.put(msg)

class LoggerManager:
    def __init__(self):
        self.logger = logging.getLogger("headLightMeter")
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        self.handeler_types = {
            "file": logging.FileHandler,
            "queue": QueueLogHandler,
            "console": logging.StreamHandler
        }
        self.setup_console_logger()
        self.setup_weblog_logger()

    def setup_console_logger(self):
        if any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            return
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def setup_file_logger(self, config : dict, file_name : str):
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                self.logger.removeHandler(handler)
                handler.close()
                
        if config.get("LOG", {}).get("ENABLED", True):
            level = config.get("LOG", {}).get("LEVEL", "INFO")
            self.file_handler = logging.FileHandler(file_name)
            self.file_handler.setLevel(LOG_LEVELS.get(level, logging.INFO))
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)

    def setup_weblog_logger(self):
        for handler in self.logger.handlers[:]:
            if isinstance(handler, QueueLogHandler):
                self.logger.removeHandler(handler)
                handler.close()
                
        self.log_queue = queue.Queue()
        self.queue_handler = QueueLogHandler(self.log_queue)
        self.queue_handler.setLevel(logging.INFO)
        self.queue_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.queue_handler)

    def set_level(self, level, target="all"):
        if target == "all": 
            for handler in self.logger.handlers:
                handler.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
            return True 
        else:
            instance = self.handeler_types.get(target, None)
            if instance is not None:
                for handler in self.logger.handlers:
                    if isinstance(handler, instance):
                        handler.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
                        return True
            return False       


class FileManager:
    def __init__(self):
        self.root = "/home/dev/DATABASE"
        self.today = datetime.datetime.now().strftime("%Y%m%d")
        self.current = None
        self.symlink = "/home/dev/DATABASE/current"

    def update_list(self):
        self.recordings = [f for f in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, f))]
        self.paths = [os.path.join(self.root, f) for f in os.listdir(self.root)]

    def get_path(self):
        if self.current is None:
            return None
        else:
            return os.path.join(self.root, self.current)

    @try_except
    def create_dir(self):
        self.update_list()
        if not any([self.today in f for f in self.recordings]):
            dir_name = f"{self.today}T{0:03}"
            os.mkdir(os.path.join(self.root, dir_name))
            self.current = dir_name
            return True
        
        cnt =  max([int(f.split("T")[1]) for f in self.recordings if self.today in f]) + 1
        dir_name = f"{self.today}T{cnt:03}"
        os.mkdir(os.path.join(self.root, dir_name))
        self.current = dir_name
        self.gen_symlink()
        return True
    
    def gen_symlink(self):
        if os.path.islink(self.symlink) or os.path.exists(self.symlink):
            os.unlink(self.symlink)

        os.symlink(self.get_path(), self.symlink)
    
class ConfigManager:
    def __init__(self, initial_config: dict):
        self._config = deepcopy(initial_config)
        self._undo_stack = []
        self._redo_stack = []

    @property
    def config(self):
        return deepcopy(self._config)

    def apply(self, new_config: dict):
        patch = jsonpatch.make_patch(self._config, new_config)
        self._undo_stack.append(patch)
        self._redo_stack.clear()
        self._config = deepcopy(new_config)

    def undo(self):
        if not self._undo_stack:
            return False

        patch = self._undo_stack.pop()
        inverse = patch.inverse()
        self._redo_stack.append(patch)
        self._config = inverse.apply(self._config)
        return True

    def redo(self):
        if not self._redo_stack:
            return False

        patch = self._redo_stack.pop()
        self._undo_stack.append(patch)
        self._config = patch.apply(self._config)
        return True

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self._config, f, indent=2)

    def load(self, path):
        with open(path) as f:
            self._config = json.load(f)
        self._undo_stack.clear()
        self._redo_stack.clear()

    
    
class Core:
    def __init__(self):
        self.file_manager = FileManager()
        self.logger = LoggerManager()
        self.config_manager = ConfigManager({})
        self.recording = False
        self.video_writer = None
        self.writer = None
    
    @try_except
    def init_recording(self):
        self.close_recording()
        if self.file_manager.create_dir() is None:
            return False
        path = self.file_manager.get_path()
        current = self.file_manager.current
        self.metadata = {
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "duration": None,
            "recording": current,
            "log": os.path.join(path, 'log'),
            "csv": os.path.join(path, 'data.csv'),
            "video": os.path.join(path, 'camera_feed.mp4'),
            "config": self.config_manager.config
        }
        self.metafile = os.path.join(path, 'metadata.json')
    # TODO: check with config
        # Set up logging
        self.logger.setup_file_logger(self.metadata["config"], self.metadata["log"])

        # Set up CSV recording
        self.csv_file = open(self.metadata["csv"], "w", newline="")
        self.writer = csv.DictWriter(self.csv_file, fieldnames=["ts", "frame_id", "s1", "s2", "s3", "s4"]) #TODO: add more sensors
        self.writer.writeheader()
        
        # Set up video recording
        self.video_writer = cv2.VideoWriter(
            self.metadata["video"],
            cv2.VideoWriter_fourcc(*"mp4v"),
            30,
            (640, 480)
        )
        return True
    
    @try_except
    def close_recording(self):
        self.recording = False
        safe_call(self.video_writer.release, label="release video writer")
        self.writer = None
        safe_call(self.csv_file.close, label="close csv file")
        with open(self.metafile, "w") as f:
            json.dump(self.metadata, f, indent=2)
        return True

frame_counter = itertools.count()
core_ = Core()


FPS_INVERSE = 1/30
SPS_INVERSE = 1/100

latest_frame = {
    "frame_id": None,
    "ts": None
}

lock = threading.Lock()

