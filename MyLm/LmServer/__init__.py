import os
GLOBAL_CONFIG = [
    {"name": "InternVideo2.5-Chat-8B",      "port": 8001, "env": "ivd"},
    {"name": "InternVL3_5-8B",              "port": 8002, "env": "try"},
    {"name": "Qwen3-VL-8B-Instruct",        "port": 8003, "env": "try"},
    {"name": "Qwen2.5-VL-7B-Instruct",      "port": 8004, "env": "try"},
    {"name": "LLaVA-NeXT-Video-7B-hf",      "port": 8005, "env": "try"},
    {"name": "LLaVA-Video-7B-Qwen2",        "port": 8006, "env": "llava"},
    {"name": "llava-onevision-qwen2-7b-ov", "port": 8007, "env": "llava"},
    {"name": "LongVA-7B-DPO",               "port": 8008, "env": "longva"},
    {"name": "EgoGPT-7b-EgoIT-EgoLife",     "port": 8009, "env": "egogpt"},
    {"name": "Qwen4-VL-8B-Instruct",        "port":18003, "env": "try",   "source": "Qwen3-VL-8B-Instruct"},
    {"name": "Qwen5-VL-8B-Instruct",        "port":28003, "env": "try",   "source": "Qwen3-VL-8B-Instruct"},
    {"name": "Qwen6-VL-8B-Instruct",        "port":38003, "env": "try",   "source": "Qwen3-VL-8B-Instruct"},
    {"name": "Qwen7-VL-8B-Instruct",        "port":48003, "env": "try",   "source": "Qwen3-VL-8B-Instruct"},
    {"name": "InternVideo2.6-Chat-8B",      "port":18001, "env": "ivd",   "source": "InternVideo2.5-Chat-8B"},
    {"name": "InternVideo2.7-Chat-8B",      "port":28001, "env": "ivd",   "source": "InternVideo2.5-Chat-8B"},
    {"name": "InternVideo2.8-Chat-8B",      "port":38001, "env": "ivd",   "source": "InternVideo2.5-Chat-8B"},
    {"name": "LLaVA-VVdeo-7B-Qwen2",        "port":18006, "env": "llava", "source": "LLaVA-Video-7B-Qwen2"},
    {"name": "LLaVA-VVVeo-7B-Qwen2",        "port":28006, "env": "llava", "source": "LLaVA-Video-7B-Qwen2"},
    {"name": "LLaVA-VVVVo-7B-Qwen2",        "port":38006, "env": "llava", "source": "LLaVA-Video-7B-Qwen2"},
]

class GlobalConfig:
    def __init__(self):
        self.config = GLOBAL_CONFIG

    def __getitem__(self, item):
        if isinstance(item, int):
            if item < 1000:
                return self.config[item]
            else:
                for conf in self.config:
                    if conf["port"] == item:
                        return conf
                raise KeyError(f"Config for port {item} not found.")
        elif isinstance(item, str):
            for conf in self.config:
                if conf["name"] == item:
                    return conf
            raise KeyError(f"Config for {item} not found.")
        raise KeyError(f"Config for {item} not found.")

GLOBAL_CONFIG = GlobalConfig()
MODEL_BASE  = "/mnt/data/models/"

from .Interface import call
from .Models import create
from .Server import serve

def one(model_name: str, input_data: dict):
    print("one")
    return create(model_name)(input_data)