class QA:
    def __init__(self, question="", answer="", video_key="", uid="None", bench_object=None):
        self.uid = uid
        self.question = question
        self.answer = answer
        self.video_key = video_key
        self.bench_object = bench_object
        self.result = ""
        self._compare = None
        self._video_path = self.get_video_path()
    
    def run(self, model, **kwargs):
        prompt = f"IMPORTANT: You MUST answer based ONLY on the content of the video.\n Video ID: {self.video_key}\nQuestion: {self.question}\n【Strict Instructions】1. Answer ONLY with the single option letter (e.g., A/B/C/D/E/F) that matches the correct answer.2. Do NOT add any extra explanation, video details, reasoning, or irrelevant text.Answer:"
        # prompt = f"Video ID: {self.video_key}\nQuestion: {self.question}\nAnswer:"
        from .. import call
        self.result = call(model, {"content": [{"text": prompt}, {"video":self.video_path}], **kwargs} )
        return self.result, self.compare(self.result)

    @property
    def record(self):
        return {"result": self.result, "correct": self._compare}
    
    # hrw
    def get_video_path(self):
        try:
            return self.bench_object.Videos[self.video_key].path
        except (AttributeError, KeyError):
            raise ValueError(f"Video with key '{self.video_key}' not found in benchmark object.")
        
    @property
    def video_path(self):
        return self._video_path

    def compare(self, generated_answer=""):
        if self._compare is None:
            ans = generated_answer if generated_answer else self.result
            sol_letter = ans[8] if len(ans) >= 10 and ans.startswith("<answer>") and ans.endswith("</answer>") else ans[0]
            self._compare = (sol_letter.strip().lower() == self.answer.strip().lower())
        return self._compare

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
            question=problem,
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
            question=problem,
            answer=solution,
            video_key=qa_dict["video_key"],
            uid = qa_dict["uid"],
            bench_object=bench_object
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
            question=problem,
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
            question=problem,
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
            question=problem,
            answer=solution,
            video_key=qa_dict["problem_id"],
            uid = qa_dict["problem_id"],
            bench_object=bench_object
        )

    @classmethod
    def asegoschema(cls, qa_dict, bench_object):
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
            question=question,
            answer=solution,
            video_key=qa_dict["q_uid"],
            uid = qa_dict["q_uid"],
            bench_object=bench_object
        )