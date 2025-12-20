
import time, os, json
tomorrow = time.time() + 24*3600
def load(start_time=-1, end_time=tomorrow):
    from ..LmBenches import BENCH_CONFIGS
    from ..LmServer import GLOBAL_CONFIG
    data = {
        "methods": [name["name"] for name in GLOBAL_CONFIG.config],
        "benchmarks": [name for name in BENCH_CONFIGS.keys()],
        "results": [[(None, 0) for _ in BENCH_CONFIGS.keys()] for _ in GLOBAL_CONFIG.config],
    }

    for f in os.listdir(os.path.join(os.path.dirname(__file__), "res")):
        if not f.endswith(".json"): continue
        ftime = os.path.getmtime(os.path.join(os.path.dirname(__file__), "res", f))
        if ftime < start_time or ftime > end_time: continue
        with open(os.path.join(os.path.dirname(__file__), "res", f), "r") as fr:
            res = json.load(fr)
            for r in res:
                #r: {"method": method_name, "benchmark": benchmark_name, "accuracy": accuracy, "total": total}
                if r["method"] in data["methods"] and r["benchmark"] in data["benchmarks"]:
                    mi = data["methods"].index(r["method"])
                    bi = data["benchmarks"].index(r["benchmark"])
                    if data["results"][mi][bi][0] is None:
                        data["results"][mi][bi] = (r["accuracy"], r["total"])
                    else:
                        old_score, old_items = data["results"][mi][bi]
                        new_items = old_items + r["total"]
                        new_score = (old_score * old_items + r["accuracy"] * r["total"]) / new_items
                        data["results"][mi][bi] = (new_score, new_items)
    return data

def reload(start_time=-1, end_time=tomorrow):
    from ..LmBenches import BENCH_CONFIGS
    from ..LmServer import GLOBAL_CONFIG
    data = {
        "methods": [ "InternVideo2.5-Chat-8B", "InternVL3_5-8B", "Qwen3-VL-8B-Instruct","Qwen2.5-VL-7B-Instruct", "LLaVA-Video-7B-Qwen2","llava-onevision-qwen2-7b-ov" ],#[name["name"] for name in GLOBAL_CONFIG.config],
        "benchmarks": ["EgoLifeQA", "EgoR1Bench"], #[name for name in BENCH_CONFIGS.keys()],
        "results": [[ (None, 0) for _ in range(2) ] for _ in range(6)], #[[(None, 0) for _ in BENCH_CONFIGS.keys()] for _ in GLOBAL_CONFIG.config],
    }

    for f in os.listdir(os.path.join(os.path.dirname(__file__), "res")):
        if not f.endswith(".json"): continue
        ftime = os.path.getmtime(os.path.join(os.path.dirname(__file__), "res", f))
        if ftime < start_time or ftime > end_time: continue
        with open(os.path.join(os.path.dirname(__file__), "res", f), "r") as fr:
            res = json.load(fr)
            for r in res:
                #r: {"method": method_name, "benchmark": benchmark_name, "accuracy": accuracy, "total": total}
                if r["method"] in data["methods"] and r["benchmark"] in data["benchmarks"]:
                    mi = data["methods"].index(r["method"])
                    bi = data["benchmarks"].index(r["benchmark"])
                    if data["results"][mi][bi][0] is None:
                        data["results"][mi][bi] = (r["accuracy"], r["total"])
                    else:
                        old_score, old_items = data["results"][mi][bi]
                        new_items = old_items + r["total"]
                        new_score = (old_score * old_items + r["accuracy"] * r["total"]) / new_items
                        data["results"][mi][bi] = (new_score, new_items)
                    # print(f"Loaded result for method {r['method']} on benchmark {r['benchmark']}: accuracy {r['accuracy']} over {r['total']} items.")
    return data

def random(start_time=-1, end_time=tomorrow):
    from ..LmBenches import BENCH_CONFIGS
    from ..LmServer import GLOBAL_CONFIG
    data = {
        "methods": [name["name"] for name in GLOBAL_CONFIG.config],
        "benchmarks": [name for name in BENCH_CONFIGS.keys()],
        "results": [[(None, 0) for _ in BENCH_CONFIGS.keys()] for _ in GLOBAL_CONFIG.config],
    }

    for mi in range(len(data["methods"])):
        for bi in range(len(data["benchmarks"])):
            import random
            score = random.uniform(0, 1)
            items = random.randint(10, 100)
            data["results"][mi][bi] = (score, items)
    return data

def plot(data, figname):
    import matplotlib.pyplot as plt
    import numpy as np

    methods = data["methods"]
    benchmarks = data["benchmarks"]
    results = data["results"]

    x = np.arange(len(benchmarks))
    width = 0.8 / len(methods)

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, method in enumerate(methods):
        scores = [results[i][j][0] if results[i][j][0] is not None else 0 for j in range(len(benchmarks))]
        ax.bar(x + i * width, scores, width, label=method)

    ax.set_xlabel('Benchmarks')
    ax.set_ylabel('Scores')
    ax.set_title('Method Performance on Benchmarks')
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels(benchmarks, rotation=0)#45)
    ax.legend()

    plt.tight_layout()
    plt.savefig(figname)
    plt.close()

def visualize(start_time=-1, end_time=tomorrow, figname="vis.png"):
    data = reload(start_time, end_time) #random(start_time, end_time) #
    plot(data, figname)