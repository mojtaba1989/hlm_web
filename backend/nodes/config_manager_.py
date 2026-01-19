import json
import jsonpatch
from copy import deepcopy


class ConfigManager:
    def __init__(self, initial_config: dict):
        self._config = deepcopy(initial_config)
        self._undo_stack = []
        self._redo_stack = []

    @property
    def config(self):
        return deepcopy(self._config)

    def apply(self, new_config: dict):
        patch = jsonpatch.make_patch(self._config, new_config)
        self._undo_stack.append(patch)
        self._redo_stack.clear()
        self._config = deepcopy(new_config)

    def undo(self):
        if not self._undo_stack:
            return False

        patch = self._undo_stack.pop()
        inverse = patch.inverse()
        self._redo_stack.append(patch)
        self._config = inverse.apply(self._config)
        return True

    def redo(self):
        if not self._redo_stack:
            return False

        patch = self._redo_stack.pop()
        self._undo_stack.append(patch)
        self._config = patch.apply(self._config)
        return True

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self._config, f, indent=2)

    def load(self, path):
        with open(path) as f:
            self._config = json.load(f)
        self._undo_stack.clear()
        self._redo_stack.clear()