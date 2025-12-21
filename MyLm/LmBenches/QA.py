
class QA:
    def __init__(self, question="", options=[], answer="", video_key="", uid="None", bench_object=None, **kwargs):
        self.uid = uid
        self.question = question
        self.options = options
        self.answer = answer
        self.video_key = video_key
        self.bench_object = bench_object
        self.result = ""

        from .TS import TS
        from .Video import DEFAULT_EXPERIENCE_START_BASE
        self.query_time = kwargs.get("query_time", None)
        if self.query_time is None:
            dur = self.bench_object.Videos[self.video_key].duration if self.bench_object and self.video_key in self.bench_object.Videos else 0
            self.query_time = TS(None, Natural_Time=DEFAULT_EXPERIENCE_START_BASE+dur, Continuous_Time=dur, Video_path=self.bench_object.Videos[self.video_key].path if self.bench_object and self.video_key in self.bench_object.Videos else None, Video_Time=dur)
        
        self.ref_start = kwargs.get("ref_start", None)
        if self.ref_start is None:
            dur = 0
            self.ref_start = TS(None, Natural_Time=DEFAULT_EXPERIENCE_START_BASE+dur, Continuous_Time=dur, Video_path=self.bench_object.Videos[self.video_key].path if self.bench_object and self.video_key in self.bench_object.Videos else None, Video_Time=dur)
        
        self.ref_end = kwargs.get("ref_end", None)
        if self.ref_end is None:
            dur = self.bench_object.Videos[self.video_key].duration if self.bench_object and self.video_key in self.bench_object.Videos else 0
            self.ref_end = TS(None, Natural_Time=DEFAULT_EXPERIENCE_START_BASE+dur, Continuous_Time=dur, Video_path=self.bench_object.Videos[self.video_key].path if self.bench_object and self.video_key in self.bench_object.Videos else None, Video_Time=dur)
        
        self._compare = None

    @property
    def query(self):
        return self.question + (" Options: " + " ".join([chr(65+i) + ". " + str(option) for i, option in enumerate(self.options)]) if self.options else "")

    def __repr__(self):
        return f"QA (uid={self.uid}, video_key={self.video_key}, question={self.question}, options={self.options}, answer={self.answer}, query_time={self.query_time}, ref_time={self.ref_time})"

    @property
    def prompt(self):
        return f"IMPORTANT: You MUST answer based ONLY on the content of the video.\n Video ID: {self.video_key}\nQuestion: {self.query}\n【Strict Instructions】1. Answer ONLY with the single option letter (e.g., A/B/C/D/E/F) that matches the correct answer.2. Do NOT add any extra explanation, video details, reasoning, or irrelevant text.Answer:"
        #return f"Video ID: {self.video_key}\nQuestion: {self.question}\nAnswer:"
        
    def run(self, model, **kwargs):
        from .. import call
        self.result = call(model, {"content": [{"text": self.prompt}, {"video":self.video_path}], **kwargs} )
        return self.result, self.compare(self.result)
    
    def evaluate(self, function, **kwargs):
        self.result = function(self, **kwargs)
        return self.result, self.compare(self.result)

    @property
    def record(self):
        return {"result": self.result, "correct": self._compare}
        
    @property
    def video_path(self):
        return self.bench_object.Videos[self.video_key].path

    def compare(self, generated_answer=""):
        if self._compare is None:
            ans = generated_answer if generated_answer else self.result
            sol_letter = ans[8] if len(ans) >= 10 and ans.startswith("<answer>") and ans.endswith("</answer>") else ans[0]
            self._compare = (sol_letter.strip().lower() == self.answer.strip().lower())
        return self._compare

    @property
    def to_dict(self):
        return {
            "uid": self.uid,
            "video_key": self.video_key,
            "question": self.question,
            "options": self.options,
            "answer": self.answer,
            "result": self.result,
            "correct": self._compare,
            "query_time": self.query_time,
            "ref_time": self.ref_time,
        }
    
    @property
    def execution(self):
        return {
            "TIME": {
                "seconds_natural_s": self.query_time.natural_second,
                "seconds_experience_s": self.query_time.continuous_second,
                "seconds_activity_s": None,
                "seconds_video_s": self.query_time.video_second
            },
            "question": self.question,
            "ref_time": {
                "STARTSTAMP": {
                    "seconds_natural_s": self.ref_start.natural_second,
                    "seconds_experience_s": self.ref_start.continuous_second,
                    "seconds_activity_s": None,
                    "seconds_video_s": self.ref_start.video_second
                },
                "ENDSTAMP": {
                    "seconds_natural_s": self.ref_end.natural_second,
                    "seconds_experience_s": self.ref_end.continuous_second,
                    "seconds_activity_s": None,
                    "seconds_video_s": self.ref_end.video_second
                }
            },
            "answer": self.answer,
            "response": None,
            "score": None,
            "choices": self.options
        }

    @property
    def source(self):
        return self.bench_object.name if self.bench_object else "Unknown"

    @classmethod
    def asLongVideoBench(cls, qa_dict, bench_object):
        """
        {
            "problem_id": "86CxyhFV9MI_0",
            "problem": "In the video, which subtitles appear at the same time as the man with black hair, dressed in grey clothes with black sleeves, on stage?",
            "data_type": "video",
            "problem_type": "multiple choice",
            "options": [
                "A. promisc has come to an end, in and run away countless times, i was just scared, i still",
                "B. run away countless times, i was just scared, i still and front of our crown, like a world of souls,",
                "C. promisc has come to an end, in and front of our crown, like a world of souls,",
                "D. promisc has come to an end, in and captain of the godson, three three three three three three"
            ],
            "solution": "B",
            "path": "/mnt/data/raw_data/LongVideoBench/videos/86CxyhFV9MI.mp4",
            "data_source": "LongVideoBench"
        },
        """
        # Normalize to Video_MME format with lettered options and <answer>X</answer>
        options = qa_dict.get("options", [])
        letters = ["A", "B", "C", "D", "E", "F"]
        lettered = [f"{letters[i]}. {opt}" for i, opt in enumerate(options)]
        problem = qa_dict["problem"] + "Options: " + " ".join(lettered)
        sol = qa_dict.get("solution")
        # solution may already be a letter; if numeric index, convert
        if isinstance(sol, int):
            sol_letter = letters[sol] if 0 <= sol < len(letters) else "A"
        else:
            sol_letter = str(sol).strip()
            if sol_letter and sol_letter[0].isdigit():
                idx = int(sol_letter[0])
                sol_letter = letters[idx] if 0 <= idx < len(letters) else "A"
            elif sol_letter and sol_letter[0] in letters:
                sol_letter = sol_letter[0]
            else:
                # try to match by text
                try:
                    idx = options.index(sol)
                    sol_letter = letters[idx]
                except Exception:
                    sol_letter = "B"
        solution = sol_letter #f"<answer>{sol_letter}</answer>"
        return cls(
            question=qa_dict["problem"],
            options=[o.split('. ')[1] for o in options],
            answer=solution,
            video_key=qa_dict["problem_id"][:qa_dict["problem_id"].rfind("_")],
            uid = qa_dict["problem_id"],
            bench_object=bench_object
        )
    
    @classmethod
    def asLVBench(cls, qa_dict, bench_object):
        """
        {"video_key": "Cm73ma6Ibcs", "uid": "55", "question": "What year appears in the opening caption of the video?\n(A) 1636\n(B) 1366\n(C) 1363\n(D) 1633", "answer": "D", "question_type": ["key information retrieval"], "time_reference": "00:15-00:19"}
        """
        # Normalize to Video_MME format
        opts = qa_dict.get("options") or qa_dict.get("candidates") or []
        letters = ["A", "B", "C", "D", "E", "F"]
        lettered = [f"{letters[i]}. {opt}" for i, opt in enumerate(opts)]
        problem = qa_dict["question"] + (" Options: " + " ".join(lettered) if lettered else "")
        sol = qa_dict.get("answer")
        # sol may be a letter or text; convert to letter enclosed with tags
        if isinstance(sol, int):
            sol_letter = letters[sol] if 0 <= sol < len(letters) else "A"
        else:
            sol_letter = str(sol).strip()
            if sol_letter and sol_letter[0] in letters:
                sol_letter = sol_letter[0]
            else:
                try:
                    idx = opts.index(sol)
                    sol_letter = letters[idx]
                except Exception:
                    sol_letter = "A"
        solution = sol_letter #f"<answer>{sol_letter}</answer>"
        return cls(
            #question=problem,
            question=qa_dict["question"].split("\n")[0],
            options=[o.split(') ')[1] for o in qa_dict["question"].split("\n")[1:] if o],
            answer=solution,
            video_key=qa_dict["video_key"],
            uid = qa_dict["uid"],
            bench_object=bench_object,
            ref_start = qa_dict.get("time_reference", "").split("-")[0] if qa_dict.get("time_reference") else None,
            ref_end = qa_dict.get("time_reference", "").split("-")[1] if qa_dict.get("time_reference") else None,
        )
    
    @classmethod
    def asLongTimeScope(cls, qa_dict, bench_object):
        """
        {
            "problem_id": "OCR_36000_0",
            "problem": "What are all the special magic words mentioned in the provided video, ordered by their appearance?",
            "options": [
                "A: date, apple, kiwi",
                "B: raspberry, elderberry, quince",
                "C: grape, date, watermelon",
                "D: apple, kiwi, cherry",
                "E: kiwi, strawberry, kiwi",
                "F: lemon, ugli, ugli"
            ],
            "data_type": "video",
            "problem_type": "multiple choice",
            "process": "",
            "solution": "A",
            "path": "/mnt/data/raw_data/LongTimeScope/videos_split_2/videos_OCR_36000/0.mp4",
            "data_source": "LongTimeScope"
        },
        
        """
        options = qa_dict.get("options", [])
        letters = ["A", "B", "C", "D", "E", "F"]
        lettered = [f"{letters[i]}. {opt}" for i, opt in enumerate(options)]
        problem = qa_dict["problem"] + " Options: " + " ".join(lettered)
        sol = qa_dict.get("solution")
        if isinstance(sol, int):
            sol_letter = letters[sol] if 0 <= sol < len(letters) else "A"
        else:
            sol_letter = str(sol).strip()
            if sol_letter and sol_letter[0] in letters:
                sol_letter = sol_letter[0]
            else:
                try:
                    idx = options.index(sol)
                    sol_letter = letters[idx]
                except Exception:
                    sol_letter = "A"
        solution = sol_letter #f"<answer>{sol_letter}</answer>"
        return cls(
            #question=problem,
            question=qa_dict["problem"],
            options=[o.split(': ')[1] for o in options],
            answer=solution,
            video_key=qa_dict["problem_id"],
            uid = qa_dict["problem_id"],
            bench_object=bench_object
        )
    
    @classmethod
    def asMLVU(cls, qa_dict, bench_object):
        """
        {
            "video": "1_plotQA/movie101_66.mp4",
            "duration": 246,
            "question": "What color is the main male character in the video?",
            "candidates": [
                "Yellow",
                "Red",
                "Green",
                "Blue"
            ],
            "answer": "Yellow",
            "question_type": "plotQA",
            "data_source": "1_plotQA.json",
            "uid": "1_plotQA/movie101_66_0"
        },
        """
        candidates = qa_dict.get("candidates", [])
        letters = ["A", "B", "C", "D", "E", "F"]
        lettered = [f"{letters[i]}. {opt}" for i, opt in enumerate(candidates)]
        problem = qa_dict["question"] + " Options: " + " ".join(lettered)
        sol = qa_dict.get("answer")
        # match text to letter
        try:
            idx = candidates.index(sol)
            sol_letter = letters[idx]
        except Exception:
            sol_letter = str(sol).strip()[0].upper() if isinstance(sol, str) and sol else "A"
        solution = sol_letter #f"<answer>{sol_letter}</answer>"
        return cls(
            # question=problem,
            question=qa_dict["question"],
            options=qa_dict.get("candidates", []),
            answer=solution,
            video_key=qa_dict["video"][:-4],
            uid = qa_dict["uid"],
            bench_object=bench_object
        )
    
    @classmethod
    def asVideo_MME(cls, qa_dict, bench_object):
        """
        {
            "problem_id": "fFjv93ACGo8",
            "problem": "When demonstrating the Germany modern Christmas tree is initially decorated with apples, candles and berries, which kind of the decoration has the largest number?",
            "data_type": "video",
            "problem_type": "multiple choice",
            "options": [
                "A. Apples.",
                "B. Candles.",
                "C. Berries.",
                "D. The three kinds are of the same number."
            ],
            "solution": "<answer>C</answer>",
            "path": "/mnt/data/raw_data/Video-MME/videos/fFjv93ACGo8.mp4",
            "data_source": "Video-MME-short"
        },
        """
        letters = ["A", "B", "C", "D", "E", "F"]
        opts = qa_dict.get("options", [])
        # if already lettered, keep; else add letters
        normalized = []
        for i, opt in enumerate(opts):
            opt_str = str(opt)
            if len(opt_str) > 2 and opt_str[0] in letters and opt_str[1] == ".":
                normalized.append(opt_str)
            else:
                normalized.append(f"{letters[i]}. {opt_str}")
        problem = qa_dict["problem"] + "Options: " + " ".join(normalized)
        solution = qa_dict["solution"]
        sol_letter = solution[8] if len(solution) >= 10 and solution.startswith("<answer>") and solution.endswith("</answer>") else "A"
        solution = sol_letter #f"<answer>{sol_letter}</answer>"
        return cls(
            # question=problem,
            question = qa_dict["problem"],
            options = [o.split('. ')[1] for o in opts],
            answer=solution,
            video_key=qa_dict["problem_id"],
            uid = qa_dict["problem_id"],
            bench_object=bench_object
        )

    @classmethod
    def asEgoSchema(cls, qa_dict, bench_object):
        """
        {
            "q_uid": "00faf954-74f7-4aa3-8b29-4a5dff4f9518",
            "google_drive_id": "17vdvmp5BUcxwdUl_Rhq4WYpa_AVeA_IN",
            "question": "What is the primary sequence of actions performed by c throughout the video, and how do these actions relate to the overall task being performed?",
            "option 0": "C cleans brick mold with his hand.",
            "option 1": "C scoops clay into the brick mold, removes clay from the brick mold, scoops mortar from a pile of mortar on the floor, slams mortar into the brick mold, scoops excess mortar from the brick mold, throws excess mortar on the pile of mortar in his front, adds clay from the floor on the brick mold, and drops brick from brick mold beside already made bricks on the floor. then, c cleans brick mold with his hand.",
            "option 2": "C scoops clay into the brick mold, removes clay from the brick mold, scoops mortar from a pile of mortar on the floor, slams mortar into the brick mold, scoops excess mortar from the brick mold, throws excess mortar on the pile of mortar in his front, adds clay from the floor on the brick mold, drops brick from brick mold beside already made bricks on the floor. then, c takes a break.",
            "option 3": "C scoops clay into the brick mold, removes clay from the brick mold, scoops mortar from a pile of mortar on the floor, slams mortar into the brick mold, scoops excess mortar from the brick mold, throws excess mortar on the pile of mortar in his front, adds clay from the floor on the brick mold, drops brick from brick mold beside already made bricks on the floor. then, c goes to sleep.",
            "option 4": "C scoops clay into the brick mold, removes clay from the brick mold, scoops mortar from a pile of mortar on the floor, slams mortar into the brick mold, scoops excess mortar from the brick mold, throws excess mortar on the pile of mortar in his front, adds clay from the floor on the brick mold, and drops brick from brick mold beside already made bricks on the floor.",
            "answer": 4
        },
        
        """
        letters = ["A", "B", "C", "D", "E", "F"]
        opts = [qa_dict.get(f"option {i}", "") for i in range(5)]
        lettered = [f"{letters[i]}. {opt}" for i, opt in enumerate(opts)]
        question = qa_dict["question"] + " Options: " + " ".join(lettered)
        sol = qa_dict.get("answer")
        # answer is numeric index per example; convert to letter
        if isinstance(sol, int):
            sol_letter = letters[sol] if 0 <= sol < len(letters) else "A"
        else:
            try:
                idx = int(sol)
                sol_letter = letters[idx] if 0 <= idx < len(letters) else "A"
            except Exception:
                sol_letter = "A"
        solution = sol_letter #f"<answer>{sol_letter}</answer>"
        return cls(
            # question=question,
            question=qa_dict["question"],
            options=[qa_dict.get(f"option {i}", "") for i in range(6) if qa_dict.get(f"option {i}", "")],
            answer=solution,
            video_key=qa_dict["q_uid"],
            uid = qa_dict["q_uid"],
            bench_object=bench_object
        )
    
    @classmethod
    def asEgoLifeQA(cls, qa_dict, bench_object, video_key):
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
        letters = ["A", "B", "C", "D", "E", "F"]
        # collect choices (support up to 6)
        choice_keys = ["choice_a", "choice_b", "choice_c", "choice_d", "choice_e", "choice_f"]
        choices = [qa_dict.get(k) for k in choice_keys if qa_dict.get(k) is not None]
        lettered = [f"{letters[i]}. {opt}" for i, opt in enumerate(choices)]
        question = qa_dict.get("question", "") + (" Options: " + " ".join(lettered) if lettered else "")
        sol = qa_dict.get("answer")
        # normalize solution to a single letter
        if isinstance(sol, int):
            sol_letter = letters[sol] if 0 <= sol < len(letters) else "A"
        else:
            sol_str = str(sol).strip()
            if sol_str and sol_str[0].upper() in letters:
                sol_letter = sol_str[0].upper()
            else:
                try:
                    idx = choices.index(sol)
                    sol_letter = letters[idx]
                except Exception:
                    sol_letter = "A"
        solution = sol_letter
        #video_key = qa_dict.get("identity") or qa_dict.get("ID") or qa_dict.get("video_key") or "unknown"
        uid = qa_dict.get("ID")
        #print("query_time:", qa_dict.get("query_time"))
        #print("target_time:", qa_dict.get("target_time"))
        if "time_list" in qa_dict["target_time"]:
            qa_dict["target_time"]["start_time"] = str(min([int(t) for t in qa_dict["target_time"]["time_list"]]))
            qa_dict["target_time"]["start_date"] = qa_dict["target_time"]["date"]
            qa_dict["target_time"]["end_time"] = str(max([int(t) for t in qa_dict["target_time"]["time_list"]]))
            qa_dict["target_time"]["end_date"] = qa_dict["target_time"]["date"]
        elif qa_dict["target_time"]["time"].find("DAY") != -1:
            time_list = qa_dict["target_time"]["time"].split("DAY")
            qa_dict["target_time"]["time_list"] = [ qa_dict["target_time"]["date"]+"_"+time_list[0] ] + [ "DAY"+t for t in time_list[1:] if t ]
            qa_dict["target_time"]["start_time"] = qa_dict["target_time"]["time_list"][0][5:]
            qa_dict["target_time"]["start_date"] = qa_dict["target_time"]["time_list"][0][:4]
            qa_dict["target_time"]["end_time"] = qa_dict["target_time"]["time_list"][-1][5:]
            qa_dict["target_time"]["end_date"] = qa_dict["target_time"]["time_list"][-1][:4]
        elif qa_dict["target_time"]["time"].find("-") != -1:
            qa_dict["target_time"]["start_time"] = qa_dict["target_time"]["time"].split("-")[0]
            qa_dict["target_time"]["start_date"] = qa_dict["target_time"]["date"]
            qa_dict["target_time"]["end_time"] = qa_dict["target_time"]["time"].split("-")[1]
            qa_dict["target_time"]["end_date"] = qa_dict["target_time"]["date"]
        else:
            qa_dict["target_time"]["start_time"] = qa_dict["target_time"]["time"]
            qa_dict["target_time"]["start_date"] = qa_dict["target_time"]["date"]
            HH, MM, SS, FF = int(qa_dict["target_time"]["time"][0:2]), int(qa_dict["target_time"]["time"][2:4]), int(qa_dict["target_time"]["time"][4:6]), int(qa_dict["target_time"]["time"][6:8])
            FF += 1
            if FF >= 20:
                FF, SS = 0, SS + 1
                if SS >= 60:
                    SS, MM = 0, MM + 1
                    if MM >= 60: MM, HH = 0, HH + 1
            qa_dict["target_time"]["end_time"] = f"{HH:02d}{MM:02d}{SS:02d}{FF:02d}"
            qa_dict["target_time"]["end_date"] = qa_dict["target_time"]["date"]


        query_time = f"{qa_dict['query_time']['date']}_{qa_dict['identity']}_{qa_dict['query_time']['time']}"
        ref_start = f"{qa_dict['target_time']['start_date']}_{qa_dict['identity']}_{qa_dict['target_time']['start_time']}"
        ref_end = f"{qa_dict['target_time']['end_date']}_{qa_dict['identity']}_{qa_dict['target_time']['end_time']}"
        
        
        QUERY_TS, REFSTART_TS, REFEND_TS = bench_object.Videos[video_key].TSS(query_time, domain="natural"), bench_object.Videos[video_key].TSS(ref_start, domain="natural"), bench_object.Videos[video_key].TSS(ref_end, domain="natural")

        return cls(
            # question=question,
            question=qa_dict["question"],
            options=[qa_dict.get(k) for k in choice_keys if qa_dict.get(k) is not None],
            answer=solution,
            video_key=video_key,
            uid=uid,
            bench_object=bench_object,
            # query_time = f"{qa_dict['query_time']['date']}_{qa_dict['identity']}_{qa_dict['query_time']['time']}",
            # ref_start = f"{qa_dict['target_time']['start_date']}_{qa_dict['identity']}_{qa_dict['target_time']['start_time']}",
            # ref_end = f"{qa_dict['target_time']['end_date']}_{qa_dict['identity']}_{qa_dict['target_time']['end_time']}",
            query_time = QUERY_TS,
            ref_start = REFSTART_TS,
            ref_end = REFEND_TS,
        )
    
    @classmethod
    def asXLeBench(cls, qa_dict, bench_object, video_key):
        """
        {
            "response_start_time_sec": 43050.0210286,
            "response_end_time_sec": 43064.4490286,
            "query": "Where is the knife?",
            "template": "Objects: Where is object X?",
            "video_uid": "1246d6ec-5620-4f71-8b4b-d823775f58c2"
            "global_uid": "xlebench_00001",
        },
        """


        REFSTART_TS, REFEND_TS = bench_object.Videos[video_key].TSS(qa_dict.get("response_start_time_sec"), domain="natural"), bench_object.Videos[video_key].TSS(qa_dict.get("response_end_time_sec"), domain="natural")
        return cls(
            question=qa_dict["query"],
            options=[],
            answer=qa_dict.get("answer", "A"),
            video_key=qa_dict["video_uid"],
            uid = qa_dict.get("global_uid", "unknown"),
            bench_object=bench_object,
            # query_time = bench_object.Videos[video_key].duration,
            # ref_start = qa_dict.get("response_start_time_sec", None),
            # ref_end = qa_dict.get("response_end_time_sec", None),
            ref_start = REFSTART_TS,
            ref_end = REFEND_TS,
        )