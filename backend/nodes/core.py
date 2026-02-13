import datetime
import os
import json
import csv

from nodes.utils import try_except, safe_call, socket_recorder
from nodes.camera_ import video_recorder, convert_to_mp4
from nodes.lux_ import DAQ_bin_to_csv
from nodes.rt_ import NCOM_converter, RCOM_converter 
from nodes.file_manager_ import FileManager
from nodes.logger_ import LoggerManager
from nodes.config_manager_ import ConfigManager


class Core:
    def __init__(self, logger, config):
        self.file_manager = FileManager(logger)
        self.config = config
        self.logger = logger
        self.recorders = {}
        self.logger.logger.info("[NODE-INFO] Core initialized")
        self.register_sensors()
        self.recording = False

    def register_sensors(self):
        self.recorders = {}
        # Add DAQ socket
        if self.config.get('DAQ.ENABLED'):
            tmp = socket_recorder(self.config.get('DAQ.IP/NETMASK'),
                                port=self.config.get('DAQ.PORT'),
                                name='DAQ',
                                logger=self.logger,
                                max_failed=self.config.get('DAQ.MAX_FAILURES'),)
            if not tmp.is_duplicate(self.recorders):
                self.recorders['DAQ'] = {
                    'recorder': tmp,
                    'converter': DAQ_bin_to_csv
                }
            else:
                self.logger.logger.error("Core: IP AND PORT ALREADY IN USE")
        # Add Lux socket
        if self.config.get('NCOM.ENABLED'):
            tmp = socket_recorder(self.config.get('NCOM.IP/NETMASK'),
                                port=self.config.get('NCOM.PORT'),
                                name='NCOM',
                                logger=self.logger,
                                max_failed=self.config.get('NCOM.MAX_FAILURES'),)
            if not tmp.is_duplicate(self.recorders):
                self.recorders['NCOM'] = {
                    'recorder': tmp,
                    'converter': RCOM_converter
                }
            else:
                self.logger.logger.error("Core: IP AND PORT ALREADY IN USE")

        # Add RCOM socket
        if self.config.get('RCOM.ENABLED'):
            tmp = socket_recorder(self.config.get('RCOM.IP/NETMASK'),
                                port=self.config.get('RCOM.PORT'),
                                name='RCOM',
                                logger=self.logger,
                                max_failed=self.config.get('RCOM.MAX_FAILURES'),)
            if not tmp.is_duplicate(self.recorders):
                self.recorders['RCOM'] = {
                    'recorder': tmp,
                    'converter': NCOM_converter
                }
            else:
                self.logger.logger.error("Core: IP AND PORT ALREADY IN USE")

        # Add CAMERA
        if self.config.get('CAMERA.ENABLED'):
            self.recorders['CAMERA'] = {
                'recorder': video_recorder(self.logger, self.config),
                'converter': convert_to_mp4
            }
        self.logger.logger.info("[NODE-INFO] Sensors registered")

    @try_except
    def init_recording(self):
        if self.recording:
            self.logger.logger.info("Core: Already recording")
            return
        self.logger.logger.info("Core: Starting new recording")
        if self.file_manager.create_dir() is None:
            self.logger.logger.error("Core: Failed to create recording directory")
            return False
        
        if self.config.is_reconfigured():
            self.register_sensors()
        path = self.file_manager.get_path()
        current = self.file_manager.current
        self.metadata = {
            "start_time": datetime.datetime.now(),
            "end_time": None,
            "duration": None,
            "recording": current,
            "result": "unknown",
            "log": os.path.join(path, 'log'),
            "DAQ": os.path.join(path, 'daq.csv'),
            "CAMERA": os.path.join(path, 'camera_feed.mp4'),
            "RCOM": os.path.join(path, 'rcom.csv'),
            "NCOM": os.path.join(path, 'ncom.csv'),
            "config": self.config.configs
        }
        self.metafile = os.path.join(path, 'metadata.json')
        # Set up logging
        if self.config.get("FILE_LOGGER.ENABLED"):
            self.logger.setup_file_logger(self.metadata["log"], self.config.get("FILE_LOGGER.LEVEL"))
        
        # Set up destination files
        for key in self.recorders.keys():
            self.recorders[key]['recorder'].set_file_name(self.metadata[key])

        # Start recording
        for key in self.recorders.keys():
            self.recorders[key]['recorder'].start()
        return True
    
    @try_except
    def close_recording(self):
        if not self.recording:
            return
        self.logger.logger.info("Core: Closing recording")
        self.metadata["end_time"] = datetime.datetime.now()
        self.recording = False
        # Stop recording
        for key in self.recorders:
            self.recorders[key]['recorder'].stop()
        
        # Convert files
        for key in self.recorders:
            if self.recorders[key]['converter'] is not None:
                result = self.recorders[key]['converter'](self.metadata[key], self.config)
                if result["status"] == "success":
                    self.logger.logger.info(result["message"])
                else:
                    self.logger.logger.error(result["message"])

        self.metadata["duration"] = str(self.metadata["end_time"] - self.metadata["start_time"])
        self.metadata["end_time"] = self.metadata["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        self.metadata["start_time"] = self.metadata["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        with open(self.metafile, "w") as f:
            json.dump(self.metadata, f, indent=2)
        self.logger.logger.info("Core: Recording closed")
        self.logger.logger.info(f"Core: Recording saved to {self.metadata['recording']}")
        self.logger.logger.info(f"Core: Recording duration: {self.metadata['duration']}")
        return True
    
logger_ = LoggerManager()
config_ = ConfigManager()
core_ = Core(logger_, config_)