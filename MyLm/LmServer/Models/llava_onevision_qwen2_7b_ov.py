from .AModel import AModel, AFormater
import os
from PIL import Image

class llava_onevision_qwen2_7b_ov_Formater(AFormater):
    def __init__(self):
        pass

    def video(self, v, **kwargs):
        if isinstance(v, str):
            if not os.path.exists(v):
                # 文件不存在时返回 None（也可以根据需求返回空数组等）
                print(f"Warning: Video path {v} does not exist, continue without video")
                return np.empty((0, 3, 224, 224), dtype=np.uint8)
            return self.video_real(v, **kwargs)
        elif isinstance(v, np.ndarray):
            return v
        else:
            raise ValueError("Unsupported video input type.")

    def video_real(self, v, **kwargs):
        from decord import VideoReader, cpu
        import numpy as np
        
        max_frames_num = kwargs.get("frame_rates", 64)
        fps = kwargs.get("fps",1)
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


class llava_onevision_qwen2_7b_ov(AModel):
    def __init__(self, model_dir):
        model_id = model_dir if model_dir.endswith("llava-onevision-qwen2-7b-ov") else os.path.join(model_dir, "llava-onevision-qwen2-7b-ov")
        model_name, device_map, device, llava_model_args = "llava_qwen", "auto", "cuda", {"multimodal": True, "attn_implementation": "sdpa"}
        
        from llava.model.builder import load_pretrained_model
        self.tokenizer, self.model, self.image_processor, _ = load_pretrained_model(model_id, None, model_name, device_map=device_map, **llava_model_args)
        self.model.eval()
        self.formater = llava_onevision_qwen2_7b_ov_Formater()

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
        input_ids = tokenizer_image_token(prompt_question, self.tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt").unsqueeze(0).to("cuda")

        video = [self.image_processor.preprocess(content[1]['video'], return_tensors="pt")["pixel_values"].cuda().half()]
        
        cont = self.model.generate(
            input_ids, images=video, modalities= ["video"],
            do_sample=do_sample, temperature=0, max_new_tokens=max_new_tokens,
        )
        return self.tokenizer.batch_decode(cont, skip_special_tokens=True)[0].strip()