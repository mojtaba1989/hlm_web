import datetime
import os
import json
import csv

from nodes.utils import try_except, safe_call
from nodes.camera_ import video_recorder
from nodes.lux_ import lux_recorder
from nodes.file_manager_ import FileManager
from nodes.logger_ import LoggerManager
from nodes.config_manager_ import ConfigManager


class Core:
    def __init__(self):
        self.file_manager = FileManager()
        self.logger = LoggerManager()
        self.video_recorder = video_recorder()
        self.lux_recorder = lux_recorder()
        self.config = ConfigManager({})
    
    @try_except
    def init_recording(self):
        if self.file_manager.create_dir() is None:
            return False
        path = self.file_manager.get_path()
        current = self.file_manager.current
        self.metadata = {
            "start_time": datetime.datetime.now(),
            "end_time": None,
            "duration": None,
            "recording": current,
            "log": os.path.join(path, 'log'),
            "csv": os.path.join(path, 'data.csv'),
            "video": os.path.join(path, 'camera_feed.mp4'),
            "config": self.config.config
        }
        self.metafile = os.path.join(path, 'metadata.json')
    # TODO: check with config
        # Set up logging
        self.logger.setup_file_logger(self.metadata["config"], self.metadata["log"])

        # Set up Lux recording
        self.lux_recorder.file_name = self.metadata["csv"]
        self.lux_recorder.start()

        # Set up video recorder
        self.video_recorder.file_name = self.metadata["video"]
        self.video_recorder.start()
        return True
    
    @try_except
    def close_recording(self):
        self.metadata["end_time"] = datetime.datetime.now()
        self.recording = False
        self.video_recorder.stop()
        self.lux_recorder.stop()
        self.video_recorder.convert_to_mp4()
        self.lux_recorder.convert_to_csv()
        self.writer = None
        self.metadata["duration"] = str(self.metadata["end_time"] - self.metadata["start_time"])
        self.metadata["end_time"] = self.metadata["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        self.metadata["start_time"] = self.metadata["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        with open(self.metafile, "w") as f:
            json.dump(self.metadata, f, indent=2)
        return True
    

core_ = Core()