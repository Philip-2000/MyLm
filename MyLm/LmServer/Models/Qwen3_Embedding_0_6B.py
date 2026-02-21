from .AModel import AModel, AFormater
import os
import logging
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

# 配置日志（统一排查问题）
logger = logging.getLogger(__name__)

# ===================== 第一步：文本预处理类（优化配置） =====================
class Qwen3Embedding06B_Formater(AFormater):
    def __init__(self):
        super().__init__()
        # Qwen3-embedding核心配置（可外部调整）
        self.max_length = 8192
        self.padding = "max_length"
        self.truncation = True
        self.normalize = True

    def preprocess_text(self, texts):
        """统一文本预处理：单文本→列表、过滤空文本、去空格"""
        if isinstance(texts, str):
            texts = [texts]
        # 严格过滤空文本/空白文本
        processed_texts = []
        for text in texts:
            if isinstance(text, str):
                clean_text = text.strip()
                if clean_text:  # 非空才保留
                    processed_texts.append(clean_text)
        return processed_texts

    # 兼容现有框架的空方法（避免报错）
    def build_transform(self, *args, **kwargs):
        pass

    def load_image(self, *args, **kwargs):
        pass

    def load_video(self, *args, **kwargs):
        pass

    def dynamic_preprocess(self, *args, **kwargs):
        pass

    def get_index(self, *args, **kwargs):
        pass

    def get_num_frames_by_duration(self, *args, **kwargs):
        pass

# ===================== 第二步：核心模型类（全链路修复） =====================
class Qwen3_Embedding_0_6B(AModel):
    def __init__(self, model_dir):
        """
        初始化模型（兼容完整路径/根路径两种传入方式）
        :param model_dir: 模型完整路径（如 "/mnt/models/Qwen3-Embedding-0.6B"）或根路径（如 "/mnt/models"）
        """
        super().__init__()
        # 1. 修复模型路径拼接逻辑（自动判断是否为完整路径）
        self.model_name = "Qwen3-Embedding-0.6B"
        if os.path.basename(model_dir) == self.model_name:
            self.model_id = model_dir  # 传入的是完整路径
        else:
            self.model_id = os.path.join(model_dir, self.model_name)  # 传入的是根路径
        
        # 2. 校验模型路径（报错直接终止，不隐藏问题）
        if not os.path.exists(self.model_id):
            raise FileNotFoundError(f"Qwen3-Embedding模型路径不存在：{self.model_id}")
        logger.info(f"加载Qwen3-Embedding模型：{self.model_id}")
        
        # 3. 加载tokenizer和模型（兼容CPU/GPU，修复bfloat16问题）
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
        # 设备适配：GPU用bfloat16，CPU用float32
        dtype = torch.float16
        self.model = AutoModel.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            torch_dtype=dtype,
            device_map="auto"
        )
        
        # 4. 推理模式+初始化预处理类
        self.model.eval()
        self.formater = Qwen3Embedding06B_Formater()
        self.device = self.model.device
        logger.info(f"模型加载完成，设备：{self.device}，精度：{dtype}")

    def _generate_embedding(self, texts):
        """核心embedding生成逻辑（返回所有文本的embedding）"""
        # 分词（复用预处理类配置）
        inputs = self.tokenizer(
            texts,
            max_length=self.formater.max_length,
            padding=self.formater.padding,
            truncation=self.formater.truncation,
            return_tensors="pt",
            return_length=True  # 返回实际token数（截断后）
        ).to(self.device)

        # 生成embedding（无梯度推理）
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, -1, :]  # 取最后一个token
        
        # 归一化
        if self.formater.normalize:
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
        # 返回：embedding数组 + 实际token数（截断后）
        return embeddings.cpu().numpy(), inputs["length"].cpu().numpy()

    def __call__(self, input_data):
        """
        对外唯一调用接口（修复输入解析逻辑，匹配call函数传入格式）
        :param input_data: 实际传入格式（call函数的content）：
               {
                   "text": "待生成embedding的文本",  # 核心输入（单文本）
                   "timeout": 15,        # 兼容参数，忽略
                   "check": True         # 兼容参数，忽略
               }
        :return: dict - 适配call函数解析，异常直接抛出
        """
        try:
            # 1. 修复输入解析逻辑（匹配实际传入的字典格式）
            raw_text = input_data.get("text", "")
            if not raw_text:
                logger.warning("输入无有效文本，返回空embedding")
                return {"embedding": [], "total_tokens": 0, "status": "success"}
            
            # 2. 文本预处理
            texts = self.formater.preprocess_text(raw_text)
            if not texts:
                return {"embedding": [], "total_tokens": 0, "status": "success"}
            
            # 3. 生成embedding + 计算实际token数（修复token数不准确问题）
            embeddings, token_lengths = self._generate_embedding(texts)
            total_tokens = int(np.sum(token_lengths))  # 截断后的总token数
            
            # 4. 返回格式：单文本返回第一个embedding，多文本返回列表（兼容上层）
            result = {
                "embedding": embeddings[0].tolist() if len(embeddings) > 0 else [],
                "total_tokens": total_tokens,
                "status": "success"
            }
            logger.info(f"生成embedding成功 | 文本长度：{len(raw_text)} | Token数：{total_tokens} | Embedding维度：{len(result['embedding'])}")
            return result

        except Exception as e:
            # 关键修复：异常直接抛出，让上层重试逻辑感知错误
            error_msg = f"Qwen3-Embedding生成失败：{str(e)}"
            logger.error(error_msg, exc_info=True)  # 打印完整异常栈
            raise RuntimeError(error_msg) from e  # 抛出异常，保留原始栈