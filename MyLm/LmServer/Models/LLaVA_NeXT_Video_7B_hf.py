from .AModel import AModel, AFormater
import os
from PIL import Image
import numpy as np


class LLaVA_NeXT_Video_7B_hf_Formater(AFormater):
    def __init__(self):
        self.target_size = (448,448)
    
    def resize_frame(self, frame):
        """统一帧尺寸，确保维度一致"""
        import numpy as np
        if isinstance(frame, np.ndarray):
            frame = Image.fromarray(frame).convert("RGB")
        return frame.resize(self.target_size, Image.Resampling.LANCZOS)

    def video(self, v, **kwargs):
        '''
        v should support different types of inputs, such as sub-folders of frames, video file path/uri, preloaded frames as numpy array etc.
        '''
        if isinstance(v, str):
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
                frames = [np.array(self.resize_frame(Image.open(f).convert("RGB"))) for f in frame_files]
                return np.stack(frames).astype(np.float32) / 255.0
        elif isinstance(v, np.ndarray):
            return v # TODO
        else:
            raise ValueError("Unsupported video input type.")


    def video_real(self, v, **kwargs):
        print("Qwen3_VL_8B_Instruct.load_video:", v, "frame_rates:", kwargs.get("frame_rates",-1), "num_segments:", kwargs.get("num_segments",-1))
        from decord import VideoReader, cpu
        import torch, numpy as np
        vr = VideoReader(v, ctx=cpu(0), num_threads=1)
        total_frames = len(vr)
        fps = float(vr.get_avg_fps())


        frame_rates = kwargs.get("frame_rates", 8)
        num_segments = kwargs.get("num_segments", -1)
    
        
        indices = np.linspace(0, total_frames - 1, frame_rates).astype(int)
        
        print("Qwen3_VL_8B_Instruct.parsed:", v, "frame_rates:", frame_rates, "num_segments:", num_segments, "total_frames:", total_frames, "len(indices):", len(indices))  
        

        frames = []
        start_index = indices[0]
        end_index = indices[-1]
        print("Qwen3_VL_8B_Instruct.load_video","start_index:", start_index, "end_index:", end_index)
        for frame_index in indices:
            frame_np = vr[frame_index].asnumpy()
            frame_resized = self.resize_frame(frame_np)
            frames.append(np.array(frame_resized, dtype=np.float32))
           
        print("Qwen3_VL_8B_Instruct.load_video","num_segments:", len(frames), "fps:", frame_rates, "max_frame:", len(indices), "len(frames):", len(frames))

        
        clip = np.stack(frames) / 255.0  # 0-1 float32
        clip = clip.transpose(0, 3, 1, 2)  # (T, H, W, 3) -> (T, 3, H, W)
        print("type of clip:", type(clip), "shape of clip:", clip.shape)
        return clip
  
       
    

    def text(self, t):
        return t

    def __call__(self, item, **kwargs):
        if list(item.keys()) == ["text"]:
            return {"text": self.text(item["text"])}
        elif list(item.keys()) == ["image"]:
            return {"image": self.image(item["image"])}
        elif list(item.keys()) == ["video"]:
            return {"video": self.video(item["video"], **kwargs)}
        else:
            raise ValueError("LLaVA_NeXT_Video_7B_hf_Formater.__call__: Unsupported item type.")


class LLaVA_NeXT_Video_7B_hf(AModel):
    def __init__(self, model_dir):
        
        #这个是模型类的构造函数，
        
        #其实只需要弄一个model_dir参数就行了，其他参数和模型本身有关吗？
        
        
        from transformers import LlavaNextVideoProcessor, LlavaNextVideoForConditionalGeneration
        import torch, os
        #"llava-hf/LLaVA-NeXT-Video-7B-hf"
        model_id = model_dir if model_dir.endswith("LLaVA-NeXT-Video-7B-hf") else os.path.join(model_dir, "LLaVA-NeXT-Video-7B-hf")

        self.model = LlavaNextVideoForConditionalGeneration.from_pretrained(model_id, torch_dtype=torch.float16, low_cpu_mem_usage=True).to(0)
        self.processor = LlavaNextVideoProcessor.from_pretrained(model_id)
        self.formater = LLaVA_NeXT_Video_7B_hf_Formater()

    def __call__(self, input_data):
        kwargs = input_data
        #input_data : dict
            #input_data["content"]: list
            # Each value in "content" has to be a list of dicts with types ("text", "image", "video")
        assert isinstance(input_data, dict), "input_data must be a dict"
        assert "content" in input_data and isinstance(input_data["content"], list), "input_data['content'] must be a list"
        assert list(input_data["content"][0].keys())==['text'] and list(input_data["content"][1].keys())==['video'], "Although our model should support text+image+video input, currently we only support text+video input for simplicity."
        frame_rates = kwargs.get("frame_rates", 8)
        max_new_tokens = kwargs.get("max_new_tokens", 100)
        do_sample = kwargs.get("do_sample", False)
        

        content = [self.formater(c, **kwargs) for c in input_data["content"]]
        
        conversation = [
            {"role": "user", "content": [ {"type": "text", "text": content[0]['text']}, {"type": "video","video": content[1]['video']}]}
        ]
        prompt = self.processor.apply_chat_template(conversation, add_generation_prompt=True)
        import torch
        clip = content[1]['video']
        clip_tensor = torch.from_numpy(clip).float()
        clip_tensor = clip_tensor.to(self.model.device, dtype=torch.float16)
        inputs_video = self.processor(text=prompt, videos=clip_tensor, padding=True, return_tensors="pt").to(self.model.device)
        output = self.model.generate(**inputs_video, max_new_tokens=max_new_tokens, do_sample=do_sample)
        full_decoded = self.processor.decode(output[0], skip_special_tokens=True)
        final_answer = full_decoded.split("ASSISTANT:")[-1].strip()
        return final_answer