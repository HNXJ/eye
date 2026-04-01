from .ingestion import mlx_lms_eye_local

def mlx_lms_view(image_path, user_instructions):
    """
    GAMMA Problem 2: Preserving Scientific Data Integrity.
    Analyzes visual outputs (plots, circuits) vs. user instructions.
    Logic: Feedback loop -> analyze errors -> source code patch -> execute -> verify.
    """
    analysis_prompt = f"""
    SCIENTIFIC VISUAL AUDIT:
    User Instruction: {user_instructions}
    Identify any structural, labeling, or coordinate discrepancies in this visual output.
    Return only the technical critique needed to fix the underlying source code (Matplotlib/JAX).
    """
    
    critique = mlx_lms_eye_local(image_path, analysis_prompt)
    return critique

def execute_visual_patch(vlm_critique, source_script_path, llm_callback):
    """
    Bridges VLM critique to a standard text LLM to generate a code patch.
    Ensures that visual fixes are code-driven, preserving mathematical integrity.
    """
    with open(source_script_path, "r") as f:
        source_code = f.read()
    
    patch_prompt = f"""
    The following source code generated a figure with visual errors.
    VLM CRITIQUE: {vlm_critique}
    SOURCE CODE: {source_code}
    Generate only the Python code patch to resolve the issue. Do NOT explain.
    """
    
    patch_code = llm_callback(patch_prompt)
    return patch_code
