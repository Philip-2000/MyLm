import json,os
from os.path import join as opj
DEFAULT_EXPERIENCE_START_BASE = 8*3600  # 8 AM in seconds

class Video:
    def __init__(self, path, video_id, bench_object):
        self.path = path
        self.video_id = video_id
        self.bench_object = bench_object
        self._video = None
        self.QAs = []
    
    def __repr__(self):
        return f"Video (video_id={self.video_id}, path={self.path}, num_QAs={len(self.QAs)})\n" + "\n".join([f"\t{qa.__repr__()}" for qa in self.QAs])

    @property
    def video(self): #lazy load video
        if self._video is None:
            import av
            self._video = av.open(self.path)
        return self._video
    
    def append_qa(self, qa):
        self.QAs.append(qa)
        qa.video_key = self.video_id
    
    @property
    def duration(self):
        import av
        return self.video.duration / av.time_base

    @property
    def bench_name(self):
        return self.bench_object.name

    @property
    def experience_name(self):
        return f"{self.bench_name}_{self.video_id.replace('/', '_')}"

    @property
    def experience(self):
        return {
            "name": self.experience_name,
            "start_s": 0.0,
            "duration_s": self.duration,
            "activities": [
                {
                    "name": self.video_id,
                    "source": self.bench_name,
                    "VIDEOS": [
                        {
                            "video_path": self.path,
                            "TIMESPAN": {
                            "STARTSTAMP": {
                                "seconds_natural_s": DEFAULT_EXPERIENCE_START_BASE,
                                "seconds_experience_s": 0,
                                "seconds_activity_s": 0,
                                "seconds_video_s": 0
                            },
                            "ENDSTAMP": {
                                "seconds_natural_s": DEFAULT_EXPERIENCE_START_BASE + self.duration,
                                "seconds_experience_s": self.duration,
                                "seconds_activity_s": self.duration,
                                "seconds_video_s": self.duration
                            }
                            },
                            "clip_id": ""
                        }
                    ],
                    "ANNOS": {},
                    "TIMESPAN": {
                        "STARTSTAMP": {
                            "seconds_natural_s": DEFAULT_EXPERIENCE_START_BASE,
                            "seconds_experience_s": 0,
                            "seconds_activity_s": 0,
                            "seconds_video_s": 0
                        },
                        "ENDSTAMP": {
                            "seconds_natural_s": DEFAULT_EXPERIENCE_START_BASE + self.duration,
                            "seconds_experience_s": self.duration,
                            "seconds_activity_s": self.duration,
                            "seconds_video_s": self.duration
                        }
                    }
                }
            ]
        }

    @property
    def execution(self):
        return {
            "name": "benches",
            "experience": self.experience_name,
            "questions": [
                {
                    "TIME": {
                        "seconds_natural_s": DEFAULT_EXPERIENCE_START_BASE + self.duration,
                        "seconds_experience_s": self.duration,
                        "seconds_activity_s": None,
                        "seconds_video_s": None
                    },
                    "question": qa.question,
                    "ref_time": {
                        "STARTSTAMP": {
                            "seconds_natural_s": DEFAULT_EXPERIENCE_START_BASE + self.duration - 0.1,
                            "seconds_experience_s": self.duration-0.1,
                            "seconds_activity_s": self.duration-0.1,
                            "seconds_video_s": self.duration-0.1
                        },
                        "ENDSTAMP": {
                            "seconds_natural_s": DEFAULT_EXPERIENCE_START_BASE + self.duration,
                            "seconds_experience_s": self.duration,
                            "seconds_activity_s": self.duration,
                            "seconds_video_s": self.duration
                        }
                    },
                    "answer": qa.answer,
                    "response": None,
                    "score": None,
                    "choices": None
                } for qa in self.QAs
            ]
        }

    def save_experience(self):
        from EgoCL.paths import EPRC_ROOT
        exp_path = opj(EPRC_ROOT, f"{self.experience_name}.json")
        with open(exp_path, "w") as f:
            json.dump(self.experience, f, indent=4)
        
    def save_execution(self):
        from EgoCL.paths import EXPERIMENT_ROOT
        exec_path = opj(EXPERIMENT_ROOT, "benches", self.experience_name, "execution.json")
        os.makedirs(os.path.dirname(exec_path), exist_ok=True)
        with open(exec_path, "w") as f:
            json.dump(self.execution, f, indent=4)

    def save_ee(self):
        self.save_experience()
        self.save_execution()

class VideoEgoLife(Video):
    def __init__(self, path, video_id, bench_object, N=64, create=False):
        self.dir = path
        self.N = N
        self.create = create

        self.video_id = video_id
        self.TSS = self.idt2tss(identity=self.identity, date=self.date, time_str=self.time_str)

        super().__init__(path, video_id, bench_object)
        self.path=self.video_path
        #if self.create or not os.path.exists(self.path): self.toVideo()

    @property
    def video(self): #lazy load video
        import os
        if self._video is not None: return self._video
        if self.create or not os.path.exists(self.path): self.toVideo()
        import av
        self._video = av.open(self.path)
        return self._video
        
    @property
    def identity(self):
        return self.video_id.split("_")[1]+"_"+self.video_id.split("_")[2]
    
    @property
    def date(self):
        return self.video_id.split("_")[0]
    
    @property
    def time_str(self):
        return self.video_id.split("_")[3]

    @property
    def video_name(self):
        return self.video_id

    @property
    def duration(self):
        return self.TSS.duration

    @property
    def cache_dir(self):
        from . import CONCAT_VIDEO_CACHE
        return opj(CONCAT_VIDEO_CACHE, self.bench_name)
    
    @property
    def video_path(self):
        return opj(self.cache_dir, self.video_name+'.mp4')

    def timemapping(self, identity):
        import json, os
        from . import EGOLIFE_TSS_FULL, EGOLIFE_MAP_JSON
        if EGOLIFE_TSS_FULL[identity] is not None: return EGOLIFE_TSS_FULL[identity]
        if EGOLIFE_MAP_JSON is None: EGOLIFE_MAP_JSON = json.load(open(os.path.join(os.path.dirname(__file__),"egolife_map.json"), "r"))
        content = [c for c in EGOLIFE_MAP_JSON['content'] if c['meta']['name']==identity][0]
        from .TS import TSS, TS
        THE_TSS, continuous_second = TSS(), 0
        for segment in content['content']:
            for video in segment['content']:
                # "/mnt/data/raw_data/EgoLife/A1_JAKE/DAY1/DAY1_A1_JAKE_11094208.mp4"
                THE_TS = TS(THE_TSS, Natural_Time=video["video_path"].split("/")[-1].split(".")[0], Continuous_Time=continuous_second, Video_path=video["video_path"], Video_Time=0.0)
                THE_TSS += THE_TS
                continuous_second += video["duration_seconds"]
                
            THE_TS = TS(THE_TSS, Natural_Time=None, Continuous_Time=continuous_second, Video_path=None, Video_Time=None)
            THE_TS.fill(THE_TSS[-1])
            THE_TSS += THE_TS
        EGOLIFE_TSS_FULL[identity] = THE_TSS
        THE_TSS.subject = identity
        return THE_TSS
    
    def idt2tss(self, identity, date, time_str):
        THE_TSS = self.timemapping(identity)
        return THE_TSS.clip(f"{date}_{identity}_{time_str}")

    def ts2frame(self, THE_TS):
        from decord import VideoReader, cpu
        vr = VideoReader(THE_TS.VIDEO_PATH, ctx=cpu(0), num_threads=1)
        f = vr[int(float(vr.get_avg_fps()) * THE_TS.video_second)]
        return f

    def toVideo(self): #print(len(self.TSS))
        seconds = self.TSS.segments(self.N)
        frames = [self.ts2frame(ts) for ts in seconds]
        import av, os, numpy as np
        os.makedirs(os.path.dirname(self.video_path), exist_ok=True)
        container = av.open(self.video_path, mode="w")
        stream = container.add_stream("libx264", rate=2)

        # determine size from first frame
        first = frames[0]
        try:
            first = first.asnumpy()
        except Exception:
            first = first
        first = np.asarray(first)
        if first.ndim == 2:
            first = np.stack([first, first, first], axis=-1)
        if first.shape[2] == 4:
            first = first[..., :3]

        h, w = first.shape[0], first.shape[1]
        stream.width = w
        stream.height = h
        stream.pix_fmt = "yuv420p"

        for img in frames:
            try:
                arr = img.asnumpy()
            except Exception:
                arr = img
            arr = np.asarray(arr)
            if arr.ndim == 2:
                arr = np.stack([arr, arr, arr], axis=-1)
            if arr.shape[2] == 4:
                arr = arr[..., :3]

            vframe = av.VideoFrame.from_ndarray(arr, format="rgb24")
            for packet in stream.encode(vframe):
                container.mux(packet)

        # flush encoder
        for packet in stream.encode():
            container.mux(packet)
        container.close()

    @property
    def experience(self):
        from copy import deepcopy as dopy
        JSON = {
            "name": self.experience_name,
            "start_s": 0.0,
            "duration_s": self.duration,
            "activities": []
        }


        TEMPLATE_ACTIVITY = {
            "name": None,
            "source": self.bench_name,
            "VIDEOS": [],
            "ANNOS": {},
            "TIMESPAN": {
                "STARTSTAMP": {},
                "ENDSTAMP": {}
            }
        }

        TEMPLATE_VIDEO = {
            "video_path": self.path,
            "TIMESPAN": {
                "STARTSTAMP": {},
                "ENDSTAMP": {}
            },
            "clip_id": ""
        }

        CURR_ACT = None
        CURR_ACT_ID = 0
        CURR_VIDEO = None

        for i, CURR_TS in enumerate(self.TSS):
            
            if CURR_ACT is None and CURR_TS.video_second == 0.0:
                # start new activity and video
                CURR_ACT = dopy(TEMPLATE_ACTIVITY)
                CURR_ACT["name"] = f"act{CURR_ACT_ID}"
                CURR_ACT["TIMESPAN"]["STARTSTAMP"] = {
                    "seconds_natural_s": CURR_TS.natural_second,
                    "seconds_experience_s": CURR_TS.continuous_second,
                    "seconds_activity_s": 0.0,
                    "seconds_video_s": CURR_TS.video_second
                }
                CURR_VIDEO = dopy(TEMPLATE_VIDEO)
                CURR_VIDEO["video_path"] = CURR_TS.VIDEO_PATH
                CURR_ACT_SECOND = 0.0
                CURR_VIDEO["TIMESPAN"]["STARTSTAMP"] = {
                    "seconds_natural_s": CURR_TS.natural_second,
                    "seconds_experience_s": CURR_TS.continuous_second,
                    "seconds_activity_s": CURR_ACT_SECOND,
                    "seconds_video_s": CURR_TS.video_second
                }

            elif CURR_TS.video_second == 0.0:
                LAST_TS = self.TSS[i-1]
                CURR_ACT_SECOND += CURR_TS.continuous_second - LAST_TS.continuous_second
                # close last video
                CURR_VIDEO["TIMESPAN"]["ENDSTAMP"] = {
                    "seconds_natural_s": CURR_TS.natural_second,
                    "seconds_experience_s": CURR_TS.continuous_second,
                    "seconds_activity_s": CURR_ACT_SECOND,
                    "seconds_video_s": CURR_VIDEO["TIMESPAN"]["STARTSTAMP"]["seconds_video_s"] + (CURR_TS.continuous_second - LAST_TS.continuous_second)
                }
                CURR_ACT["VIDEOS"].append(dopy(CURR_VIDEO))
                # start new video
                CURR_VIDEO = dopy(TEMPLATE_VIDEO)
                CURR_VIDEO["video_path"] = CURR_TS.VIDEO_PATH
                CURR_VIDEO["TIMESPAN"]["STARTSTAMP"] = {
                    "seconds_natural_s": CURR_TS.natural_second,
                    "seconds_experience_s": CURR_TS.continuous_second,
                    "seconds_activity_s": CURR_ACT_SECOND,
                    "seconds_video_s": CURR_TS.video_second
                }
            else:
                LAST_TS = self.TSS[i-1]
                CURR_ACT_SECOND += CURR_TS.continuous_second - LAST_TS.continuous_second
                # close last video
                CURR_VIDEO["TIMESPAN"]["ENDSTAMP"] = {
                    "seconds_natural_s": CURR_TS.natural_second,
                    "seconds_experience_s": CURR_TS.continuous_second,
                    "seconds_activity_s": CURR_ACT_SECOND,
                    "seconds_video_s": CURR_TS.video_second
                }
                CURR_ACT["VIDEOS"].append(dopy(CURR_VIDEO))
                #close current activity
                CURR_ACT["TIMESPAN"]["ENDSTAMP"] = {
                    "seconds_natural_s": CURR_TS.natural_second,
                    "seconds_experience_s": CURR_TS.continuous_second,
                    "seconds_activity_s": CURR_ACT_SECOND,
                    "seconds_video_s": CURR_TS.video_second
                }
                JSON["activities"].append(dopy(CURR_ACT))
                #disable the current activity and video
                CURR_ACT_ID += 1
                CURR_ACT = None
                CURR_VIDEO = None
        return JSON

    @property
    def execution(self):
        JSON = {
            "name": "benches",
            "experience": self.experience_name,
            "questions": []
        }
        from .TS import TS
        for qa in self.QAs:
            QUERY_TS, REFSTART_TS, REFEND_TS = self.TSS(qa.query_time, domain="natural"), self.TSS(qa.ref_time["start"], domain="natural"), self.TSS(qa.ref_time["end"], domain="natural")
            qa_json = {
                        "TIME": {
                            "seconds_natural_s": QUERY_TS.natural_second,
                            "seconds_experience_s": QUERY_TS.continuous_second,
                            "seconds_activity_s": None, #this is too hard to compute, and I think this may not be used in the future, so set to None
                            "seconds_video_s": QUERY_TS.video_second
                        },
                        "question": qa.question,
                        "ref_time": {
                            "STARTSTAMP": {
                                "seconds_natural_s": REFSTART_TS.natural_second,
                                "seconds_experience_s": REFSTART_TS.continuous_second,
                                "seconds_activity_s": None, # as above
                                "seconds_video_s": REFSTART_TS.video_second
                            },
                            "ENDSTAMP": {
                                "seconds_natural_s": REFEND_TS.natural_second,
                                "seconds_experience_s": REFEND_TS.continuous_second,
                                "seconds_activity_s": None, # as above
                                "seconds_video_s": REFEND_TS.video_second
                            }
                        },
                        "answer": qa.answer,
                        "response": None,
                        "score": None,
                        "choices": None
                    }
            JSON["questions"].append(qa_json)
        return JSON

    def save_experience(self):
        from EgoCL.paths import EPRC_ROOT
        exp_path = opj(EPRC_ROOT, f"{self.experience_name}.json")
        print("exp_path", exp_path)
        with open(exp_path, "w") as f:
            json.dump(self.experience, f, indent=4)
        
    def save_execution(self):
        from EgoCL.paths import EXPERIMENT_ROOT
        exec_path = opj(EXPERIMENT_ROOT, "benches", self.experience_name, "execution.json")
        print("exec_path", exec_path)
        os.makedirs(os.path.dirname(exec_path), exist_ok=True)
        with open(exec_path, "w") as f:
            json.dump(self.execution, f, indent=4)

    def save_ee(self):
        self.save_experience()
        self.save_execution()

class VideoXLeBench(Video):
    def __init__(self, path, video_id, bench_object, SIM, N=64, create=False):
        
        self.TSS = self.sim2tss(SIM)
        self.N = N
        self.create = create
        super().__init__(path, video_id, bench_object)
        self.path=self.video_path
        #if self.create or not os.path.exists(self.path): self.toVideo()

    @property
    def video(self): #lazy load video
        import os
        if self._video is not None: return self._video
        if self.create or not os.path.exists(self.path): self.toVideo()
        import av
        self._video = av.open(self.path)
        return self._video
    
    @property
    def video_name(self):
        return self.video_id

    @property
    def cache_dir(self):
        from . import CONCAT_VIDEO_CACHE
        return opj(CONCAT_VIDEO_CACHE, self.bench_name)
    
    @property
    def video_path(self):
        return opj(self.cache_dir, self.video_name+'.mp4')
    
    @property
    def duration(self):
        return self.TSS.duration_seconds
    
    @property
    def experience_name(self):
        return (f"{self.bench_name}_{self.video_id.replace('/', '_')}")[:-len((f"{self.bench_name}_{self.video_id.replace('/', '_')}").split("_")[-1])-1]
    
    def sim2tss(self, SIM):
        """
        SIM = [
            {
                "video_uid": "869a2290-5509-49d0-8cc6-e0a0230790d3",
                "start_time": "07:00",
                "end_time": "07:59"
            },
            {
                "video_uid": "046855d7-41d7-4f41-a6a7-fce921ea8133",
                "start_time": "09:05",
                "end_time": "09:12"
            },
            {
                "video_uid": "66c507b5-211d-4955-a722-704440ddf751",
                "start_time": "09:50",
                "end_time": "10:17"
            },
            {
                "video_uid": "1246d6ec-5620-4f71-8b4b-d823775f58c2",
                "start_time": "11:35",
                "end_time": "12:05"
            },
            {
                "video_uid": "2fd1837a-613b-48af-9ad2-0222f8fd6b69",
                "start_time": "12:10",
                "end_time": "12:44"
            },
            {
                "video_uid": "56504e4e-a228-4b28-baa4-1ce2de03c2d4",
                "start_time": "12:49",
                "end_time": "13:30"
            },
            {
                "video_uid": "d29b209e-cbc7-40a7-a0d6-acf803b86c78",
                "start_time": "19:05",
                "end_time": "19:13"
            },
            {
                "video_uid": "4dab2e2a-6f27-4c5f-ae51-c39613e0d62c",
                "start_time": "20:05",
                "end_time": "20:47"
            },
            {
                "video_uid": "cf90f24b-32de-452a-b154-03ca5e47099a",
                "start_time": "22:05",
                "end_time": "22:14"
            }
        ]
        """
        from .TS import TSS, TS
        from . import EGO4D_VIDEO_BASE, XLEN_LEN_JSON
        if XLEN_LEN_JSON is None: XLEN_LEN_JSON = json.load(open(opj(os.path.dirname(__file__),"xlen_len.json"), "r"))
        THE_TSS, continuous_second = TSS(), 0
        for item in SIM: 
            THE_TS = TS(THE_TSS,
                Natural_Time=f"01:{item['start_time']}:00" if int(item['start_time'][0:2]) > 2 else f"02:{item['start_time']}:00",
                Continuous_Time=continuous_second,
                Video_path=opj(EGO4D_VIDEO_BASE, f"{item['video_uid']}.mp4"),
                Video_Time=0.0)
            THE_TSS += THE_TS
            continuous_second += self.hhmmss2second(XLEN_LEN_JSON[item['video_uid']])

            NXT_TS = TS(THE_TSS, Natural_Time=None, Continuous_Time=continuous_second, Video_path=None, Video_Time=None)
            NXT_TS.fill(THE_TSS[-1])
            THE_TSS += NXT_TS
        
        return THE_TSS
    
    def hhmmss2second(self, hhmmss):
        hh = int(hhmmss[0:2])
        mm = int(hhmmss[3:5])
        ss = float(hhmmss[6:])
        return hh*3600 + mm*60 + ss

    def ts2frame(self, THE_TS):
        from decord import VideoReader, cpu
        vr = VideoReader(THE_TS.VIDEO_PATH, ctx=cpu(0), num_threads=1)
        f = vr[int(float(vr.get_avg_fps()) * THE_TS.video_second)]
        return f

    def toVideo(self): #print(len(self.TSS))
        seconds = self.TSS.segments(self.N)
        frames = [self.ts2frame(ts) for ts in seconds]
        import av, os, numpy as np
        os.makedirs(os.path.dirname(self.video_path), exist_ok=True)
        container = av.open(self.video_path, mode="w")
        stream = container.add_stream("libx264", rate=2)

        # determine size from first frame
        first = frames[0]
        try:
            first = first.asnumpy()
        except Exception:
            first = first
        first = np.asarray(first)
        if first.ndim == 2:
            first = np.stack([first, first, first], axis=-1)
        if first.shape[2] == 4:
            first = first[..., :3]

        h, w = first.shape[0], first.shape[1]
        stream.width = w
        stream.height = h
        stream.pix_fmt = "yuv420p"

        for img in frames:
            try:
                arr = img.asnumpy()
            except Exception:
                arr = img
            arr = np.asarray(arr)
            if arr.ndim == 2:
                arr = np.stack([arr, arr, arr], axis=-1)
            if arr.shape[2] == 4:
                arr = arr[..., :3]

            vframe = av.VideoFrame.from_ndarray(arr, format="rgb24")
            for packet in stream.encode(vframe):
                container.mux(packet)

        # flush encoder
        for packet in stream.encode():
            container.mux(packet)
        container.close()

    @property
    def experience(self):
        JSON = {
            "name": self.experience_name,
            "start_s": 0.0,
            "duration_s": self.duration,
            "activities": []
        }
        assert len(self.TSS)%2==0, "TSS length should be even."
        for i in range(0, len(self.TSS), 2):
            START_TS = self.TSS[i]
            END_TS = self.TSS[i+1]
            ACTIVITY = {
                "name": f"act{i//2}",
                "source": self.bench_name,
                "VIDEOS": [
                    {
                        "video_path": START_TS.VIDEO_PATH,
                        "TIMESPAN": {
                            "STARTSTAMP": {
                                "seconds_natural_s": START_TS.natural_second,
                                "seconds_experience_s": START_TS.continuous_second,
                                "seconds_activity_s": 0.0,
                                "seconds_video_s": START_TS.video_second
                            },
                            "ENDSTAMP": {
                                "seconds_natural_s": END_TS.natural_second,
                                "seconds_experience_s": END_TS.continuous_second,
                                "seconds_activity_s": END_TS.continuous_second - START_TS.continuous_second,
                                "seconds_video_s": END_TS.video_second
                            }
                        },
                        "clip_id": ""
                    }
                ],
                "ANNOS": {},
                "TIMESPAN": {
                    "STARTSTAMP": {
                        "seconds_natural_s": START_TS.natural_second,
                        "seconds_experience_s": START_TS.continuous_second,
                        "seconds_activity_s": 0.0,
                        "seconds_video_s": START_TS.video_second
                    },
                    "ENDSTAMP": {
                        "seconds_natural_s": END_TS.natural_second,
                        "seconds_experience_s": END_TS.continuous_second,
                        "seconds_activity_s": END_TS.continuous_second - START_TS.continuous_second,
                        "seconds_video_s": END_TS.video_second
                    }
                }
            }
            JSON["activities"].append(ACTIVITY)
        return JSON

    @property
    def execution(self):
        JSON = {
            "name": "benches",
            "experience": self.experience_name,
            "questions": []
        }
        from .TS import TS
        for qa in self.QAs:
            QUERY_TS, REFSTART_TS, REFEND_TS = self.TSS(qa.query_time, domain="continuous"), self.TSS(qa.ref_time["start"], domain="natural"), self.TSS(qa.ref_time["end"], domain="natural")
            qa_json = {
                        "TIME": {
                            "seconds_natural_s": QUERY_TS.natural_second,
                            "seconds_experience_s": QUERY_TS.continuous_second,
                            "seconds_activity_s": None, #this is too hard to compute, and I think this may not be used in the future, so set to None
                            "seconds_video_s": QUERY_TS.video_second
                        },
                        "question": qa.question,
                        "ref_time": {
                            "STARTSTAMP": {
                                "seconds_natural_s": REFSTART_TS.natural_second,
                                "seconds_experience_s": REFSTART_TS.continuous_second,
                                "seconds_activity_s": None, # as above
                                "seconds_video_s": REFSTART_TS.video_second
                            },
                            "ENDSTAMP": {
                                "seconds_natural_s": REFEND_TS.natural_second,
                                "seconds_experience_s": REFEND_TS.continuous_second,
                                "seconds_activity_s": None, # as above
                                "seconds_video_s": REFEND_TS.video_second
                            }
                        },
                        "answer": qa.answer,
                        "response": None,
                        "score": None,
                        "choices": None
                    }
            JSON["questions"].append(qa_json)
        return JSON

    def save_experience(self):
        from EgoCL.paths import EPRC_ROOT
        exp_path = opj(EPRC_ROOT, f"{self.experience_name}.json") #print("exp_path", exp_path)
        with open(exp_path, "w") as f:
            json.dump(self.experience, f, indent=4)
        
    def save_execution(self):
        from EgoCL.paths import EXPERIMENT_ROOT
        exec_path = opj(EXPERIMENT_ROOT, "benches", self.experience_name, "execution.json") #print("exec_path", exec_path)
        os.makedirs(os.path.dirname(exec_path), exist_ok=True)
        with open(exec_path, "w") as f:
            json.dump(self.execution, f, indent=4)

    def save_ee(self):
        self.save_experience()
        self.save_execution()