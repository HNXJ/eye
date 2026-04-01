import os
import base64
from pathlib import Path
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

def optimize_asset_tool(file_path, max_edge=1024):
    """
    GAMMA Problem 3: Context Window Bloat & Latency.
    Sanitizes HTML/SVG and downsamples raster images to preserve VRAM and context.
    """
    path = Path(file_path)
    if not path.exists(): return None
    
    # 1. HTML/SVG Sanitization (BS4)
    if path.suffix.lower() in [".html", ".svg"]:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 2 * 1024 * 1024: # 2MB limit
            soup = BeautifulSoup(content, 'html.parser')
            for img in soup.find_all('img'): img.decompose()
            for script in soup.find_all('script'): script.decompose()
            return soup.get_text()[:10000] # Safe text extract
        return content

    # 2. Raster Downsampling (Pillow)
    if path.suffix.lower() in [".png", ".jpg", ".jpeg", ".tiff"]:
        img = Image.open(path)
        if max(img.size) > max_edge:
            img.thumbnail((max_edge, max_edge))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return None
