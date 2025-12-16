class Video:
    def __init__(self, path, video_id, bench_object):
        self.path = path
        self.video_id = video_id
        self.bench_object = bench_object
        self._video = None
        self.QAs = []
    
    @property
    def video(self): #lazy load video
        if self._video is None:
            import av
            self._video = av.open(self.path)
        return self._video
    
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
                    "VIDEO": {
                        "video_path": self.path,
                        "TIMESPAN": {
                        "STARTSTAMP": {
                            "seconds_experience_s": 0,
                            "seconds_activity_s": 0,
                            "seconds_video_s": 0
                        },
                        "ENDSTAMP": {
                            "seconds_experience_s": self.duration,
                            "seconds_activity_s": self.duration,
                            "seconds_video_s": self.duration
                        }
                        },
                        "clip_id": ""
                    },
                    "ANNOS": {},
                    "TIMESPAN": {
                        "STARTSTAMP": {
                            "seconds_experience_s": 0,
                            "seconds_activity_s": 0,
                            "seconds_video_s": 0
                        },
                        "ENDSTAMP": {
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
                        "seconds_experience_s": self.duration,
                        "seconds_activity_s": None,
                        "seconds_video_s": None
                    },
                    "question": qa.question,
                    "ref_time": {
                        "STARTSTAMP": {
                            "seconds_experience_s": self.duration-0.1,
                            "seconds_activity_s": self.duration-0.1,
                            "seconds_video_s": self.duration-0.1
                        },
                        "ENDSTAMP": {
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
        import os, json
        exp_path = os.path.join(EPRC_ROOT, f"{self.experience_name}.json")
        with open(exp_path, "w") as f:
            json.dump(self.experience, f, indent=4)
        
    
    def save_execution(self):
        from EgoCL.paths import EXPERIMENT_ROOT
        import os, json
        exec_path = os.path.join(EXPERIMENT_ROOT, "benches", self.experience_name, "execution.json")
        os.makedirs(os.path.dirname(exec_path), exist_ok=True)
        with open(exec_path, "w") as f:
            json.dump(self.execution, f, indent=4)

    def save_ee(self):
        self.save_experience()
        self.save_execution()