import requests
import json
import subprocess
import time
import os
from .optimizer import optimize_asset_tool

VLM_PORT = 4474

def mlx_lms_eye_local(image_path, prompt="Describe this image.", min_tokens=10, max_tokens=1000):
    """
    GAMMA Problem 1: Multimodal Ingestion.
    Routes visual data to local Qwen-VL via LM Studio on port 4474.
    """
    asset_data = optimize_asset_tool(image_path)
    if not asset_data: return f"Error: Failed to process asset {image_path}"

    url = f"http://localhost:{VLM_PORT}/v1/chat/completions"
    
    # Image vs Text routing
    if len(asset_data) < 50000 and not asset_data.startswith("data:"):
        # Likely sanitized SVG/HTML text
        messages = [{"role": "user", "content": f"Context: {asset_data}\nTask: {prompt}"}]
    else:
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": f"{prompt}\nConstraint: {min_tokens}-{max_tokens} words."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{asset_data}"}}
            ]
        }]

    payload = {
        "model": "qwen3.5-vl-4b-mlx-crack", # Default identifier
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": max_tokens
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"VLM Error: {e}"
