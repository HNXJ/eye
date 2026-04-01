# Eye: Local Vision Interceptor for CLI

This repository contains the local multimodal processing engine for command-line visual reasoning. It relies on LM Studio (`lms`) to host vision-language models (like Qwen-VL) entirely on local hardware.

## Structure
* `/code/`: Core Python execution scripts.
* `/config/`: State constraints and model default parameters.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/HNXJ/eye.git # Replace with actual repo URL if different
    cd eye
    ```
    *(Note: The actual repository URL for the 'eye' project might differ. Currently, the script `qwen_subagent.py` is located at `/Users/hamednejat/workspace/Warehouse/Repositories/eye/`)*

2.  **Ensure Python dependencies are met:**
    *   Python 3 is recommended.
    *   Required libraries: `requests`, `Pillow`. Install them if not present:
        ```bash
        pip install requests Pillow
        ```

## Usage

The `qwen_subagent.py` script acts as the interface for image analysis.

### `/eye` Command

This command uses the local VLM to analyze an image and provide a description.

**Syntax:**
```bash
python qwen_subagent.py /eye <image_path> <min_words> <max_words>
```

**Arguments:**
*   `<image_path>`: The absolute or relative path to the image file (e.g., `/Users/hamednejat/workspace/misc/images/Screenshot 2026-04-01 at 1.03.33 PM.png`). Ensure the path is enclosed in quotes if it contains spaces.
*   `<min_words>`: The minimum number of words for the description (integer).
*   `<max_words>`: The maximum number of words for the description (integer).

**Example:**
```bash
python qwen_subagent.py /eye "/Users/hamednejat/workspace/misc/images/Screenshot 2026-04-01 at 1.03.33 PM.png" 50 100
```

### VLM Model Management

Models are loaded with a 10-minute TTL (600 seconds) by default. They will unload automatically after this period. Explicit unloading can be performed if needed by invoking `lms unload --all` or similar commands manually.

## Functions Exposed:

*   **`load_lms_vlm(...)`**: Starts the LM Studio server and loads the specified vision model with TTL.
*   **`get_lms_vlm_query(...)`**: Encodes an image and queries the local vision model for a description.
*   **`unload_lms_vlm()`**: Unloads all models currently active in LM Studio to free VRAM.

---
**Note on Current VLM State:**
The `get_lms_vlm_query` function currently uses a simulated response. To enable actual image analysis, this placeholder function needs to be replaced with code that interacts with LM Studio's API.
