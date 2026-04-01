import subprocess
import requests
import base64
import json
import time
import os
import sys

# Constants for GAMMA Protocol
ALIAS_PATH = os.path.expanduser("~/.lmstudio/models/mlx_models_alias")
WAREHOUSE_PATH = "/Users/hamednejat/workspace/Warehouse/mlx_models/lm_studio_format"

def resolve_lms_alias_model(model_name_prefix):
    """
    Verifies the alias path and resolves the exact model identifier 
    required by LM Studio, specifically filtering for the alias namespace.
    """
    if not os.path.exists(ALIAS_PATH):
        print(f"CRITICAL ERROR: LM Studio alias path {ALIAS_PATH} is broken or missing.")
        # Trigger user decision router logic (mocked here for the script's scope)
        print("Please ensure the Warehouse drive is mounted and 'Full Disk Access' is granted.")
        return None

    try:
        result = subprocess.run(["lms", "ls", "--json"], capture_output=True, text=True, check=True)
        models = json.loads(result.stdout)
        
        # Priority 1: Search specifically within the alias namespace
        for model in models:
            identifier = model.get("identifier", "")
            if "mlx_models_alias" in identifier and model_name_prefix.lower() in identifier.lower():
                return identifier
        
        # Priority 2: Fallback to absolute warehouse path loading if lms identifies it directly
        for model in models:
            path = model.get("path", "")
            if WAREHOUSE_PATH in path and model_name_prefix.lower() in path.lower():
                return model.get("identifier")

        return None
    except Exception as e:
        print(f"Error during model resolution: {e}")
        return None

def load_lms_vlm(model_name_prefix="qwen3.5-vl", port=4474, context_input=131072):
    """Starts the LMS server and loads the specified vision model via the GAMMA alias resolver."""
    print(f"Starting LM Studio server on port {port}...")
    subprocess.Popen(["lms", "server", "start", "--port", str(port)], stdout=subprocess.DEVNULL)
    time.sleep(3) 
    
    print(f"Resolving model identifier for prefix: {model_name_prefix}...")
    target_model = resolve_lms_alias_model(model_name_prefix)
    
    if not target_model:
        print(f"FAILED: Model matching prefix '{model_name_prefix}' not found in {ALIAS_PATH}.")
        return False
            
    print(f"Loading model via identifier: {target_model}...")
    try:
        subprocess.run([
            "lms", "load", target_model, 
            "--gpu", "max", 
            "--context-length", str(context_input),
            "--ttl", "900" 
        ], check=True)
        return True
    except Exception as e:
        print(f"Failed to load model: {e}")
        return False

def get_lms_vlm_query(file_path, query="Describe the location of each object in this image relative to each other, and tell if is there a overlap or collision between boxes in image", min_tokens=10, max_tokens=1000, port=4474):
    """Encodes an image and queries the local vision model."""
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
        
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    mime_type = "image/png" if file_path.lower().endswith('.png') else "image/jpeg"
    data_uri = f"data:{mime_type};base64,{encoded_string}"
    
    constrained_query = f"{query}\n\nConstraint: Your response must be strictly between {min_tokens} and {max_tokens} words."
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": constrained_query},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]
            }
        ],
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
    """Unloads all models currently active in LM Studio to free VRAM."""
    print("Unloading all models from VRAM...")
    try:
        subprocess.run(["lms", "unload", "--all"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to unload models: {e}")
        return False
