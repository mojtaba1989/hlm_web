import datetime
import os
import json
import csv

from nodes.utils import try_except, safe_call, socket_recorder
from nodes.camera_ import video_recorder, convert_to_mp4
from nodes.lux_ import DAQ_bin_to_csv
from nodes.rt_ import XCOM_converter
from nodes.file_manager_ import FileManager
from nodes.logger_ import logger_ as logger
from nodes.config_manager_ import config_ as config
from nodes.postprocess_ import TestPostProcess


class Core:
    def __init__(self):
        self.file_manager = FileManager(logger)
        self.current_scenario = 'unknown'
        self.postprocess_enabled = False
        self.recorders = {}
        logger.logger.info("[NODE-INFO] Core initialized")
        self.register_sensors()
        self.recording = False

    def register_sensors(self):
        self.recorders = {}
        # Add DAQ socket
        if config.get('DAQ.ENABLED'):
            tmp = socket_recorder(config.get('DAQ.IP/NETMASK'),
                                port=config.get('DAQ.PORT'),
                                name='DAQ',
                                max_failed=config.get('DAQ.MAX_FAILURES'),)
            if not tmp.is_duplicate(self.recorders):
                self.recorders['DAQ'] = {
                    'recorder': tmp,
                    'converter': DAQ_bin_to_csv
                }
            else:
                logger.logger.error("Core: IP AND PORT ALREADY IN USE")
        # Add Lux socket
        if config.get('NCOM.ENABLED'):
            tmp = socket_recorder(config.get('NCOM.IP/NETMASK'),
                                port=config.get('NCOM.PORT'),
                                name='NCOM',
                                max_failed=config.get('NCOM.MAX_FAILURES'),)
            if not tmp.is_duplicate(self.recorders):
                self.recorders['NCOM'] = {
                    'recorder': tmp,
                    'converter': XCOM_converter
                }
            else:
                logger.logger.error("Core: IP AND PORT ALREADY IN USE")

        # Add RCOM socket
        if config.get('RCOM.ENABLED'):
            tmp = socket_recorder(config.get('RCOM.IP/NETMASK'),
                                port=config.get('RCOM.PORT'),
                                name='RCOM',
                                max_failed=config.get('RCOM.MAX_FAILURES'),)
            if not tmp.is_duplicate(self.recorders):
                self.recorders['RCOM'] = {
                    'recorder': tmp,
                    'converter': XCOM_converter
                }
            else:
                logger.logger.error("Core: IP AND PORT ALREADY IN USE")

        # Add CAMERA
        if config.get('CAMERA.ENABLED'):
            self.recorders['CAMERA'] = {
                'recorder': video_recorder(),
                'converter': convert_to_mp4
            }
        logger.logger.info("[NODE-INFO] Sensors registered")

    @try_except
    def init_recording(self):
        if self.recording:
            logger.logger.info("Core: Already recording")
            return
        logger.logger.info("Core: Starting new recording")
        if self.file_manager.create_dir() is None:
            logger.logger.error("Core: Failed to create recording directory")
            return False
        
        if config.is_reconfigured():
            self.register_sensors()
        path = self.file_manager.get_path()
        current = self.file_manager.current
        self.metadata = {
            "start_time": datetime.datetime.now(),
            "end_time": None,
            "duration": None,
            "recording": current,
            "scenario_config_number": self.current_scenario,
            "result": "",
            "log": os.path.join(path, 'log'),
            "DAQ": os.path.join(path, 'daq.csv') if "DAQ" in self.recorders else "",
            "CAMERA": os.path.join(path, 'camera_feed.mp4') if "CAMERA" in self.recorders else "",
            "RCOM": os.path.join(path, 'rcom.csv') if "RCOM" in self.recorders else "",
            "NCOM": os.path.join(path, 'ncom.csv') if "NCOM" in self.recorders else "",
            "config": config.configs
        }
        self.metafile = os.path.join(path, 'metadata.json')
        # Set up logging
        if config.get("FILE_LOGGER.ENABLED"):
            logger.setup_file_logger(self.metadata["log"], config.get("FILE_LOGGER.LEVEL"))
        
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
        logger.logger.info("Core: Closing recording")
        self.metadata["end_time"] = datetime.datetime.now()
        self.recording = False
        # Stop recording
        for key in self.recorders:
            self.recorders[key]['recorder'].stop()
        
        # Convert files
        for key in self.recorders:
            if self.recorders[key]['converter'] is not None:
                result = self.recorders[key]['converter'](self.metadata[key], config)
                if result["status"] == "success":
                    logger.logger.info(result["message"])
                    for msg in result.get("more", []):
                        logger.logger.debug(msg)
                else:
                    logger.logger.error(result["message"])

        self.metadata["duration"] = str(self.metadata["end_time"] - self.metadata["start_time"])
        self.metadata["end_time"] = self.metadata["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        self.metadata["start_time"] = self.metadata["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        with open(self.metafile, "w") as f:
            json.dump(self.metadata, f, indent=2)
        logger.logger.info("Core: Recording closed")
        logger.logger.info(f"Core: Recording saved to {self.metadata['recording']}")
        logger.logger.info(f"Core: Recording duration: {self.metadata['duration']}")
        
        if self.postprocess_enabled:
            logger.logger.info("Core: Starting postprocessing")
            tpp = TestPostProcess()
            tpp.process(self.file_manager.get_path())
        return True
    
core_ = Core()