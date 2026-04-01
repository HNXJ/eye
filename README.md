# Eye: Local Multimodal Vision Integration (GAMMA Architecture)

The "Eye" module provides an autonomous visual reasoning cortex for the Gemini CLI, leveraging local MLX-optimized VLMs (Qwen-VL) via LM Studio.

## Architecture
- **Inference Engine:** LM Studio (Port 4474)
- **Modality Handling:** `ingestion.py` (Conversions & Base64)
- **Asset Optimization:** `optimizer.py` (Pillow downsampling & HTML/SVG stripping)
- **Scientific Debugging:** `vision_debugger.py` (Deterministic code patches)
- **Meta-Awareness:** `reflection.py` (Context Audit & Tool Extraction)

## Standardized Tools
- `mlx_lms_eye_local`: High-level multimodal description.
- `mlx_lms_view`: Visual error analysis vs. instructions.
- `optimize_asset_tool`: Pre-inference sanitization gate.
- `context_audit_extractor`: Autonomous skill formalization.
