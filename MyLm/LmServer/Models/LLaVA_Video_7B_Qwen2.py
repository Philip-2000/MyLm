from .AModel import AModel, AFormater
import os
from PIL import Image

class LLaVA_Video_7B_Qwen2_Formater(AFormater):
    def __init__(self):
        pass

    def video(self, v, **kwargs):
        if isinstance(v, str):
            assert os.path.exists(v), f"Video path {v} does not exist"
            return self.video_real(v, **kwargs)
        elif isinstance(v, np.ndarray):
            return v
        else:
            raise ValueError("Unsupported video input type.")

    def video_real(self, v, **kwargs):
        from decord import VideoReader, cpu
        import numpy as np
        
        max_frames_num = 64

        fps=1
        if max_frames_num == 0:
            return np.zeros((1, 336, 336, 3))
        vr = VideoReader(v, ctx=cpu(0),num_threads=1)
        total_frame_num = len(vr)
        video_time = total_frame_num / vr.get_avg_fps()
        fps = round(vr.get_avg_fps()/fps)
        frame_idx = [i for i in range(0, len(vr), fps)]
        frame_time = [i/fps for i in frame_idx]
        if len(frame_idx) > max_frames_num or True:
            sample_fps = max_frames_num
            uniform_sampled_frames = np.linspace(0, total_frame_num - 1, sample_fps, dtype=int)
            frame_idx = uniform_sampled_frames.tolist()
            frame_time = [i/vr.get_avg_fps() for i in frame_idx]
        frame_time = ",".join([f"{i:.2f}s" for i in frame_time])
        spare_frames = vr.get_batch(frame_idx).asnumpy()
        return spare_frames
    
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


class LLaVA_Video_7B_Qwen2(AModel):
    def __init__(self, model_dir):
        model_id = model_dir if model_dir.endswith("LLaVA-Video-7B-Qwen2") else os.path.join(model_dir, "LLaVA-Video-7B-Qwen2")
        model_name = "llava_qwen"
        self.device = "cuda"
        device_map = "auto"
        import torch
        from llava.model.builder import load_pretrained_model
        self.tokenizer, self.model, self.image_processor, _ = load_pretrained_model(model_id, None, model_name, device_map=device_map)
        self.model.eval()
        self.formater = LLaVA_Video_7B_Qwen2_Formater()
    
    def __call__(self, input_data, **kwargs):
        #input_data : dict
            #input_data["content"]: list
            # Each value in "content" has to be a list of dicts with types ("text", "image", "video")
        assert isinstance(input_data, dict), "input_data must be a dict"
        assert "content" in input_data and isinstance(input_data["content"], list), "input_data['content'] must be a list"
        assert list(input_data["content"][0].keys())==['text'] and list(input_data["content"][1].keys())==['video'], "Although our model should support text+image+video input, currently we only support text+video input for simplicity."
        frame_rates = kwargs.get("frame_rates", 8)
        max_new_tokens = kwargs.get("max_new_tokens", 100)
        do_sample = kwargs.get("do_sample", False)


        content = [self.formater(c, frame_rates=frame_rates) for c in input_data["content"]]

        
        import copy
        from llava.mm_utils import get_model_name_from_path, process_images, tokenizer_image_token
        from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
        from llava.conversation import conv_templates, SeparatorStyle

        conv_template = "qwen_1_5"  # Make sure you use correct chat template for different models
        time_instruciton = "" #f"The video lasts for {video_time:.2f} seconds, and {len(video[0])} frames are uniformly sampled from it. These frames are located at {frame_time}.Please answer the following questions related to this video."
        question = DEFAULT_IMAGE_TOKEN + f"\n{time_instruciton}\n" + content[0]['text']
        conv = copy.deepcopy(conv_templates[conv_template])
        conv.append_message(conv.roles[0], question)
        conv.append_message(conv.roles[1], None)
        prompt_question = conv.get_prompt()
        input_ids = tokenizer_image_token(prompt_question, self.tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt").unsqueeze(0).to(self.device)

        video = [self.image_processor.preprocess(content[1]['video'], return_tensors="pt")["pixel_values"].cuda().half()]
        
        cont = self.model.generate(
            input_ids, images=video, modalities= ["video"],
            do_sample=do_sample, temperature=0, max_new_tokens=max_new_tokens,
        )
        return self.tokenizer.batch_decode(cont, skip_special_tokens=True)[0].strip()
        

        
"""


# pip install git+https://github.com/LLaVA-VL/LLaVA-NeXT.git
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path, process_images, tokenizer_image_token
from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN, IGNORE_INDEX
from llava.conversation import conv_templates, SeparatorStyle
from PIL import Image
import requests
import copy
import torch
import sys
import warnings
from decord import VideoReader, cpu
import numpy as np
warnings.filterwarnings("ignore")









pretrained = "/mnt/data/models/LLaVA-Video-7B-Qwen2" #"lmms-lab/LLaVA-Video-7B-Qwen2"
model_name = "llava_qwen"
device = "cuda"
device_map = "auto"
tokenizer, model, image_processor, max_length = load_pretrained_model(pretrained, None, model_name, torch_dtype="bfloat16", device_map=device_map)  # Add any other thing you want to pass in llava_model_args
model.eval()



conv_template = "qwen_1_5"  # Make sure you use correct chat template for different models
time_instruciton = f"The video lasts for {video_time:.2f} seconds, and {len(video[0])} frames are uniformly sampled from it. These frames are located at {frame_time}.Please answer the following questions related to this video."
question = DEFAULT_IMAGE_TOKEN + f"\n{time_instruciton}\nPlease describe this video in detail."
conv = copy.deepcopy(conv_templates[conv_template])
conv.append_message(conv.roles[0], question)
conv.append_message(conv.roles[1], None)
prompt_question = conv.get_prompt()
input_ids = tokenizer_image_token(prompt_question, tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt").unsqueeze(0).to(device)







video_path = "XXXX"
max_frames_num = 64

fps=1
if max_frames_num == 0:
    return np.zeros((1, 336, 336, 3))
vr = VideoReader(video_path, ctx=cpu(0),num_threads=1)
total_frame_num = len(vr)
video_time = total_frame_num / vr.get_avg_fps()
fps = round(vr.get_avg_fps()/fps)
frame_idx = [i for i in range(0, len(vr), fps)]
frame_time = [i/fps for i in frame_idx]
if len(frame_idx) > max_frames_num or True:
    sample_fps = max_frames_num
    uniform_sampled_frames = np.linspace(0, total_frame_num - 1, sample_fps, dtype=int)
    frame_idx = uniform_sampled_frames.tolist()
    frame_time = [i/vr.get_avg_fps() for i in frame_idx]
frame_time = ",".join([f"{i:.2f}s" for i in frame_time])
spare_frames = vr.get_batch(frame_idx).asnumpy()
# import pdb;pdb.set_trace()
video=spare_frames

video = image_processor.preprocess(video, return_tensors="pt")["pixel_values"].cuda().half()
video = [video]











cont = model.generate(
    input_ids,
    images=video,
    modalities= ["video"],
    do_sample=False,
    temperature=0,
    max_new_tokens=4096,
)
text_outputs = tokenizer.batch_decode(cont, skip_special_tokens=True)[0].strip()
print(text_outputs)















"""