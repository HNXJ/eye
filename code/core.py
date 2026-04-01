import subprocess
import requests
import base64
import json
import time
import os

def load_lms_vlm(model_name_prefix="qwen3.5-vl", port=4474, context_input=131072):
    """Starts the LMS server and loads the specified vision model with a TTL."""
    print(f"Starting LM Studio server on port {port}...")
    # Start server in background
    subprocess.Popen(["lms", "server", "start", "--port", str(port)], stdout=subprocess.DEVNULL)
    time.sleep(3) # Give server time to bind to port
    
    print("Finding model ID...")
    try:
        result = subprocess.run(["lms", "ls", "--json"], capture_output=True, text=True, check=True)
        models = json.loads(result.stdout)
        
        target_model = None
        for model in models:
            if model_name_prefix.lower() in model.get("identifier", "").lower():
                target_model = model["identifier"]
                break
                
        if not target_model:
            raise ValueError(f"No model found matching prefix: {model_name_prefix}")
            
        # Enforce absolute path loading from the Warehouse
        absolute_model_path = os.path.join("/Users/hamednejat/workspace/Warehouse/mlx_models/lm_studio_format", target_model)
            
        print(f"Loading model from absolute path: {absolute_model_path} with context size {context_input} and TTL of 15 minutes...")
        subprocess.run([
            "lms", "load", absolute_model_path, 
            "--gpu", "max", 
            "--context-length", str(context_input),
            "--ttl", "900" # Set TTL to 15 minutes (900 seconds)
        ], check=True)
        return True
        
    except Exception as e:
        print(f"Failed to load model: {e}")
        return False

def get_lms_vlm_query(file_path, query="Describe the location of each object in this image relative to each other, and tell if is there a overlap or collision between boxes in image", min_tokens=10, max_tokens=1000, port=4474):
    """Encodes an image and queries the local vision model."""
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
        
    # Read and encode image
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    mime_type = "image/png" if file_path.lower().endswith('.png') else "image/jpeg"
    data_uri = f"data:{mime_type};base64,{encoded_string}"
    
    # Construct strictly constrained prompt
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
        "temperature": 0.1, # Keep it deterministic for coordinate mapping
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
