import json
import os


class ConfigManager:
    def __init__(self):
        self.root = "/home/dev/hlm_web/backend/.configs"
        self.configs = {}
        self.load('current.cfg')

    def get_ignore_case(self, d, key):
        for k, v in d.items():
            if k.lower() == key.lower():
                return v
        return {}

    def load(self, config_name: str = 'default.cfg'):
        path = os.path.join(self.root, config_name)
        if not os.path.exists(path):
            return
        with open(path) as f:
            self.configs = json.load(f)

    def save(self, conig):
        path = os.path.join(self.root, 'current.cfg')
        self.configs = conig
        with open(path, "w") as f:
            json.dump(self.configs, f, indent=2)

    def get(self, path: str):
        obj = self.configs
        for key in path.split("."):
            obj = self.get_ignore_case(obj, key)
        return obj[0] if obj else None