import requests
import json
import base64
import os
from pathlib import Path
from http import HTTPStatus

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
VIDEO_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis"
TASK_QUERY_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/tasks/"


def encode_image(image_path: str) -> str:
    """图片转base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def generate_video(first_frame_path: str, last_frame_path: str, prompt: str) -> dict:
    """
    生成换装视频（首帧+尾帧），异步模式
    返回：{"status": "running", "task_id": "..."}
          {"status": "failed", "error": "..."}
    """
    if not API_KEY:
        return {"status": "failed", "error": "MODELSTUDIO_API_KEY 环境变量未设置"}

    first_b64 = encode_image(first_frame_path)
    last_b64 = encode_image(last_frame_path)

    payload = {
        "model": "wanx2.1-kf2v-plus",
        "input": {
            "first_frame_url": f"data:image/png;base64,{first_b64}",
            "last_frame_url": f"data:image/png;base64,{last_b64}",
            "prompt": prompt
        },
        "parameters": {
            "resolution": "720P",
            "prompt_extend": False,  # 禁止模型自动扩写提示词，避免指令被稀释
            "duration": 5,  # 固定5秒
            "negative_prompt": "画面硬切，画面扭曲变形，镜头突变，跳变，多个人物，人物变形，背景变化，光影不一致，色彩失真，模糊，闪烁，穿模，转场生硬，人物残留，半身消失，换装在画面内完成，人物走出后残影仍留在画面，姿势突变，卡顿，身体残缺手部变形, 手指增多, 手指缺失, 手指融合, 手部特写, 手臂扭曲,人物残影, 人物轮廓残留, 身体局部残留, 换装过渡帧"
        }
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"  # 异步调用
    }

    try:
        resp = requests.post(VIDEO_ENDPOINT, headers=headers, data=json.dumps(payload), timeout=120)
        resp.raise_for_status()
        data = resp.json()

        if resp.status_code == HTTPStatus.OK:
            task_id = data['output']['task_id']
            return {"status": "running", "task_id": task_id}
        else:
            return {"status": "failed", "error": data}

    except requests.exceptions.RequestException as e:
        return {"status": "failed", "error": str(e)}


def query_task_status(task_id: str) -> dict:
    """
    查询视频任务状态，返回结构化结果
    返回：{"status": "success", "video_url": "..."}  （已完成）
          {"status": "running"}                       （进行中）
          {"status": "failed", "error": "..."}
    """
    if not API_KEY:
        return {"status": "failed", "error": "MODELSTUDIO_API_KEY 环境变量未设置"}

    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        resp = requests.get(f"{TASK_QUERY_ENDPOINT}{task_id}", headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        task_status = data.get("output", {}).get("task_status")
        if task_status == "SUCCEEDED":
            video_url = data.get("output", {}).get("video_url")
            return {"status": "success", "video_url": video_url}
        elif task_status == "FAILED":
            error_msg = data.get("output", {}).get("error", {}).get("message", "未知错误")
            return {"status": "failed", "error": error_msg}
        else:
            return {"status": "running"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}


def wait_for_video(task_id: str, interval: int = 30, max_wait: int = 600) -> dict:
    """
    轮询等待视频生成完成（阻塞调用，最多等待 max_wait 秒）
    返回：{"status": "success", "video_url": "..."}
          {"status": "failed", "error": "..."}
          {"status": "timeout"}
    """
    import time
    elapsed = 0
    while elapsed < max_wait:
        time.sleep(interval)
        elapsed += interval
        result = query_task_status(task_id)
        if result["status"] in ("success", "failed"):
            return result
    return {"status": "timeout"}
