import requests

# 定义服务地址和输入数据
services = {
    "Intern-Video-2_5": "http://127.0.0.1:8000/predict",
    "LLaVA-NeXT-Video": "http://127.0.0.1:8001/predict",
    "LLaVA-OneVision-Qwen2": "http://127.0.0.1:8002/predict",
    "Qwen2_5-VL-32B-Instruct": "http://127.0.0.1:8003/predict",
    "Qwen3-VL-8B-Instruct": "http://127.0.0.1:8004/predict",
}

# 示例输入数据
input_text = "测试输入数据"
input_image_path = "example.jpg"  # 替换为实际图片路径
input_video_path = "example.mp4"  # 替换为实际视频路径

# 图片预处理
import base64
from PIL import Image
import io

def preprocess_image(image_path):
    with Image.open(image_path) as img:
        img = img.resize((224, 224))  # 调整图片大小
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

# 视频预处理
import cv2

def preprocess_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (224, 224))  # 调整帧大小
        _, buffer = cv2.imencode(".jpg", frame)
        frames.append(base64.b64encode(buffer).decode("utf-8"))
    cap.release()
    return frames

# 预处理图片和视频
image_data = preprocess_image(input_image_path)
video_data = preprocess_video(input_video_path)

# 遍历所有服务并调用
for model_name, url in services.items():
    try:
        payload = {
            "input_text": input_text,
            "input_image": image_data,
            "input_video": video_data,
        }
        response = requests.post(url, json=payload)
        print(f"Model: {model_name}, Response: {response.json()}")
    except Exception as e:
        print(f"Failed to call {model_name}: {e}")