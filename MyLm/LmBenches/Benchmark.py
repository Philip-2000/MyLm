from .QA import QA
from .Video import Video
import json,os
from os.path import join as opj

class Benchmark:
    def __init__(self, name=""):
        self.name = name
        self.Videos = {}
        self.QAs = [] # the full QA set containing every QA
        self.qas = [] # the real QAs to run in current test
    
    def __repr__(self):
        return (f"Benchmark: {self.name}, len={len(self.QAs)} QAs, {len(self.Videos)} videos")

    def test(self, model):
        self.run(model)
        return self.compare()
    
    def __len__(self):
        return len(self.QAs)
    
    def __getitem__(self, index):
        return self.QAs[index]
    
    def run(self, model, **kwargs):
        self.qas = self.create_qa(**kwargs)#self.QAs[:kwargs["max_qa"] if kwargs.get("max_qa", -1) > 0 else len(self.QAs)] if kwargs.get("key", None) is None else [qa for qa in self.QAs if qa.uid in kwargs["key"]]
        for qa in self.qas:
            r,c = qa.run(model, **kwargs)
            print(r,c,qa.answer)
        
    def evaluate(self, function, **kwargs):
        self.qas = self.create_qa(**kwargs)#self.QAs[:kwargs["max_qa"] if kwargs.get("max_qa", -1) > 0 else len(self.QAs)] if kwargs.get("key", None) is None else [qa for qa in self.QAs if qa.uid in kwargs["key"]]
        for qa in self.qas:
            r,c = qa.evaluate(function, **kwargs)
            print(r,c,qa.answer)

    def compare(self):
        results = [qa.compare() for qa in self.qas]
        return sum(results) / len(results) if results else 0

    @property
    def record(self):
        return {
            "benchmark": self.name,
            "total": len(self.qas),
            "correct": sum([int(qa._compare) for qa in self.qas]),
            "accuracy": sum([int(qa._compare) for qa in self.qas]) / len(self.qas) if self.qas else 0,
            "records": {qa.uid: qa.record for qa in self.qas}
        }
    
    def save_pe(self):
        #(0) load question json
        from . import BENCH_CONFIGS, EGOLIFE_TSS_FULL
        from .Video import VideoEgoLife
        JSON_PATH = opj(BENCH_CONFIGS[self.name]["path"], "EgoLifeQA", "EgoLifeQA.json") if self.name=="EgoLifeQA" else opj(BENCH_CONFIGS[self.name]["path"], "merge.json")
        VIDEO_BASE = BENCH_CONFIGS[self.name]["path"] if self.name=="EgoLifeQA" else opj(BENCH_CONFIGS[self.name]["path"], "..", "EgoLife")
        JSON = json.load(open(JSON_PATH,"r"))

        for k in EGOLIFE_TSS_FULL.keys():
            JSO = [j for j in JSON if j["identity"]==k]
            if len(JSO)==0: continue
            THE_VIDEO = VideoEgoLife(path=VIDEO_BASE, video_id=f"DAY8_{k}_01000000", bench_object=self, N=64, create=False)
            THE_VIDEO.video_id = k
            self.Videos[k] = THE_VIDEO
            qa_objects = [QA.asEgoLifeQA(qa_dict, self, video_key=k) for qa_dict in JSO]
            THE_VIDEO.QAs = qa_objects
            THE_VIDEO.save_ee()

    def save_ee(self):
        if self.name in ["EgoLifeQA","EgoR1Bench"]: return self.save_pe() #too special, handle separately
        from tqdm import tqdm
        import traceback
        for video in tqdm(self.Videos.values(), desc="Saving Experience and Execution"):
            try:
                video.save_ee()
            except Exception as e:
                traceback.print_exc()
                print(f"Error saving EE for video {video.video_id}: {e}") #raise e

    @classmethod
    def asLongVideoBench(cls, path, **kwargs):
        bench = cls("LongVideoBench")
        JSON_PATH = opj(path, "longvideobench.json")
        VIDEO_BASE = opj(path, "videos")
        for qa_dict in json.load(open(JSON_PATH,"r")):
            video_key = qa_dict["problem_id"][:qa_dict["problem_id"].rfind("_")] #  this will change 86CxyhFV9MI_0 to 86CxyhFV9MI
            if video_key == "4QSmRYQBfN4":
                continue
            if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=opj(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
            
            qa_object = QA.asLongVideoBench(qa_dict, bench)
            bench.QAs.append(qa_object)
            bench.Videos[video_key].append_qa(qa_object)
                
        bench.QAs = sorted(bench.QAs, key=lambda x: x.video_key) # Sort QAs by video_key, so the qa with same video are together, for better caching
        return bench
    
    @classmethod
    def asLVBench(cls, path, **kwargs):
        bench = cls("LVBench")
        JSON_PATH = opj(path, "video_info.meta.jsonl")
        VIDEO_BASE = opj(path, "all_videos")
        with open(JSON_PATH, "r") as f:
            for line in f:
                video_dict = json.loads(line)
                video_key = video_dict["key"]
                if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=opj(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
                for qa_dict in video_dict.get("qa", []):
                    qa_object = QA.asLVBench({"video_key": video_key, **qa_dict}, bench)
                    bench.QAs.append(qa_object)
                    bench.Videos[video_key].append_qa(qa_object)
                
        bench.QAs = sorted(bench.QAs, key=lambda x: x.video_key) # Sort QAs by video_key, so the qa with same video are together, for better caching
        return bench
    
    @classmethod
    def asLongTimeScope(cls, path, **kwargs):
        bench = cls("LongTimeScope")
        JSON_PATH = opj(path, "data/LongTimeScope.json")
        VIDEO_BASE = opj(path, "videos_split_2")
        for qa_dict in json.load(open(JSON_PATH,"r")):
            video_key = qa_dict["problem_id"]
            if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=opj(VIDEO_BASE, f"videos_{video_key[:video_key.rfind('_')]}/{video_key[video_key.rfind('_')+1:]}.mp4"), bench_object=bench ) #"OCR_36000_0" -> videos_OCR_36000/0.mp4
            qa_object = QA.asLongTimeScope(qa_dict, bench)
            bench.QAs.append(qa_object)
            bench.Videos[video_key].append_qa(qa_object)
                
        bench.QAs = sorted(bench.QAs, key=lambda x: x.video_key) # Sort QAs by video_key, so the qa with same video are together, for better caching
        
        return bench
    
    @classmethod
    def asMLVU(cls, path, **kwargs):
        bench = cls("MLVU")
        JSON_PATH = opj(path, "mlvu.json")
        VIDEO_BASE = opj(path, "video")
        for qa_dict in json.load(open(JSON_PATH,"r")):
            video_key = qa_dict["video"][:-4]
            if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=opj(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
            qa_object = QA.asMLVU(qa_dict, bench)
            bench.QAs.append(qa_object)
            bench.Videos[video_key].append_qa(qa_object)
                
        bench.QAs = sorted(bench.QAs, key=lambda x: x.video_key) # Sort QAs by video_key, so the qa with same video are together, for better caching
        
        return bench
    
    @classmethod
    def asVideoMME(cls, path, **kwargs):
        bench = cls("VideoMME")
        JSON_PATH = opj(path, "videomme.json")
        VIDEO_BASE = opj(path, "mme_videos")
        for qa_dict in json.load(open(JSON_PATH,"r")):
            video_key = qa_dict["problem_id"]
            if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=opj(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
            
            qa_object = QA.asVideo_MME(qa_dict, bench)
            bench.QAs.append(qa_object)
            bench.Videos[video_key].append_qa(qa_object)
        return bench

    @classmethod
    def asEgoSchema(cls, path, **kwargs):
        bench = cls("EgoSchema")
        JSON_PATH = opj(path, "merged.json")
        VIDEO_BASE = opj(path, "videos")
        for qa_dict in json.load(open(JSON_PATH,"r")):
            video_key = qa_dict["q_uid"]
            if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=opj(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
            
            qa_object = QA.asEgoSchema(qa_dict, bench)
            bench.QAs.append(qa_object)
            bench.Videos[video_key].append_qa(qa_object)
        return bench

    @classmethod
    def asEgoLifeQA(cls, path, **kwargs):
        bench = cls("EgoLifeQA")
        import json, os, tqdm
        from .Video import VideoEgoLife
        JSON_PATH = opj(path, "EgoLifeQA", "EgoLifeQA.json") #暂时是从那个只公布了的A1_JAKE直接复制过来的，就是说里面只有JAKE的问答，如果以后全公布了那就应该全融合在一起在这个文件中
        VIDEO_BASE = path
        N = kwargs.get("N", 64)
        for qa_dict in tqdm.tqdm(json.load(open(JSON_PATH,"r"))):
            """
            {
                "ID": "1",
                "query_time": {
                    "date": "DAY1",
                    "time": "11210217"
                },
                "type": "EntityLog",
                "type_chinese": "实体日志",
                "need_audio": false,
                "need_name": true,
                "last_time": false,
                "trigger": "The table was filled with various tools and parts",
                "trigger_chinese": "桌上摆满了各种工具和零件",
                "question": "Who used the screwdriver first?",
                "question_chinese": "谁最先使用过螺丝刀？",
                "choice_a": "Tasha",
                "choice_a_chinese": "Tasha",
                "choice_b": "Alice",
                "choice_b_chinese": "Alice",
                "choice_c": "Shure",
                "choice_c_chinese": "Shure",
                "choice_d": "Lucia",
                "choice_d_chinese": "Lucia",
                "answer": "B",
                "target_time": {
                    "date": "DAY1",
                    "time": "11152408"
                },
                "keywords": "use screwdriver",
                "reason": "Saw Alice tightening screws with a screwdriver",
                "reason_chinese": "看见Alice用螺丝刀紧螺丝",
                "identity": "A1_JAKE"
            },
            """
            video_key = f"{qa_dict['query_time']['date']}_{qa_dict['identity']}_{qa_dict['query_time']['time']}_{N}f"
            if video_key not in bench.Videos: bench.Videos[video_key] = VideoEgoLife(path=VIDEO_BASE, video_id=video_key, bench_object=bench, N=N, create=kwargs.get("create", False))
            qa_object = QA.asEgoLifeQA(qa_dict, bench, video_key=video_key)
            bench.QAs.append(qa_object)
            bench.Videos[video_key].append_qa(qa_object) #break

        return bench

    @classmethod
    def asEgoR1Bench(cls, path, **kwargs):
        bench = cls("EgoR1Bench")
        import json, os, tqdm
        from .Video import VideoEgoLife
        JSON_PATH = opj(path, "merge.json")
        VIDEO_BASE = opj(path, "..", "EgoLife")
        N = kwargs.get("N", 64)
        for qa_dict in tqdm.tqdm(json.load(open(JSON_PATH,"r"))):
            
            video_key = f"{qa_dict['query_time']['date']}_{qa_dict['identity']}_{qa_dict['query_time']['time']}_{N}f"
            if video_key not in bench.Videos: bench.Videos[video_key] = VideoEgoLife(path=VIDEO_BASE, video_id=video_key, bench_object=bench, N=N, create=kwargs.get("create", False))
            qa_object = QA.asEgoLifeQA(qa_dict, bench, video_key=video_key)
            bench.QAs.append(qa_object)
            bench.Videos[video_key].append_qa(qa_object)
            
        return bench
    
    @classmethod
    def asXLeBench(cls, path, **kwargs):
        bench = cls("XLeBench")
        import json, os, tqdm, traceback
        from .Video import VideoXLeBench
        JSON_PATH = opj(path, "simulation_annotation")
        VIDEO_BASE = opj(path, "..", "Ego4d", "v2", "full_scale")
        N = kwargs.get("N", 64)
        
        for JSON_FILE in tqdm.tqdm([_ for _ in os.listdir(JSON_PATH) if _.endswith(".json")]):
            try:
                JSON = json.load(open(opj(JSON_PATH, JSON_FILE),"r"))
                video_key = f"{JSON['metadata']['persona_id']}_{JSON['metadata']['memory_id']}_{N}f"
                if video_key not in bench.Videos: bench.Videos[video_key] = VideoXLeBench(path=VIDEO_BASE, video_id=video_key, bench_object=bench, SIM=JSON["simulations"], N=N, create=kwargs.get("create", False))
                
                for q in JSON["tasks"].get("objects_retrieval", {}).get("query_list", []):
                    for qa_dict in q.get("queries", []):
                        qa_object = QA.asXLeBench(qa_dict, bench, video_key=video_key)
                        bench.QAs.append(qa_object)
                        bench.Videos[video_key].append_qa(qa_object)
                
                for q in JSON["tasks"].get("people_retrieval", []).get("query_list", []):
                    for qa_dict in q.get("queries", []):
                        qa_object = QA.asXLeBench(qa_dict, bench, video_key=video_key)
                        bench.QAs.append(qa_object)
                        bench.Videos[video_key].append_qa(qa_object)

                for q in JSON["tasks"].get("action_retrieval", {}).get("moment_localisation", {}).get("query_list", []):
                    for qa_dict in q.get("query_list", []):
                        continue

                if "summarisation" in JSON["tasks"]:
                    for qa_dict in JSON["tasks"]["summarisation"].get("individual_sum", []):
                        continue
                    for qa_dict in JSON["tasks"]["summarisation"].get("multi_video_sum", []):
                        continue
                    for qa_dict in JSON["tasks"]["summarisation"].get("holistic_sum", []):
                        continue
                
                for qa_dict in JSON["tasks"].get("counting", []):
                    continue
                
                qa_dict = JSON["tasks"].get("summary_ordering", {})
            except Exception as e:
                #print(traceback.format_exc())
                print(f"Error loading {JSON_FILE} in XLeBench: {e}")
                #raise e

        return bench

    @classmethod
    def asAuto(cls, name, **kwargs):
        from . import BENCH_BASE, BENCH_CONFIGS
        if name in BENCH_CONFIGS:
            return BENCH_CONFIGS[name]["loader"](BENCH_CONFIGS[name]["path"], **kwargs)
        else:
            raise ValueError(f"No benchmark configuration found for name: {name}")
    
    # New helper to reorder Videos by number of QAs per video.
    def sort_videos_by_qa_count(self, reverse=False):
        """
        Sort self.Videos (a dict) by the length of each Video's QAs list.
        After calling this, iteration like `for k, v in self.Videos.items():`
        will yield items in the sorted order (Python 3.7+ preserves insertion order).
        Set reverse=True to get descending order (most QAs first).
        """
        self.Videos = dict(sorted(self.Videos.items(), key=lambda kv: len(kv[1].QAs), reverse=reverse))

    def create_qa(self, max_videos=-1, max_qa=-1):
        #(1) sort by video, firstly process videos with more QAs
        self.sort_videos_by_qa_count(reverse=True)
        #(2) insert these qas in to self.qas
        self.qas = []
        count = 0
        for video in self.Videos.values():
            for qa in video.QAs:
                self.qas.append(qa)
            count +=1
            if (max_videos>0 and count>=max_videos) or (max_qa>0 and len(self.qas)>=max_qa):
                break