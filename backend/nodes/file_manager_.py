import datetime
import os
from nodes.utils import try_except
from nodes.logger_ import logger_ as logger

class FileManager:
    def __init__(self, logger=None):
        self.root = "/home/dev/DATABASE"
        self.today = datetime.datetime.now().strftime("%Y%m%d")
        self.current = None
        self.symlink = "/home/dev/DATABASE/current"
        logger.logger.info("[NODE-INFO] File manager node initialized")
        self.check_root()
        self.update_list()
    
    def check_root(self):
        if not os.path.exists(self.root):
            os.mkdir(self.root)

    def update_list(self):
        logger.logger.info("FileManager: Updating recording list")
        self.recordings = [f for f in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, f))]
        self.paths = [os.path.join(self.root, f) for f in os.listdir(self.root)]

    def get_path(self):
        if self.current is None:
            return None
        else:
            return os.path.join(self.root, self.current)

    @try_except
    def create_dir(self):
        logger.logger.info("FileManager: Creating new recording directory")
        self.update_list()
        if not any([self.today in f for f in self.recordings]):
            dir_name = f"{self.today}T{0:03}"
            os.mkdir(os.path.join(self.root, dir_name))
            self.current = dir_name
            self.gen_symlink()
            logger.logger.info(f"FileManager: Created new recording directory {dir_name}")
            return True
        
        cnt =  max([int(f.split("T")[1]) for f in self.recordings if self.today in f]) + 1
        dir_name = f"{self.today}T{cnt:03}"
        os.mkdir(os.path.join(self.root, dir_name))
        self.current = dir_name
        self.gen_symlink()
        logger.logger.info(f"FileManager: Created new recording directory {dir_name}")
        return True
    
    def gen_symlink(self):
        if os.path.islink(self.symlink) or os.path.exists(self.symlink):
            logger.logger.info("FileManager: Removing old symlink")
            os.unlink(self.symlink)

        os.symlink(self.get_path(), self.symlink)
        logger.logger.info(f"FileManager: Created symlink to {self.get_path()}")