import datetime
import os
import json
import csv

from nodes.utils import try_except, safe_call
from nodes.camera_ import video_recorder
from nodes.file_manager_ import FileManager
from nodes.logger_ import LoggerManager
from nodes.config_manager_ import ConfigManager


class Core:
    def __init__(self):
        self.file_manager = FileManager()
        self.logger = LoggerManager()
        self.video_recorder = video_recorder()
        self.config = ConfigManager({})
        self.recording = False
        self.writer = None
    
    @try_except
    def init_recording(self):
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
            "config": self.config.config
        }
        self.metafile = os.path.join(path, 'metadata.json')
    # TODO: check with config
        # Set up logging
        self.logger.setup_file_logger(self.metadata["config"], self.metadata["log"])

        # Set up CSV recording
        self.csv_file = open(self.metadata["csv"], "w", newline="")
        self.writer = csv.DictWriter(self.csv_file, fieldnames=["ts", "frame_id", "s1", "s2", "s3", "s4"])
        self.writer.writeheader()

        # Set up video recorder
        self.video_recorder.file_name = self.metadata["video"]
        self.video_recorder.start()
        return True
    
    @try_except
    def close_recording(self):
        self.recording = False
        self.video_recorder.stop()
        self.video_recorder.convert_to_mp4()
        self.writer = None
        safe_call(self.csv_file.close, label="close csv file")
        with open(self.metafile, "w") as f:
            json.dump(self.metadata, f, indent=2)
        return True
    

core_ = Core()