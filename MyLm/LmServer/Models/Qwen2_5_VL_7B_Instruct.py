from .AModel import AModel, AFormater
import os
from PIL import Image

class Qwen2_5_VL_7B_Instruct_Formater(AFormater):
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

        return frames
  
    def video_fake(self, v, **kwargs):
        print("Qwen3_VL_8B_Instruct.load_video:", v, "frame_rates:", kwargs.get("frame_rates",-1), "num_segments:", kwargs.get("num_segments",-1))
        import av
        import numpy as np
        container = av.open(v)
        stream = container.streams.video[0]
        # try the reported frame count first (may be 0 or None if unknown)
        total_frames = getattr(stream, "frames", 0) or 0

        # if frames is missing or zero, try to compute from duration and average/base rate
        if not total_frames or total_frames <= 0:
            try:
                if stream.duration is not None:
                    # stream.duration * stream.time_base gives seconds
                    seconds = float(stream.duration * stream.time_base)
                    avg_rate = stream.average_rate or stream.base_rate
                    if avg_rate is not None:
                        total_frames = max(0, int(seconds * float(avg_rate)))
            except Exception:
                total_frames = 0

        # last resort: count frames by decoding (may be slow)
        if not total_frames or total_frames <= 0:
            total_frames = 0
            for _ in container.decode(video=0):
                total_frames += 1
            container.seek(0)

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
        container.seek(0)
        start_index = indices[0]
        end_index = indices[-1]
        print("Qwen3_VL_8B_Instruct.load_video","start_index:", start_index, "end_index:", end_index)
        for i, frame in enumerate(container.decode(video=0)):
            if i > end_index:
                break
            if i >= start_index and i in indices:
                print("Qwen3_VL_8B_Instruct.load_video","decoding frame index:", i)
                frames.append(frame)
                print("type of frame:", type(frame), "size of frame:", frame.width, frame.height)
        print("Qwen3_VL_8B_Instruct.load_video","num_segments:", len(frames), "fps:", frame_rates, "max_frame:", len(indices), "len(frames):", len(frames))

        clip = np.stack([x.to_ndarray(format="rgb24") for x in frames])
        print("type of clip:", type(clip), "shape of clip:", clip.shape)
        return clip

    def text(self, t):
        return t
    
    def image(self, i):
        return "file://"+i

    def __call__(self, item, **kwargs):
        if list(item.keys()) == ["text"]:
            return {"type": "text", "text": self.text(item["text"])}
        elif list(item.keys()) == ["image"]:
            return {"type": "image", "image": self.image(item["image"])}
        elif list(item.keys()) == ["video"]:
            return {"type": "video", "video": self.video(item["video"], **kwargs)}
        else:
            raise ValueError("LLaVA_NeXT_Video_7B_hf_Formater.__call__: Unsupported item type.")
    
    

class Qwen2_5_VL_7B_Instruct(AModel):
    def __init__(self, model_dir):
        model_id = model_dir if model_dir.endswith("Qwen2.5-VL-7B-Instruct") else os.path.join(model_dir, "Qwen2.5-VL-7B-Instruct")

        from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_id, dtype="auto", device_map="auto")
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.formater = Qwen2_5_VL_7B_Instruct_Formater()

    def __call__(self, input_data):
        kwargs = input_data
        #assert list(input_data["content"][0].keys())==['text'] and list(input_data["content"][1].keys())==['video'], "Although our model should support text+image+video input, currently we only support text+video input for simplicity."
         
        messages = [
            {"role": "user", "content": [self.formater(c, **kwargs) for c in input_data["content"]]}
        ]

        # # Preparation for inference
        # inputs = self.processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt").to(self.model.device)
        # # Inference: Generation of the output
        # generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        # generated_ids_trimmed = [ out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids) ]
        # return self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()



        # # Preparation for inference
        from qwen_vl_utils import process_vision_info
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(self.model.device)

        # # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=1024)
        generated_ids_trimmed = [ out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids) ]
        return self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()
