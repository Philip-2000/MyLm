from .AModel import AModel, AFormater
import os
import logging
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

class Qwen3_Embed_0_6B_Formater(AFormater):
    def __init__(self):
        super().__init__()
        pass
    
    def __call__(self, query):
        if isinstance(query, str):
            query = [query]
        if isinstance(query, list):
            for i, q in enumerate(query):
                if isinstance(q, str):
                    query[i] = q.strip()
                else:
                    raise ValueError("Unsupported query type in list: {}".format(type(q)))
        return query

class Qwen3_Embed_0_6B(AModel):
    def __init__(self, model_dir):
        super().__init__()
        
        S = "Qwen3-Embed-0.6B"
        from .. import GLOBAL_CONFIG
        T = S.replace("0.6B", GLOBAL_CONFIG[S]["par"])
        model_id = model_dir.replace(S, T) if model_dir.endswith(S) else os.path.join(model_dir, T)
        model_id = model_id.replace("Embed", "Embedding")

        super().__init__()
        self.formater = Qwen3_Embed_0_6B_Formater()
        
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_id)
        self.formater = Qwen3_Embed_0_6B_Formater()
    
    def __call__(self, input_data):
        return self.model.encode(self.formater(input_data["content"])).tolist()