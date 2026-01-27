import datetime
import os
import json
import csv

from nodes.utils import try_except, safe_call, socket_recorder
from nodes.camera_ import video_recorder
from nodes.lux_ import DAQ_bin_to_csv
from nodes.file_manager_ import FileManager
from nodes.logger_ import LoggerManager
from nodes.config_manager_ import ConfigManager


class Core:
    def __init__(self, logger):
        self.file_manager = FileManager(logger)
        self.logger = logger
        self.video_recorder = video_recorder(logger)
        self.socket_recorders = {}
        self.config = ConfigManager({})
        self.logger.logger.info("[NODE-INFO] Core initialized")
        self.register_sockets()
        self.recording = False

    def register_sockets(self):
        tmp = socket_recorder('10.0.0.105',
                               port=5555,
                               name='lux',
                               logger=self.logger,
                               max_failed=-1)
        if not tmp.is_duplicate(self.socket_recorders):
            self.socket_recorders['lux'] = {
                'recorder': tmp,
                'converter': DAQ_bin_to_csv
            }
    
    @try_except
    def init_recording(self):
        if self.recording:
            self.logger.logger.info("Core: Already recording")
            return
        self.logger.logger.info("Core: Starting new recording")
        if self.file_manager.create_dir() is None:
            self.logger.logger.error("Core: Failed to create recording directory")
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
        self.socket_recorders['lux']['recorder'].set_file_name(self.metadata["csv"])

        for key in self.socket_recorders:
            self.socket_recorders[key]['recorder'].start()

        # Set up video recorder
        self.video_recorder.file_name = self.metadata["video"]
        self.video_recorder.start()
        return True
    
    @try_except
    def close_recording(self):
        if not self.recording:
            return
        self.logger.logger.info("Core: Closing recording")
        self.metadata["end_time"] = datetime.datetime.now()
        self.recording = False
        self.video_recorder.stop()
        for key in self.socket_recorders:
            self.socket_recorders[key]['recorder'].stop()
        self.video_recorder.convert_to_mp4()
        self.socket_recorders['lux']['converter'](self.metadata["csv"],self.logger)
        self.writer = None
        self.metadata["duration"] = str(self.metadata["end_time"] - self.metadata["start_time"])
        self.metadata["end_time"] = self.metadata["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        self.metadata["start_time"] = self.metadata["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        with open(self.metafile, "w") as f:
            json.dump(self.metadata, f, indent=2)
        self.logger.logger.info("Core: Recording closed")
        self.logger.logger.info(f"Core: Recording saved to {self.metadata['recording']}")
        self.logger.logger.info(f"Core: Recording duration: {self.metadata['duration']}")
        return
    
logger_ = LoggerManager()
core_ = Core(logger_)