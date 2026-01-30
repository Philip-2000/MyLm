import os

ONLINE_CONFIG = {
    "Qwen3-Ours": {"name": "Qwen3-Ours", "base_url":"http://10.0.2.232:12345/v1", "model":"qwen3-235b-instruct", "api_key":"-"},
    
}



BASE_CONFIG = [
    {"name": "Qwen3-32B",                   "port": 7001, "env": "try"},
    {"name": "InternVideo2.5-Chat-8B",      "port": 8001, "env": "ivd"},
    {"name": "InternVL3_5-8B",              "port": 8002, "env": "try"},
    {"name": "Qwen3-VL-8B-Instruct",        "port": 8003, "env": "try"},
    {"name": "Qwen2.5-VL-7B-Instruct",      "port": 8004, "env": "try"},
    {"name": "LLaVA-NeXT-Video-7B-hf",      "port": 8005, "env": "try"},
    {"name": "LLaVA-Video-7B-Qwen2",        "port": 8006, "env": "llava"},
    {"name": "llava-onevision-qwen2-7b-ov", "port": 8007, "env": "llava"},
    {"name": "LongVA-7B-DPO",               "port": 8008, "env": "longva"},
    {"name": "EgoGPT-7b-EgoIT-EgoLife",     "port": 8009, "env": "egogpt"},
    {"name": "Qwen3_Embedding_0.6B",        "port": 9001, "env": "try"},
]


GLOBAL_CONFIG = [ [conf.copy()] + [{"name":conf['name']+ f":{chr(ord('a')+i)}", "port":conf["port"]+10000*i, "env":conf["env"]}  for i in range(5)] for conf in BASE_CONFIG ]
# Flatten the list
GLOBAL_CONFIG = [item for sublist in GLOBAL_CONFIG for item in sublist]


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