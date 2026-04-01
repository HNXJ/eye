import subprocess
import requests
import base64
import json
import time
import os
from PIL import Image
from io import BytesIO

def load_lms_vlm(model_name_prefix="qwen3.5-vl", port=4474, context_input=131072):
    """Starts the LMS server and loads the specified vision model."""
    print(f"Starting LM Studio server on port {port}...")
    subprocess.Popen(["lms", "server", "start", "--port", str(port)], stdout=subprocess.DEVNULL)
    time.sleep(3)
    
    try:
        result = subprocess.run(["lms", "ls", "--json"], capture_output=True, text=True, check=True)
        models = json.loads(result.stdout)
        target_model = next((m["identifier"] for m in models if model_name_prefix.lower() in m.get("identifier", "").lower()), None)
        
        if not target_model:
            raise ValueError(f"No model found matching prefix: {model_name_prefix}")
            
        print(f"Loading model: {target_model}...")
        subprocess.run(["lms", "load", target_model, "--gpu", "max", "--context-length", str(context_input)], check=True)
        return True
    except Exception as e:
        print(f"Failed to load model: {e}")
        return False

def optimize_asset(file_path, max_edge=1024):
    """Sanitizes and resizes images before encoding."""
    if not os.path.exists(file_path): return None
    img = Image.open(file_path)
    if max(img.size) > max_edge:
        img.thumbnail((max_edge, max_edge))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_lms_vlm_query(file_path, query="Describe this image", min_tokens=10, max_tokens=1000, port=4474):
    """Encodes an image and queries the local vision model."""
    encoded_string = optimize_asset(file_path)
    if not encoded_string: return f"Error: File {file_path} not found."
        
    payload = {
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": f"{query}\nConstraint: Strictly {min_tokens}-{max_tokens} words."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_string}"}}
            ]
        }],
        "temperature": 0.1,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(f"http://localhost:{port}/v1/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Inference failed: {e}"

def unload_lms_vlm():
    """Unloads all models from VRAM."""
    try:
        subprocess.run(["lms", "unload", "--all"], check=True)
        return True
    except: return False
