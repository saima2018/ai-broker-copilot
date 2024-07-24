import copy
import warnings
import yaml
from easydict import EasyDict as edict


class BaseConfig:
    _allow_write = True  # will be overwritten to false after init

    def __init__(self, cfg_path: str, *, project_path: str):
        cfg = self.load_cfg_file(cfg_path)
        for k, v in cfg.items():
            assert not hasattr(self, k)
            if isinstance(v, str) and "$project_path" in v:
                v = v.replace("$project_path", project_path)
            setattr(self, k, v)

        self._allow_write = False

    @staticmethod
    def load_cfg_file(cfg_path: str):
        with open(cfg_path, 'r', encoding='utf-8') as f:
            contents = yaml.safe_load(f)
        return contents

    def __setattr__(self, key, value):
        if key != "allow_write" and not self._allow_write:
            raise RuntimeError("cfg cls does not support set")

        if isinstance(value, dict):
            value = edict(value)
        self.__dict__[key] = value

    def get(self, key, default="CFG_DEFAULT_NULL_VALUE"):
        if key in self.__dict__:
            return self.__dict__[key]
        if default != "CFG_DEFAULT_NULL_VALUE":
            return default
        else:
            raise KeyError(f"key {key} not existed in cfg")

    def allow_modify(self):
        warnings.warn("modification of cfg must only in test env")
        self._allow_write = True

    def to_dict(self) -> dict:
        ret = copy.deepcopy(self.__dict__)
        [ret.pop(i) for i in self.__dict__.keys() if i.startswith("_")]
        return ret
