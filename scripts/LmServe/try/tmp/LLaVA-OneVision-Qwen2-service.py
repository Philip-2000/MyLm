from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import threading

# 定义输入数据模型
class InputData(BaseModel):
    input_text: str

# 初始化 FastAPI 应用
app = FastAPI()

# 启动模型的后台线程
def start_model():
    subprocess.run(["python", "LLaVA-OneVision-Qwen2.py"])

thread = threading.Thread(target=start_model, daemon=True)
thread.start()

@app.post("/predict")
async def predict(data: InputData):
    try:
        # 模拟推理逻辑，这里需要替换为实际的推理代码
        result = {"message": f"Processed: {data.input_text}"}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))