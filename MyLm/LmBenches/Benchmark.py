from .QA import QA
from .Video import Video

class Benchmark:
    def __init__(self, name=""):
        self.name = name
        self.Videos = {}
        self.QAs = []
        self.qas = [] # the real QAs to run in current test

    def test(self, model):
        self.run(model)
        return self.compare()
    
    def __len__(self):
        return len(self.QAs)
    
    def __getitem__(self, index):
        return self.QAs[index]
    
    def run(self, model, **kwargs):
        self.qas = self.QAs[:kwargs["max_qa"] if kwargs.get("max_qa", -1) > 0 else len(self.QAs)] if kwargs.get("key", None) is None else [qa for qa in self.QAs if qa.uid in kwargs["key"]]
        for qa in self.qas:
            r,c = qa.run(model, **kwargs)
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
    
    def save_ee(self):
        from tqdm import tqdm
        for video in tqdm(self.Videos.values(), desc="Saving Experience and Execution"):
            try:
                video.save_ee()
            except Exception as e:
                print(f"Error saving EE for video {video.video_id}: {e}")

    @classmethod
    def asLongVideoBench(cls, path):
        bench = cls("LongVideoBench")
        import json, os
        JSON_PATH = os.path.join(path, "longvideobench.json")
        VIDEO_BASE = os.path.join(path, "videos")
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            for qa_dict in data:
                video_key = qa_dict["problem_id"][:qa_dict["problem_id"].rfind("_")] #  this will change 86CxyhFV9MI_0 to 86CxyhFV9MI
                if video_key == "4QSmRYQBfN4":
                    continue
                if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=os.path.join(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
                
                qa_object = QA.asLongVideoBench(qa_dict, bench)
                bench.QAs.append(qa_object)
                bench.Videos[video_key].QAs.append(qa_object)
                
        bench.QAs = sorted(bench.QAs, key=lambda x: x.video_key) # Sort QAs by video_key, so the qa with same video are together, for better caching
        return bench
    
    @classmethod
    def asLVBench(cls, path):
        bench = cls("LVBench")
        import json, os
        JSON_PATH = os.path.join(path, "video_info.meta.jsonl")
        VIDEO_BASE = os.path.join(path, "all_videos")
        with open(JSON_PATH, "r") as f:
            
            for line in f:
                video_dict = json.loads(line)
            
                video_key = video_dict["key"]
                if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=os.path.join(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
                for qa_dict in video_dict.get("qa", []):
                    qa_object = QA.asLVBench({"video_key": video_key, **qa_dict}, bench)
                    bench.QAs.append(qa_object)
                    bench.Videos[video_key].QAs.append(qa_object)
                
        bench.QAs = sorted(bench.QAs, key=lambda x: x.video_key) # Sort QAs by video_key, so the qa with same video are together, for better caching
        return bench
    
    @classmethod
    def asLongTimeScope(cls, path):
        bench = cls("LongTimeScope")
        import json, os
        JSON_PATH = os.path.join(path, "data/LongTimeScope.json")
        VIDEO_BASE = os.path.join(path, "videos_split_2")
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            for qa_dict in data:
                video_key = qa_dict["problem_id"]
                if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=os.path.join(VIDEO_BASE, f"videos_{video_key[:video_key.rfind('_')]}/{video_key[video_key.rfind('_')+1:]}.mp4"), bench_object=bench ) #"OCR_36000_0" -> videos_OCR_36000/0.mp4
                qa_object = QA.asLongTimeScope(qa_dict, bench)
                bench.QAs.append(qa_object)
                bench.Videos[video_key].QAs.append(qa_object)
                
        bench.QAs = sorted(bench.QAs, key=lambda x: x.video_key) # Sort QAs by video_key, so the qa with same video are together, for better caching
        
        return bench
    
    @classmethod
    def asMLVU(cls, path):
        bench = cls("MLVU")
        import json, os
        JSON_PATH = os.path.join(path, "mlvu.json")
        VIDEO_BASE = os.path.join(path, "video")
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            for qa_dict in data:
                video_key = qa_dict["video"][:-4]
                if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=os.path.join(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
                qa_object = QA.asMLVU(qa_dict, bench)
                bench.QAs.append(qa_object)
                bench.Videos[video_key].QAs.append(qa_object)
                
        bench.QAs = sorted(bench.QAs, key=lambda x: x.video_key) # Sort QAs by video_key, so the qa with same video are together, for better caching
        
        return bench
    
    @classmethod
    def asVideo_MME(cls, path):
        bench = cls("Video_MME")
        path = path.replace("Video_MME","Video-MME")
        import json, os
        JSON_PATH = os.path.join(path, "videomme.json")
        VIDEO_BASE = os.path.join(path, "mme_videos")
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            for qa_dict in data:
                video_key = qa_dict["problem_id"]
                if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=os.path.join(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
                
                qa_object = QA.asVideo_MME(qa_dict, bench)
                bench.QAs.append(qa_object)
                bench.Videos[video_key].QAs.append(qa_object)
        return bench

    @classmethod
    def asegoschema(cls, path):
        bench = cls("egoschema")
        import json, os
        JSON_PATH = os.path.join(path, "merged.json")
        VIDEO_BASE = os.path.join(path, "videos")
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            for qa_dict in data:
                video_key = qa_dict["q_uid"]
                if video_key not in bench.Videos: bench.Videos[video_key] = Video(video_id=video_key,path=os.path.join(VIDEO_BASE, f"{video_key}.mp4"), bench_object=bench ) #this object uses lazy loading, so it won't load video's content now
                
                qa_object = QA.asegoschema(qa_dict, bench)
                bench.QAs.append(qa_object)
                bench.Videos[video_key].QAs.append(qa_object)
        return bench

    @classmethod
    def asAuto(cls, name):
        import os
        from . import BENCH_BASE
        filename = os.path.basename(name).replace("-", "_")
        method_name = f"as{filename}"
        if hasattr(cls, method_name):
            method = getattr(cls, method_name)
            return method(os.path.join(BENCH_BASE, name))
        else:
            raise ValueError(f"No benchmark method found for filename: {filename}")
