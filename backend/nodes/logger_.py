import sys
import logging
import queue

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

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
        self.logger.setLevel(logging.INFO)
        self.setup_console_logger()
        self.setup_weblog_logger()
        self.logger.info("[NODE-INFO] Logger node initialized")

    def setup_console_logger(self):
        if any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            self.logger.warning("LogManager: Console logger already set up")
            return
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
        self.logger.info("LogManager: Console logger set up")

    def setup_file_logger(self, file_name : str, level="INFO"):
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                self.logger.info("LogManager: old file logger removed")
                self.logger.removeHandler(handler)
                handler.close()

        self.file_handler = logging.FileHandler(file_name)
        self.file_handler.setLevel(LOG_LEVELS.get(level, logging.INFO))
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.info("LogManager: File logger set up")

    def setup_weblog_logger(self):
        for handler in self.logger.handlers[:]:
            if isinstance(handler, QueueLogHandler):
                self.logger.info("LogManager: old queue logger removed")
                self.logger.removeHandler(handler)
                handler.close()
                
        self.log_queue = queue.Queue()
        self.queue_handler = QueueLogHandler(self.log_queue)
        self.queue_handler.setLevel(logging.INFO)
        self.queue_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.queue_handler)
        self.logger.info("LogManager: Queue logger set up")

    def set_level(self, level, target="all"):
        if target == "all":
            self.logger.info(f"LogManager: Setting log level to {level} - All handlers")
            for handler in self.logger.handlers:
                handler.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
            return True 
        else:
            self.logger.info(f"LogManager: Setting log level to {level} - {target}")
            instance = self.handeler_types.get(target, None)
            if instance is not None:
                for handler in self.logger.handlers:
                    if isinstance(handler, instance):
                        handler.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
                        return True
            return False  