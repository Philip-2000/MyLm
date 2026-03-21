from .AModel import AModel, AFormater
import os
import logging
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np


class Qwen3_VL_Embedding_2B_Formater(AFormater):
    def __init__(self):
        super().__init__()
        pass
    
    # def text(self, t):
    #     return t
    
    # def image(self, i):
    #     return i
    
    def __call__(self, query):
        if isinstance(query, str):
            query = [query]
        if isinstance(query, list):
            for i, q in enumerate(query):
                if isinstance(q, str):
                    query[i] = {"image": q} if os.path.exists(q) and q.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) else {"text": q}
                elif isinstance(q, dict):
                    assert "text" in q or "image" in q and len(q)==1, "Each query dict must contain either 'text' or 'image' key."
                    assert "text" not in q or isinstance(q["text"], str), "The 'text' value must be a string."
                    assert "image" not in q or (isinstance(q["image"], str) and os.path.exists(q["image"]) and q["image"].endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))), "The 'image' value must be a valid image file path."
                else:
                    raise ValueError("Unsupported query type in list: {}".format(type(q)))
        print("query", query)
        return query

class Qwen3_VL_Embedding_2B(AModel):
    def __init__(self, model_dir):
        
        S = "Qwen3-VL-Embedding-2B"
        from .. import GLOBAL_CONFIG
        T = S.replace("2B", GLOBAL_CONFIG[S]["par"])
        model_id = model_dir.replace(S, T) if model_dir.endswith(S) else os.path.join(model_dir, T)

        super().__init__()
        self.formater = Qwen3_VL_Embedding_2B_Formater()
        from models.qwen3_vl_embedding import Qwen3VLEmbedder
        self.model = Qwen3VLEmbedder(model_name_or_path=model_id)
    
    def __call__(self, input_data):
        result = self.model.process(self.formater(input_data["content"]))
        if hasattr(result, "detach"): result = result.detach().cpu().numpy()
        return result.tolist()

        # kwargs = input_data
        # #assert list(input_data["content"][0].keys())==['text'] and list(input_data["content"][1].keys())==['video'], "Although our model should support text+image+video input, currently we only support text+video input for simplicity."
        # print("Qwen3_VL_8B_Instruct.__call__", "frame_rates:", kwargs.get("frame_rates",-1))
        # messages = [
        #     {"role": "user", "content": [self.formater(c, **kwargs) for c in input_data["content"]]}
        # ]

        # # Preparation for inference #, fps=24，
        # inputs = self.processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt", fps=24).to(self.model.device)
        
        # # Inference: Generation of the output
        # generated_ids = self.model.generate(**inputs, max_new_tokens=1024)
        # generated_ids_trimmed = [ out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids) ]
        # return self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()

