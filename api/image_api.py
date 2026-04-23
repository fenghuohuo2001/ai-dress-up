import requests
import json
import base64
import os
from pathlib import Path

# API Key 读取：环境变量优先，否则从 ~/.modelstudio_env 读取
API_KEY = os.environ.get("MODELSTUDIO_API_KEY", "")
if not API_KEY:
    env_file = Path.home() / ".modelstudio_env"
    if env_file.exists():
        for line in env_file.read_text().strip().split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "MODELSTUDIO_API_KEY":
                    API_KEY = v.strip()
                    break
IMAGE_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
TASK_QUERY_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/tasks/"


def encode_image(image_path: str) -> str:
    """将图片转为base64编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def generate_dress_image(char_image_path: str, cloth_image_path: str, prompt: str) -> dict:
    """
    生成换装图（双参考图）
    返回：{"status": "success", "image_url": "...", "task_id": None}
          {"status": "running", "task_id": "..."}  （异步模式）
          {"status": "failed", "error": "..."}
    """
    if not API_KEY:
        return {"status": "failed", "error": "MODELSTUDIO_API_KEY 环境变量未设置"}

    char_b64 = encode_image(char_image_path)
    cloth_b64 = encode_image(cloth_image_path)

    payload = {
        "model": "qwen-image-2.0-pro",
        "input": {
            "messages": [{
                "role": "user",
                "content": [
                    {"image": f"data:image/png;base64,{char_b64}"},
                    {"image": f"data:image/jpeg;base64,{cloth_b64}"},
                    {"text": prompt}
                ]
            }]
        },
        "parameters": {
            "n": 1,
            "size": "1024*1024",
            "watermark": False,
            "negative_prompt": "人物变形,面容改变,五官变化,发型改变,姿势改变,动作变化,背景变化,场景改变,光影突变,角度变化,透视变化,构图改变,多人,重复人物,多余物体,杂物,文字,水印,模糊,低清,噪点,服装残缺,服装穿模,颜色偏移,风格突变,身体畸变,手部畸形,比例失调"
        }
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(IMAGE_ENDPOINT, headers=headers, data=json.dumps(payload), timeout=90)
        resp.raise_for_status()
        data = resp.json()

        if resp.status_code == 200:
            # 同步返回：直接拿到图片URL
            image_url = data['output']['choices'][0]['message']['content'][0]['image']
            return {"status": "success", "image_url": image_url, "task_id": None}
        else:
            return {"status": "failed", "error": data}

    except requests.exceptions.RequestException as e:
        return {"status": "failed", "error": str(e)}


def generate_image(prompt: str) -> dict:
    """
    纯文字生成图片（无参考图，用于生成角色原始形象）
    返回：{"status": "success", "image_url": "...", "task_id": None}
          {"status": "failed", "error": "..."}
    """
    if not API_KEY:
        return {"status": "failed", "error": "MODELSTUDIO_API_KEY 环境变量未设置"}

    payload = {
        "model": "qwen-image-2.0-pro",
        "input": {
            "messages": [{
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }]
        },
        "parameters": {
            "n": 1,
            "size": "1024*1024",
            "watermark": False,
            "negative_prompt": "多人,重复人物,畸变,模糊,低清,水印,文字,比例失调,手部畸形,多手指,断肢,背景杂乱,风格不统一,肢体扭曲,穿模"
        }
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(IMAGE_ENDPOINT, headers=headers, data=json.dumps(payload), timeout=90)
        resp.raise_for_status()
        data = resp.json()
        if resp.status_code == 200:
            image_url = data['output']['choices'][0]['message']['content'][0]['image']
            return {"status": "success", "image_url": image_url, "task_id": None}
        else:
            return {"status": "failed", "error": data}
    except requests.exceptions.RequestException as e:
        return {"status": "failed", "error": str(e)}


def query_task_status(task_id: str) -> dict:
    """查询图片/视频任务状态"""
    if not API_KEY:
        return {"status": "failed", "error": "MODELSTUDIO_API_KEY 环境变量未设置"}

    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        resp = requests.get(f"{TASK_QUERY_ENDPOINT}{task_id}", headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "failed", "error": str(e)}
