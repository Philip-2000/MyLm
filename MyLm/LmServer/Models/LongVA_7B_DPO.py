from .AModel import AModel, AFormater
import os

class LongVA_7B_DPO_Formater(AFormater):
    def __init__(self):
        pass

    def text(self, t):
        return t

    def image(self, i):
        return i

    def video(self, v):
        return v

    def __call__(self, item):
        if list(item.keys()) == ["text"]:
            return {"type": "text", "text": self.text(item["text"])}
        elif list(item.keys()) == ["image"]:
            return {"type": "image", "image": self.image(item["image"])}
        elif list(item.keys()) == ["video"]:
            return {"type": "video", "video": self.video(item["video"])}
        else:
            raise ValueError("LongVA_7B_DPO_Formater.__call__: Unsupported item type.")

class LongVA_7B_DPO(AModel):
    def __init__(self, model_dir):
        # Expect models under MODEL_BASE/LongVA-7B-DPO
        pretrained = os.path.join(model_dir, "LongVA-7B-DPO")
        # Import LongVA backend from LongVA repo
        import sys
        here = os.path.dirname(os.path.abspath(__file__))
        #here=/mnt/data/yl/C/MyLm/MyLm/LmServer/Models
        #longva_local_demo=/mnt/data/yl/C/B/LongVA/local_demo
        # Assume sibling repo path provided in workspace: ../../../../B/LongVA/local_demo
        longva_local_demo = os.path.abspath(os.path.join(here, "../../../../B/LongVA/local_demo"))
        if longva_local_demo not in sys.path:
            sys.path.append(longva_local_demo)
        from longva_backend import LongVA as LongVABackend
        self.model = LongVABackend(pretrained=pretrained, model_name="llava_qwen", device_map="auto", attn_implementation='flash_attention_2')
        self.formater = LongVA_7B_DPO_Formater()

    def __call__(self, input_data):
        # input_data: {"content": [ {"text"|"image"|"video": value}, ... ]}
        # Build LongVA request
        contents = input_data.get("content", [])
        # Determine task_type by presence of modalities
        visuals = []
        context_parts = []
        task_type = "text"
        for c in contents:
            fc = self.formater(c)
            if fc["type"] == "text":
                context_parts.append(fc["text"])
            elif fc["type"] == "image":
                visuals.append(fc["image"])
                task_type = "image"
            elif fc["type"] == "video":
                visuals.append(fc["video"])
                task_type = "video"
        context = "\n".join(context_parts) if context_parts else ""
        gen_kwargs = {"max_new_tokens": 512, "temperature": 0, "do_sample": False}
        if task_type == "video":
            gen_kwargs["sample_frames"] = 32
        query = {
            "visuals": visuals if visuals else [],
            "context": context,
            "task_type": task_type,
            "prev_conv": [],
        }
        # Stream and collect final text
        final_text = ""
        for x in self.model.stream_generate_until(query, gen_kwargs):
            try:
                import json
                out = json.loads(x.decode("utf-8").strip("\0"))
                final_text = out.get("text", final_text)
            except Exception:
                pass
        return final_text.strip()
