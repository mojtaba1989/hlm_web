import json
import os


class ConfigManager:
    def __init__(self):
        self.root = "/home/dev/hlm_web/backend/.configs"
        self.configs = {}
        self.default = 'default.cfg'
        self.load('current.cfg')
        self.reconfigured = False

    def get_ignore_case(self, d, key):
        for k, v in d.items():
            if k.lower() == key.lower():
                return v
        return {}

    def load(self, config_name: str = "default.cfg"):
        path = os.path.join(self.root, config_name)
        if not os.path.exists(path):
            path = os.path.join(self.root, self.default)
        with open(path) as f:
            self.configs = json.load(f)
        self.reconfigured = True

    def save(self, conig):
        path = os.path.join(self.root, 'current.cfg')
        self.configs = conig
        with open(path, "w") as f:
            json.dump(self.configs, f, indent=2)
        self.reconfigured = True

    def is_reconfigured(self):
        tmp = self.reconfigured
        self.reconfigured = False
        return tmp

    def get(self, path: str):
        obj = self.configs
        for key in path.split("."):
            obj = self.get_ignore_case(obj, key)
        return obj[0] if obj else None
    
config_ = ConfigManager()