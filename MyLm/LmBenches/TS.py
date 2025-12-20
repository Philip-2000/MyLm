TEMP_LOG = False

class TS:
    def __init__(self, TSS=None, Natural_Time=None, Continuous_Time=None, Video_path=None, Video_Time=None):
        self.TSS = TSS
        #a week level timestamp, supporting all kinds of format and operation,

        #several elements
        #(1) Natural time, the time in the real world
            #(a) natural language format DAY1_A1_JAKE_11094208
            #(b) DD:HH:MM:SS format, 
            #(c) second format 0s at DAY1_00000000
        #print("Natural-Time", Natural_Time)
        self.NATURAL_TIME = TS.auto2natural(Natural_Time) if Natural_Time is not None else None #{ "day": None, "hour": None, "minute": None, "second": None, "frame": None }
        #print("Natural-Time after conversion", self.NATURAL_TIME)
        #(2) Continuous time, the time in this activity; if there are bubbles among the activity, such continuous time will pause accordingly
            #(a) second format 0s at the start of this activity
            #(b) HHH:MM:SS format, do not support cross day, but use 999 hours to represent hours more than one day; because such time only represents the duration in this activity, but not the clock time in real world

        self.CONTINUOUS_TIME = TS.auto2continuous(Continuous_Time) if Continuous_Time is not None else None #{ "hour": None, "minute": None, "second": None }

        #(3) Video time, the time in the video (so the video path is also needed)
            #(a) second format 0s at the start of this video
            #(b) HHH:MM:SS format, 
        
        self.VIDEO_PATH = Video_path
        self.VIDEO_TIME = TS.auto2video(Video_Time) if Video_Time is not None else None #{ "hour": None, "minute": None, "second": None }

    def __repr__(self):
        return f"TS (Natural_Time={self.natural_string if self.NATURAL_TIME is not None else 'None'}, Continuous_Time={self.continuous_hhhmmss if self.CONTINUOUS_TIME is not None else 'None'}, Video_path={self.VIDEO_PATH if self.VIDEO_PATH is not None else 'None'}, Video_Time={self.video_hhhmmss if self.VIDEO_TIME is not None else 'None'})"

    @property
    def VIDEO(self):
        return self.TSS.VIDEO if self.TSS is not None else None
    
    @property
    def subject(self):
        return self.TSS.subject if self.TSS is not None else None
    
    def copy(self):
        NEW_TS = TS(
            TSS=self.TSS,
            Natural_Time=self.natural,
            Continuous_Time=self.continuous,
            Video_path=self.VIDEO_PATH,
            Video_Time=self.video_time
        )
        return NEW_TS
    
    def fill(self, refer):
        if self.NATURAL_TIME is None and self.CONTINUOUS_TIME is not None:
            #fill my NATURAL_TIME according to refer's NATURAL_TIME and CONTINUOUS_TIME
            seconds = self.continuous_second - refer.continuous_second
            self.NATURAL_TIME = TS.second2natural(refer.natural_second + seconds)
            self.VIDEO_TIME = TS.second2video(refer.video_second + seconds)
            self.VIDEO_PATH = refer.VIDEO_PATH
            self.TSS = refer.TSS
        elif self.CONTINUOUS_TIME is None and self.NATURAL_TIME is not None:
            seconds = self.natural_second - refer.natural_second
            self.CONTINUOUS_TIME = TS.second2continuous(refer.continuous_second + seconds)
            self.VIDEO_TIME = TS.second2video(refer.video_second + seconds)
            self.VIDEO_PATH = refer.VIDEO_PATH
            self.TSS = refer.TSS

    def __iadd__(self, gap_s: float): #move this timestamp by gap second
        if self.NATURAL_TIME is not None:
            self.NATURAL_TIME = TS.second2natural(self.natural_second + gap_s)
        if self.CONTINUOUS_TIME is not None:
            self.CONTINUOUS_TIME = TS.second2continuous(self.continuous_second + gap_s)
        if self.VIDEO_TIME is not None: self.VIDEO_TIME = TS.second2video(self.video_second + gap_s)
        return self
    
    def __isub__(self, gap_s: float): #move this timestamp by gap second
        return self.__iadd__(-gap_s)

    #region: operators

    def __lt__(self, other):
        if self.NATURAL_TIME is not None and other.NATURAL_TIME is not None:
            return self.natural_second < other.natural_second
        elif self.CONTINUOUS_TIME is not None and other.CONTINUOUS_TIME is not None:
            return self.continuous_second < other.continuous_second
        else:
            raise ValueError("Cannot compare TS with different time domains.")
    
    def __le__(self, other):
        if self.NATURAL_TIME is not None and other.NATURAL_TIME is not None:
            return self.natural_second <= other.natural_second
        elif self.CONTINUOUS_TIME is not None and other.CONTINUOUS_TIME is not None:
            return self.continuous_second <= other.continuous_second
        else:
            raise ValueError("Cannot compare TS with different time domains.")
    
    def __eq__(self, other):
        if self.NATURAL_TIME is not None and other.NATURAL_TIME is not None:
            return self.natural_second == other.natural_second
        elif self.CONTINUOUS_TIME is not None and other.CONTINUOUS_TIME is not None:
            return self.continuous_second == other.continuous_second
        else:
            raise ValueError("Cannot compare TS with different time domains.")

    def __gt__(self, other):
        if self.NATURAL_TIME is not None and other.NATURAL_TIME is not None:
            return self.natural_second > other.natural_second
        elif self.CONTINUOUS_TIME is not None and other.CONTINUOUS_TIME is not None:
            return self.continuous_second > other.continuous_second
        else:
            raise ValueError("Cannot compare TS with different time domains.")
    
    def __ge__(self, other):
        if self.NATURAL_TIME is not None and other.NATURAL_TIME is not None:
            return self.natural_second >= other.natural_second
        elif self.CONTINUOUS_TIME is not None and other.CONTINUOUS_TIME is not None:
            return self.continuous_second >= other.continuous_second
        else:
            raise ValueError("Cannot compare TS with different time domains.")
    
    #endregion

    #region Natural Time Conversions
    @classmethod
    def auto2natural(cls, time_str):
        if isinstance(time_str, (int, float)):
            return cls.second2natural(time_str)
        elif "_" in time_str:
            return cls.string2natural(time_str)
        elif ":" in time_str:
            return cls.ddhhmmss2natural(time_str)
        else:
            raise ValueError(f"Unrecognized time format: {time_str}")

    @classmethod
    def string2natural(cls, time_str): # DAY1_A1_JAKE_11094208
        day_part, time_part = time_str.split("_")[0], time_str.split("_")[-1]
        NATURAL_TIME = {}
        NATURAL_TIME["day"] = int(day_part[3:]) #DAY1 -> 1
        NATURAL_TIME["hour"] = int(time_part[0:2])
        NATURAL_TIME["minute"] = int(time_part[2:4])
        NATURAL_TIME["second"] = int(time_part[4:6]) + float(time_part[6:8]) / 20
        #NATURAL_TIME["frame"] = int(time_part[6:8])
        return NATURAL_TIME
    
    @classmethod
    def ddhhmmss2natural(cls, ddhhmmss_str): # 01:11:09:42
        NATURAL_TIME = {}
        NATURAL_TIME["day"] = int(ddhhmmss_str[0:2])
        NATURAL_TIME["hour"] = int(ddhhmmss_str[3:5])
        NATURAL_TIME["minute"] = int(ddhhmmss_str[6:8])
        NATURAL_TIME["second"] = float(ddhhmmss_str[9:])
        #NATURAL_TIME["frame"] = 0
        return NATURAL_TIME
    
    @classmethod
    def second2natural(cls, second_int): # 11*3600 + 9*60 + 42 = 40182
        total_seconds = float(second_int)
        frame = 0
        day = total_seconds // 86400
        hour = (total_seconds % 86400) // 3600
        minute = (total_seconds % 3600) // 60
        second = total_seconds % 60
        NATURAL_TIME = {}
        NATURAL_TIME["day"] = int(day) + 1
        NATURAL_TIME["hour"] = int(hour)
        NATURAL_TIME["minute"] = int(minute)
        NATURAL_TIME["second"] = float(second)
        #NATURAL_TIME["frame"] = frame    
        return NATURAL_TIME

    @property
    def natural_second(self): # 40182
        return (self.NATURAL_TIME["day"]-1) * 86400 + self.NATURAL_TIME["hour"] * 3600 + self.NATURAL_TIME["minute"] * 60 + self.NATURAL_TIME["second"]
    
    @property
    def natural_ddhhmmss(self): # 01:11:09:42
        return f"{self.NATURAL_TIME['day']:02}:{self.NATURAL_TIME['hour']:02}:{self.NATURAL_TIME['minute']:02}:{int(self.NATURAL_TIME['second']):02}.{'{:.2f}'.format(self.NATURAL_TIME['second']).split('.')[1]}"
    
    @property
    def natural_string(self): # DAY1_A1_JAKE_11094208
        return f"DAY{self.NATURAL_TIME['day']}_{self.subject}_{self.NATURAL_TIME['hour']:02}{self.NATURAL_TIME['minute']:02}{int(self.NATURAL_TIME['second']):02}{int((self.NATURAL_TIME['second'] % 1) * 20):02}"
    
    @property
    def natural(self):
        return self.natural_string
    #endregion

    #region Continuous Time Conversions
    @classmethod
    def auto2continuous(cls, time_str):
        if isinstance(time_str, (int, float)):
            return cls.second2continuous(time_str)
        elif ":" in time_str:
            return cls.hhmmss2continuous(time_str)
        else:
            raise ValueError(f"Unrecognized time format: {time_str}")
    
    @classmethod
    def hhhmmss2continuous(cls, hhhmmss_str): # 011:09:42
        CONTINUOUS_TIME = {}
        CONTINUOUS_TIME["hour"] = int(hhhmmss_str[0:4])
        CONTINUOUS_TIME["minute"] = int(hhhmmss_str[5:7])
        CONTINUOUS_TIME["second"] = float(hhhmmss_str[8:])
        return CONTINUOUS_TIME
    
    @classmethod
    def second2continuous(cls, second_float): # 11*3600 + 9*60 + 42 = 40182
        total_seconds = float(second_float)
        hour = total_seconds // 3600
        minute = (total_seconds % 3600) // 60
        second = total_seconds % 60
        CONTINUOUS_TIME = {}
        CONTINUOUS_TIME["hour"] = int(hour)
        CONTINUOUS_TIME["minute"] = int(minute)
        CONTINUOUS_TIME["second"] = float(second)
        return CONTINUOUS_TIME
    
    @property
    def continuous_second(self): # 40182
        return self.CONTINUOUS_TIME["hour"] * 3600 + self.CONTINUOUS_TIME["minute"] * 60 + self.CONTINUOUS_TIME["second"]
    
    @property
    def continuous_hhhmmss(self): # 011:09:42
        return f"{self.CONTINUOUS_TIME['hour']:03}:{self.CONTINUOUS_TIME['minute']:02}:{int(self.CONTINUOUS_TIME['second']):02}.{'{:.2f}'.format(self.CONTINUOUS_TIME['second']).split('.')[1]}"
    
    @property
    def continuous(self):
        return self.continuous_second
    #endregion

    #region Video Time Conversions
    @classmethod
    def auto2video(cls, time_str):
        if isinstance(time_str, (int, float)):
            return cls.second2video(time_str)
        elif ":" in time_str:
            return cls.hhmmss2video(time_str)
        else:
            raise ValueError(f"Unrecognized time format: {time_str}")
    
    @classmethod
    def hhhmmss2video(cls, hhhmmss_str): # 001:09:42
        VIDEO_TIME = {}
        VIDEO_TIME["hour"] = int(hhhmmss_str[0:4])
        VIDEO_TIME["minute"] = int(hhhmmss_str[5:7])
        VIDEO_TIME["second"] = int(hhhmmss_str[8:10])
        return VIDEO_TIME
    
    @classmethod
    def second2video(cls, second_int): # 1*3600 + 9*60 + 42 = 4182
        total_seconds = float(second_int)
        hour = total_seconds // 3600
        minute = (total_seconds % 3600) // 60
        second = total_seconds % 60
        VIDEO_TIME = {}
        VIDEO_TIME["hour"] = hour
        VIDEO_TIME["minute"] = minute
        VIDEO_TIME["second"] = second
        return VIDEO_TIME
    
    @property
    def video_second(self): # 4182
        return self.VIDEO_TIME["hour"] * 3600 + self.VIDEO_TIME["minute"] * 60 + self.VIDEO_TIME["second"]
    
    @property
    def video_hhhmmss(self): # 001:09:42
        return f"{self.VIDEO_TIME['hour']:03}:{self.VIDEO_TIME['minute']:02}:{int(self.VIDEO_TIME['second']):02}.{'{:.2f}'.format(self.VIDEO_TIME['second']).split('.')[1]}"
    
    @property
    def video_time(self):
        return self.video_second
    #endregion

class TSS:
    def __init__(self, VIDEO=None):
        self.VIDEO = VIDEO
        self.subject = VIDEO.identity if VIDEO is not None else None
        self.TS_LIST = []
        #a sequence of TS, supporting all kinds of format and operation,
    
    def __repr__(self):
        return f"TSS (subject={self.subject}, num_TS={len(self.TS_LIST)}, duration={self.duration_hhhmmss}({self.duration_seconds}s))\n" + \
        "\n".join([f"\t{ts.__repr__()}" for ts in self.TS_LIST][:2]) + \
        ("\n\t..." if len(self.TS_LIST) > 3 else "") + \
        ("\n\t" + self.TS_LIST[-1].__repr__() if len(self.TS_LIST) > 2 else "")
    
    def __getitem__(self, id):
        return self.TS_LIST[id]
    
    def __len__(self):
        return len(self.TS_LIST)
    
    def __iter__(self):
        return iter(self.TS_LIST)

    def __call__(self, time_str, domain="continuous"):
        if domain == "natural":
            THE_TS = TS(self, Natural_Time=time_str)
        elif domain == "continuous":
            THE_TS = TS(self, Continuous_Time=time_str)
        else:
            raise ValueError(f"Unrecognized domain: {domain}")

        if TEMP_LOG: print(f"Finding TS for time_str={time_str} in domain={domain}, Initial THE_TS:\n\t", THE_TS)

        TS_ID = 0
        THE_TS += 0.01 # to pass the lower comparation
        while TS_ID < len(self.TS_LIST) and self.TS_LIST[TS_ID] < THE_TS:
            TS_ID += 1
        if TS_ID == 0:
            print(self.TS_LIST[0].continuous)
            print(THE_TS.continuous)
            raise ValueError("No reference TS available")
        REFER_TS = self.TS_LIST[TS_ID - 1]
        THE_TS -= 0.01

        if TEMP_LOG: print(f"Found reference TS (ID={TS_ID - 1}):\n\t", REFER_TS)

        THE_TS.fill(REFER_TS)

        if TEMP_LOG: print(f"Final THE_TS after filling:\n\t", THE_TS)

        return THE_TS
    
    def clip(self, time_str, domain="natural"):
        if TEMP_LOG: print(f"Clipping TSS at {time_str} in domain {domain}, self:\n", self)
            
        THE_TS = self(time_str, domain)
        NEW_TSS = TSS(self.VIDEO)
        NEW_TSS.subject = self.subject
        for ts in self:
            if ts <= THE_TS:
                NEW_TSS.TS_LIST.append(ts.copy())
                NEW_TSS[-1].TSS = NEW_TSS
            else:
                NEW_TSS.TS_LIST.append(THE_TS.copy())
                NEW_TSS[-1].TSS = NEW_TSS
                break
        #self.TS_LIST.sort()
        
        if TEMP_LOG: print("Resulting clipped TSS:\n", NEW_TSS)

        return NEW_TSS
    
    def segments(self, N=32):
        seconds = [float((self.duration_seconds * i) / N) for i in range(N)]
        R = [self(sec) for sec in seconds]
        if TEMP_LOG: print(f"Segmenting TSS into {N} segments, result TS:\n", "\n".join([f"\t{ts}, gap from previous: {ts.continuous_second - (R[i-1].continuous_second if i > 0 else 0)}" for i, ts in enumerate(R)]))
        return R

    def __iadd__(self, other):
        if isinstance(other, TS):
            self.TS_LIST.append(other)
            other.TSS = self
            self.TS_LIST.sort()
            return self
        else:
            raise ValueError("Can only add TS instances to TSS.")

    @property
    def earliest(self):
        return self.TS_LIST[0]

    @property
    def latest(self):
        return self.TS_LIST[-1]

    @property
    def timespan_seconds(self):
        return self.latest.natural_second - self.earliest.natural_second

    @property
    def timespan_hhhmmss(self):
        total_seconds = self.timespan_seconds
        hour = total_seconds // 3600
        minute = (total_seconds % 3600) // 60
        second = float(total_seconds % 60)
        tail = (str(second - int(second)) + "00").split(".")[1][:2]
        return f"{int(hour):03}:{int(minute):02}:{int(second):02}.{tail}"

    @property
    def timespan(self):
        return self.timespan_hhhmmss

    @property
    def duration_seconds(self):
        return self.latest.continuous_second - self.earliest.continuous_second
    
    @property
    def duration_hhhmmss(self):
        total_seconds = self.duration_seconds
        hour = total_seconds // 3600
        minute = (total_seconds % 3600) // 60
        second = float(total_seconds % 60)
        tail = (str(second - int(second)) + "00").split(".")[1][:2]
        return f"{int(hour):03}:{int(minute):02}:{int(second):02}.{tail}"

    @property
    def duration(self):
        return self.duration_hhhmmss