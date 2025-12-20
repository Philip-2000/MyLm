from .Benchmark import Benchmark
import os, json
from os.path import join as opj
BENCH_BASE = "/mnt/data/raw_data/"

BENCH_CONFIGS = {
    "LongTimeScope": {
        "path": BENCH_BASE + "LongTimeScope",
        "loader": Benchmark.asLongTimeScope,
    },
    "LongVideoBench": {
        "path": BENCH_BASE + "LongVideoBench",
        "loader": Benchmark.asLongVideoBench,
    },
    "LVBench": {
        "path": BENCH_BASE + "LVBench",
        "loader": Benchmark.asLVBench,
    },
    "MLVU": {
        "path": BENCH_BASE + "MLVU",
        "loader": Benchmark.asMLVU,
    },
    "EgoSchema": {
        "path": BENCH_BASE + "egoschema",
        "loader": Benchmark.asEgoSchema,
    },
    "EgoLifeQA": {
        "path": BENCH_BASE + "EgoLife",
        "loader": Benchmark.asEgoLifeQA,
    },
    "EgoR1Bench": {
        "path": BENCH_BASE + "Ego-R1-bench",
        "loader": Benchmark.asEgoR1Bench,
    },
    "XLeBench": {
        "path": BENCH_BASE + "X-LeBench",
        "loader": Benchmark.asXLeBench,
    },
    # "VideoMME": {
    #     "path": BENCH_BASE + "Video-MME",
    #     "loader": Benchmark.asVideoMME,
    # },
}

EGOLIFE_TSS_FULL = {
    "A1_JAKE": None,
    "A2_ALICE": None,
    "A3_TASHA": None,
    "A4_LUCIA": None,
    "A5_KATRINA": None,
    "A6_SHURE": None,
}
EGOLIFE_MAP_JSON = None
XLEN_LEN_JSON = None

def egolife_map():
    from decord import VideoReader, cpu
    DIR = os.path.join("/mnt", "data", "raw_data", "EgoLife")
    MAP = {"meta": {"name":"EgoLife", "person":0, "segments":0, "videos":0}, "content":[]}
    for person in [c for c in os.listdir(DIR) if c[0]=="A"]:
        MAP_PERSON = {"meta": {"name": person, "segments":0, "videos":0}, "content":[]}
        for d in range(1,8):
            day = f"DAY{d}"
            day_dir = os.path.join(DIR, person, day)
            HHMMSSff_list = [v.split('_')[-1].split('.')[0] for v in os.listdir(day_dir) if v.endswith(".mp4")]
            HHMMSSff_list.sort()

            MAP_PERSON_SEGMENT = {"meta":{"day":day, "segment_id":0, "videos":0}, "content":[]}

            for i, hhmmssff in enumerate(HHMMSSff_list):
                video_path = os.path.join(day_dir, f"{day}_{person}_{hhmmssff}.mp4")
                vr = VideoReader(video_path, ctx=cpu(0), num_threads=1)
                duration_seconds = len(vr) / vr.get_avg_fps()
                if i == len(HHMMSSff_list) - 1:
                    gap_s = 1e9
                else:
                    HHMMSSFF = HHMMSSff_list[i+1]
                    gap_s = (int(HHMMSSFF[0:2]) - int(hhmmssff[0:2])) * 3600 + (int(HHMMSSFF[2:4]) - int(hhmmssff[2:4])) * 60 + (int(HHMMSSFF[4:6]) - int(hhmmssff[4:6])) + (int(HHMMSSFF[6:8]) - int(hhmmssff[6:8])) / 20.0
                if gap_s > duration_seconds+0.06:
                    print(f"Person: {person}, Day: {day}, Video Start Time: {hhmmssff}, Duration: {duration_seconds:.2f}s, Gap to Next: {gap_s}s")
                    MAP_PERSON_SEGMENT_VIDEO = {
                        "hhmmssff": hhmmssff,
                        "video_path": video_path,
                        "duration_seconds": duration_seconds,
                    }
                    MAP_PERSON_SEGMENT["content"].append(MAP_PERSON_SEGMENT_VIDEO)
                    MAP_PERSON_SEGMENT["meta"]["videos"] += 1

                    MAP_PERSON["content"].append(MAP_PERSON_SEGMENT)
                    MAP_PERSON["meta"]["segments"] += 1
                    MAP_PERSON["meta"]["videos"] += MAP_PERSON_SEGMENT["meta"]["videos"]
                    MAP_PERSON_SEGMENT = {"meta":{"day":day, "segment_id":len(MAP_PERSON["content"]), "videos":0}, "content":[]}
                else:
                    MAP_PERSON_SEGMENT_VIDEO = {
                        "hhmmssff": hhmmssff,
                        "video_path": video_path,
                        "duration_seconds": duration_seconds,
                    }
                    MAP_PERSON_SEGMENT["content"].append(MAP_PERSON_SEGMENT_VIDEO)
                    MAP_PERSON_SEGMENT["meta"]["videos"] += 1
        

        MAP["content"].append(MAP_PERSON)
        MAP["meta"]["person"] += 1
        MAP["meta"]["segments"] += MAP_PERSON["meta"]["segments"]
        MAP["meta"]["videos"] += MAP_PERSON["meta"]["videos"]

    with open(os.path.join(os.path.dirname(__file__),"egolife_map.json"), "w") as f:
        json.dump(MAP, f, indent=4)

EGO4D_VIDEO_BASE = opj("/mnt", "data", "raw_data", "Ego4d", "v2", "full_scale")
CONCAT_VIDEO_CACHE = opj("/mnt", "data", "yl", "cache")