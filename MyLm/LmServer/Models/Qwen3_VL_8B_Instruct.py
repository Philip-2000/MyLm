from .AModel import AModel, AFormater
import os
from PIL import Image

class Qwen3_VL_8B_Instruct_Formater(AFormater):
    def __init__(self):
        pass
    
    def video(self, v, **kwargs):
        if isinstance(v, str) and os.path.isfile(v):
            assert os.path.exists(v), f"Video path {v} does not exist"

            if v.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
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
            raise ValueError("Qwen3_VL_8B_Instruct_Formater.video: Unsupported video input type.")

    def video_real(self, v, **kwargs):
        print("Qwen3_VL_8B_Instruct.load_video:", v, "frame_rates:", kwargs.get("frame_rates",-1), "num_segments:", kwargs.get("num_segments",-1))
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
        
        print("Qwen3_VL_8B_Instruct.parsed:", v, "frame_rates:", frame_rates, "num_segments:", num_segments, "total_frames:", total_frames, "len(indices):", len(indices))  
        

        frames = []
        start_index = indices[0]
        end_index = indices[-1]
        print("Qwen3_VL_8B_Instruct.load_video","start_index:", start_index, "end_index:", end_index)
        for frame_index in indices:
            img = Image.fromarray(vr[frame_index].asnumpy()).convert("RGB")
            frames.append(img)
        print("Qwen3_VL_8B_Instruct.load_video","num_segments:", len(frames), "fps:", frame_rates, "max_frame:", len(indices), "len(frames):", len(frames))

        
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
        if list(item.keys()) == ["text"]:
            return {"type": "text", "text": self.text(item["text"])}
        elif list(item.keys()) == ["image"]:
            return {"type": "image", "image": self.image(item["image"])}
        elif list(item.keys()) == ["video"]:
            return {"type": "video", "video": self.video(item["video"], **kwargs)}
        else:
            raise ValueError("LLaVA_NeXT_Video_7B_hf_Formater.__call__: Unsupported item type.")
    
class Qwen3_VL_8B_Instruct(AModel):
    def __init__(self, model_dir):
        model_id = model_dir if model_dir.endswith("Qwen3-VL-8B-Instruct") else os.path.join(model_dir, "Qwen3-VL-8B-Instruct")

        from transformers import Qwen3VLForConditionalGeneration, AutoProcessor

        self.model = Qwen3VLForConditionalGeneration.from_pretrained(model_id, dtype="auto", device_map="auto")
        self.processor = AutoProcessor.from_pretrained(model_id)

        self.formater = Qwen3_VL_8B_Instruct_Formater()

    def __call__(self, input_data):
        kwargs = input_data
        #assert list(input_data["content"][0].keys())==['text'] and list(input_data["content"][1].keys())==['video'], "Although our model should support text+image+video input, currently we only support text+video input for simplicity."
        print("Qwen3_VL_8B_Instruct.__call__", "frame_rates:", kwargs.get("frame_rates",-1))
        messages = [
            {"role": "user", "content": [self.formater(c, **kwargs) for c in input_data["content"]]}
        ]

        # Preparation for inference
        inputs = self.processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt").to(self.model.device)

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=1024)
        generated_ids_trimmed = [ out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids) ]
        return self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()

