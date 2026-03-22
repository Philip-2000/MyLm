import os

ONLINE_CONFIG = {
    "Qwen3-Ours": {"name": "Qwen3-Ours", "base_url":"http://10.0.2.232:12345/v1", "model":"qwen3-235b-instruct", "api_key":"-", "par":"235b-instruct"},
    
}



BASE_CONFIG = [
    {"name": "Qwen3-32B",                   "port": 7001, "env": "try", "par":"32B"}, #["4B","8B","32B","30B-A3B", "1.7B", "14B"]
    {"name": "InternVideo2.5-Chat-8B",      "port": 8001, "env": "ivd", "par":"8B"}, #["8B"]
    {"name": "InternVL3_5-8B",              "port": 8002, "env": "try", "par":"38B-Instruct"}, #["1B","2B","4B","8B","38B","1B-Instruct","2B-Instruct","4B-Instruct","8B-Instruct","38B-Instruct"]
    {"name": "Qwen3-VL-8B-Instruct",        "port": 8003, "env": "try", "par":"8B-Instruct"}, #["4B-Instruct","8B-Instruct","32B-Instruct"]
    {"name": "Qwen2.5-VL-7B-Instruct",      "port": 8004, "env": "try", "par":"72B-Instruct"}, #["3B-Instruct","7B-Instruct","32B-Instruct","72B-Instruct"]
    {"name": "LLaVA-NeXT-Video-7B-hf",      "port": 8005, "env": "try", "par":"7B-hf"},
    {"name": "LLaVA-Video-7B-Qwen2",        "port": 8006, "env": "llava", "par":"72B"}, #["7B","72B"]
    {"name": "llava-onevision-qwen2-7b-ov", "port": 8007, "env": "llava", "par":"72b-ov-sft"}, #["0.5b-ov","7b-ov","72b-ov-sft"]
    {"name": "LongVA-7B-DPO",               "port": 8008, "env": "longva", "par":"7B-DPO"}, #["7B-DPO"]
    {"name": "EgoGPT-7b-EgoIT-EgoLife",     "port": 8009, "env": "egogpt", "par":"7b"}, #["7b"]
    {"name": "Qwen3.5-27B",                 "port": 8010, "env": "base", "par":"27B"}, #["4B, 27B, 122B-A10B-FP8"]
    {"name": "Qwen3_Embedding_0.6B",        "port": 9001, "env": "try", "par":"0.6B"}, #["0.6B", "4B", "8B"]
    {"name": "Qwen3-VL-Embedding-2B",       "port": 9002, "env": "try", "par":"8B"}, #["2B", "8B"]
    {"name": "Qwen3-Embed-0.6B",            "port": 9003, "env": "try", "par":"0.6B"}, #["0.6B", "4B", "8B"]
]


GLOBAL_CONFIG = [ [conf.copy()] + [{"name":conf['name']+ f":{chr(ord('a')+i)}", "port":conf["port"]+10000*i, "env":conf["env"], "par":conf["par"]}  for i in range(5)] for conf in BASE_CONFIG ]
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