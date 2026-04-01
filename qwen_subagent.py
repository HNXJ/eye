import subprocess
import requests
import base64
import json
import time
import os
import sys

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
            
        print(f"Loading model: {target_model} with context size {context_input} and TTL of 10 minutes...")
        subprocess.run([
            "lms", "load", target_model, 
            "--gpu", "max", 
            "--context-length", str(context_input),
            "--ttl", "600" # Set TTL to 10 minutes (600 seconds)
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

def parse_input():
    args = sys.argv[1:] # Get arguments excluding the script name

    if not args:
        print("Usage: python qwen_subagent.py <command> [args...]")
        return

    command = args[0]

    if command == "/eye":
        if len(args) == 4:
            image_path = args[1]
            try:
                min_words = int(args[2])
                max_words = int(args[3])
            except ValueError:
                print("Error: min_words and max_words must be integers.")
                return

            # Basic validation for image path existence
            if not os.path.exists(image_path):
                print(f"Error: Image file not found at {image_path}")
                return

            description = get_lms_vlm_query(image_path, min_tokens=min_words, max_tokens=max_words) # Corrected function call
            print(description)
        else:
            print("Usage: python qwen_subagent.py /eye <image_path> <min_words> <max_words>")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    parse_input()
