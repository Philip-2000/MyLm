import os

from .AModel import AModel, AFormater
import os
from PIL import Image

class Qwen3_5_27B_Formater(AFormater):
    def __init__(self):
        pass
    
    def video(self, v, **kwargs):
        if isinstance(v, str) and os.path.isfile(v):
            assert os.path.exists(v), f"Video path {v} does not exist"
            import numpy as np
            if v.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                #return v
                return self.video_real(v, **kwargs)
            if os.isdir(v):
                # a folder of frames
                frame_rates = kwargs.get("frame_rates", -1)

                frame_files = sorted([
                    os.path.join(v, f) for f in os.listdir(v)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
                ], key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x))) or -1))
                if frame_rates > 0 and len(frame_files) >= frame_rates:
                    idx = np.linspace(0, len(frame_files) - 1, frame_rates).astype(int)
                    frame_files = [frame_files[i] for i in idx]
                frames = [np.array(Image.open(f).convert("RGB")) for f in frame_files]
                return np.stack(frames)
        elif isinstance(v, list):
            return [frame for frame in v]
        else:
            raise ValueError("Qwen3_5_27B_Formater.video: Unsupported video input type.")

    def video_real(self, v, **kwargs):
        print("Qwen3_5_27B.load_video:", v, "frame_rates:", kwargs.get("frame_rates",-1), "num_segments:", kwargs.get("num_segments",-1))
        from decord import VideoReader, cpu
        import torch, numpy as np
        vr = VideoReader(v, ctx=cpu(0), num_threads=1)
        total_frames = len(vr)
        fps = float(vr.get_avg_fps())


        frame_rates = kwargs.get("frame_rates", -1)
        num_segments = kwargs.get("num_segments", -1)
        if frame_rates < 0 and num_segments < 0:
            print("frame_rates < 0 and num_segments < 0, set frame_rates = 1")
            frame_rates = 1
        elif frame_rates < 0 and num_segments > 0:
            print("frame_rates < 0 and num_segments > 0, calculate frame_rates = total_frames // num_segments")
            frame_rates = total_frames // num_segments
        elif frame_rates > 0 and num_segments < 0:
            print("frame_rates > 0 and num_segments < 0, use frame_rates as is")
            frame_rates = frame_rates
            num_segments = total_frames // frame_rates
        else:
            print("frame_rates > 0 and num_segments > 0, use the smaller one as frame_rates")
            frame_rates = max(frame_rates, total_frames // num_segments)
            num_segments = total_frames // frame_rates
        frame_rates = max(1, int(frame_rates))
        
        # evenly sample indices
        if total_frames < frame_rates:
            indices = np.linspace(0, total_frames - 1, total_frames).astype(int)
        else:
            indices = np.linspace(0, total_frames - 1, num_segments).astype(int)
        
        print("Qwen3_5_27B.parsed:", v, "frame_rates:", frame_rates, "num_segments:", num_segments, "total_frames:", total_frames, "len(indices):", len(indices))  
        

        frames = []
        start_index = indices[0]
        end_index = indices[-1]
        print("Qwen3_5_27B.load_video","start_index:", start_index, "end_index:", end_index)
        for frame_index in indices:
            img = Image.fromarray(vr[frame_index].asnumpy()).convert("RGB")
            frames.append(img)
        print("Qwen3_5_27B.load_video","num_segments:", len(frames), "fps:", frame_rates, "max_frame:", len(indices), "len(frames):", len(frames))

        
        clip = np.stack([
            np.asarray(x.convert("RGB"), dtype=np.uint8) if isinstance(x, Image.Image) else np.asarray(x, dtype=np.uint8)
            for x in frames
        ])
        print("type of clip:", type(clip), "shape of clip:", clip.shape)
        return clip

    def text(self, t):
        return t
    
    def image(self, i):
        return i

    def __call__(self, item, **kwargs):
        if list(item.keys()) == ["system"]:
            return {"type": "text", "text": self.text(item["system"])}
        elif list(item.keys()) == ["user"]:
            return {"type": "text", "text": self.text(item["user"])}
        elif list(item.keys()) == ["text"]:
            return {"type": "text", "text": self.text(item["text"])}
        elif list(item.keys()) == ["image"]:
            return {"type": "image", "image": self.image(item["image"])}
        elif list(item.keys()) == ["video"]:
            return {"type": "video", "video": self.video(item["video"], **kwargs)}
        else:
            raise ValueError("LLaVA_NeXT_Video_7B_hf_Formater.__call__: Unsupported item type.")
    

class Qwen3_5_27B(AModel):
    def __init__(self, model_dir):
        S = "Qwen3.5-27B"
        from .. import GLOBAL_CONFIG
        T = S.replace("27B", GLOBAL_CONFIG[S]["par"])
        model_id = model_dir.replace(S, T) if model_dir.endswith(S) else os.path.join(model_dir, T)
        
        from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, dtype="auto", device_map="auto")
        self.processor = AutoProcessor.from_pretrained(model_id, device_map="auto")
        self.formater = Qwen3_5_27B_Formater()

    def __call__(self, input_data):
        # raise NotImplementedError("Qwen3_32B.__call__ is not ok yet.")
        kwargs = input_data
        messages = [
            {"role": "user", "content": [self.formater(c, **kwargs) for c in input_data["content"]]}
        ]

        # # Preparation for inference
        # inputs = self.processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt").to(self.model.device)
        # # Inference: Generation of the output
        # generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        # generated_ids_trimmed = [ out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids) ]
        # return self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()
        inputs = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(inputs, return_tensors="pt").to(self.model.device)
        # Inference: Generation of the output
        generated_ids = self.model.generate(inputs.input_ids, max_new_tokens=1024)
        # generated_ids_trimmed = [ out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids) ]
        # return self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()
        return self.tokenizer.decode(generated_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
