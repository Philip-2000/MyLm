class No:
    def __getitem__(self, key):
        return False
class Al:
    def __getitem__(self, key):
        return True
class All:
    def __getitem__(self, key):
        return Al()

class Tes:
    def __getitem__(self, key):
        return key== "Qwen3-VL-8B-Instruct" # "InternVideo2.5-Chat-8B"
    #"Qwen3-VL-8B-Instruct" # "LLaVA-NeXT-Video-7B-hf"
                    # "Qwen2.5-VL-7B-Instruct" # √
                    # "Qwen3-VL-8B-Instruct" # √
                    #"InternVL3_5-8B" # √
    
                    # "InternVideo2.5-Chat-8B" # √
                    # "LLaVA-NeXT-Video-7B-hf" 
                    # "llava-onevision-qwen2-7b-ov" # √
                    
                    #"LLaVA-Video-7B-Qwen2" # √
                    
                    
                    
                    
                    
                    
class Test:
    def __getitem__(self, key):
        return Tes()  if key =="EgoLifeQA" else No()
    
    
    #b=egoschema        # 500qa,500v
#b=LongTimeScope    # 450qa,450v
#b=LongVideoBench   #1202qa,618v
#b=LVBench          #1549qa,103v
#b=MLVU              #2592qa,1659v
#b=Video_MME        #2700qa,900v

class MaskM:
    def __init__(self, m):
        self.m = m
    def __getitem__(self, key):
        return True if self.m=="All" else (False if self.m=="None" else (key == self.m))

class MaskBM:
    def __init__(self, b, m):
        self.b = b
        self.MASKM = MaskM(m)
    
    def __getitem__(self, keyb):
        return self.MASKM if self.b=="All" else (No() if self.b=="None" or keyb != self.b else (self.MASKM))


def evaluate(_b="None", _m="None", max_qa=1, num_segments=64): #conservative default, not run anything
    mask = MaskBM(_b, _m)
    from ..LmBenches import BENCH_CONFIGS
    from ..LmServer import GLOBAL_CONFIG
    from ..LmBenches import Benchmark
    import os
    Benchmarks = [b for b in BENCH_CONFIGS.keys()] #[os.path.basename(BENCH_CONFIGS[b]["path"]) for b in BENCH_CONFIGS.keys()]
    Methods = [name["name"] for name in GLOBAL_CONFIG.config]
    
    records = []
    for b in Benchmarks:
        for m in Methods:
            if mask[b][m]: #if use the default mask, all true; if use the test mask, only one true
                B = Benchmark.asAuto(b)
                B.run(model=m, max_qa=max_qa, num_segments=num_segments)
                record = {"method": m, **(B.record)}
                records.append(record)
    
    import json, os
    res_dir = os.path.join(os.path.dirname(__file__), "res")
    if not os.path.exists(res_dir): os.makedirs(res_dir)
    import datetime
    tstr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    res_path = os.path.join(res_dir, f"{tstr}.json")
    with open(res_path, "w") as fw:
        json.dump(records, fw)