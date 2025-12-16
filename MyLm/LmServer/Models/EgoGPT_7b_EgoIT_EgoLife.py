from .AModel import AModel, AFormater
import os
import sys
import json
import torch

class EgoGPT_7b_EgoIT_EgoLife_Formater(AFormater):
    def __init__(self):
        pass
    def text(self, t):
        return t
    def image(self, i):
        return i
    def video(self, v):
        return v
    def audio(self, a):
        return a
    def __call__(self, item):
        keys = list(item.keys())
        if keys == ["text"]:
            return {"type": "text", "text": self.text(item["text"])}
        elif keys == ["image"]:
            return {"type": "image", "image": self.image(item["image"])}
        elif keys == ["video"]:
            return {"type": "video", "video": self.video(item["video"])}
        elif keys == ["audio"]:
            return {"type": "audio", "audio": self.audio(item["audio"])}
        else:
            raise ValueError("EgoGPT formatter: Unsupported item type.")

class EgoGPT_7b_EgoIT_EgoLife(AModel):
    def __init__(self, model_dir):
        # Pretrained directory path under MODEL_BASE
        self.pretrained = os.path.join(model_dir, "EgoGPT-7b-EgoIT-EgoLife")
        # Make EgoGPT repo importable
        here = os.path.dirname(os.path.abspath(__file__))
        egogpt_repo = os.path.abspath(os.path.join(here, "../../../B/EgoLife/EgoGPT"))
        if egogpt_repo not in sys.path:
            sys.path.append(egogpt_repo)
        from egogpt.model.builder import load_pretrained_model
        from egogpt.constants import IMAGE_TOKEN_INDEX, SPEECH_TOKEN_INDEX
        from egogpt.conversation import conv_templates
        from egogpt.mm_utils import process_images
        from PIL import Image
        import numpy as np
        from decord import VideoReader, cpu
        import soundfile as sf
        import whisper
        from scipy.signal import resample

        # Store refs used in call
        self._load_pretrained_model = load_pretrained_model
        self._IMAGE_TOKEN_INDEX = IMAGE_TOKEN_INDEX
        self._SPEECH_TOKEN_INDEX = SPEECH_TOKEN_INDEX
        self._conv_templates = conv_templates
        self._process_images = process_images
        self._VideoReader = VideoReader
        self._cpu = cpu
        self._Image = Image
        self._np = np
        self._sf = sf
        self._whisper = whisper
        self._resample = resample

        # Load model
        self.tokenizer, self.model, self.max_length = self._load_pretrained_model(self.pretrained, device_map="cuda")
        self.model.eval()
        self.formater = EgoGPT_7b_EgoIT_EgoLife_Formater()

    def _load_video_and_audio(self, video_path=None, audio_path=None, max_frames_num=16, fps=1):
        if audio_path is not None:
            speech, sample_rate = self._sf.read(audio_path)
            if sample_rate != 16000:
                target_length = int(len(speech) * 16000 / sample_rate)
                speech = self._resample(speech, target_length)
            if getattr(speech, "ndim", 1) > 1:
                speech = self._np.mean(speech, axis=1)
            speech = self._whisper.pad_or_trim(speech.astype(self._np.float32))
            speech = self._whisper.log_mel_spectrogram(speech, n_mels=128).permute(1, 0)
            speech_lengths = torch.LongTensor([speech.shape[0]])
        else:
            speech = torch.zeros(3000, 128)
            speech_lengths = torch.LongTensor([3000])
        vr = self._VideoReader(video_path, ctx=self._cpu(0), num_threads=1)
        total_frame_num = len(vr)
        avg_fps = max(1, round(vr.get_avg_fps() / fps))
        frame_idx = [i for i in range(0, total_frame_num, avg_fps)]
        if max_frames_num > 0 and len(frame_idx) > max_frames_num:
            uniform_sampled_frames = self._np.linspace(0, total_frame_num - 1, max_frames_num, dtype=int)
            frame_idx = uniform_sampled_frames.tolist()
        video = vr.get_batch(frame_idx).asnumpy()
        return video, speech, speech_lengths

    def __call__(self, input_data):
        # Parse input content
        contents = input_data.get("content", [])
        visuals_video = None
        audio_path = None
        context_parts = []
        for c in contents:
            fc = self.formater(c)
            if fc["type"] == "text":
                context_parts.append(fc["text"])
            elif fc["type"] == "video":
                visuals_video = fc["video"]
            elif fc["type"] == "audio":
                audio_path = fc["audio"]
        query = "\n".join(context_parts) if context_parts else "Please describe the video in detail."

        # Build prompt with tokens
        conv_template = "qwen_1_5"
        question = "<image>\n<speech>\n\n" + query
        conv = self._conv_templates[conv_template].copy()
        conv.append_message(conv.roles[0], question)
        conv.append_message(conv.roles[1], None)
        prompt_question = conv.get_prompt()

        # Prepare video + audio
        video, speech, speech_lengths = self._load_video_and_audio(video_path=visuals_video, audio_path=audio_path)
        device = "cuda"
        processor = self.model.get_vision_tower().image_processor
        processed_video = processor.preprocess(video, return_tensors="pt")["pixel_values"]
        image_sizes = [processed_video[0].size()[-2:]] if hasattr(processed_video[0], 'size') else [video[0].shape[:2][::-1]]
        image_tensor = [processed_video.half().cuda()]

        # Tokenize with special indices
        parts = ["<image>", "<speech>", prompt_question.replace("<image>", "").replace("<speech>", "")] 
        input_ids = []
        for part in parts:
            if part == "<image>":
                input_ids.append(self._IMAGE_TOKEN_INDEX)
            elif part == "<speech>":
                input_ids.append(self._SPEECH_TOKEN_INDEX)
            else:
                input_ids.extend(self.tokenizer(part).input_ids)
        input_ids = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0).to(device)

        # Generate
        cont = self.model.generate(
            input_ids,
            images=image_tensor,
            image_sizes=image_sizes,
            speech=speech.to(device).half(),
            speech_lengths=speech_lengths,
            do_sample=False,
            temperature=0.5,
            max_new_tokens=1024,
            modalities=["video"],
            eos_token_id=self.tokenizer.eos_token_id,
        )
        text_outputs = self.tokenizer.batch_decode(cont, skip_special_tokens=True)
        return text_outputs[0].strip() if text_outputs else ""
