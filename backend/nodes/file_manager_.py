import datetime
import os
from nodes.utils import try_except

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