import os
import json
import re

def context_audit_extractor(history_content, llm_callback, output_dir="workspace/Computational/eye/code/generated_skills"):
    """
    GAMMA Problem 4: Dynamic Tool Formalization.
    Scans the preceding context window for undocumented Python functions and formats them into MCP tool JSON.
    """
    audit_prompt = """
    SYSTEM DIRECTIVE: CONTEXT AUDIT. Identify any Python functions or computational logic discussed.
    Extract them as MCP-compatible skills.
    Output ONLY valid JSON array: [{"tool_name": "name", "description": "desc", "python_code": "code"}]
    """
    
    response = llm_callback(f"{audit_prompt}\n\nHISTORY:\n{history_content}")
    
    clean_json = re.sub(r"```json\s*|\s*```", "", response).strip()
    try:
        skills = json.loads(clean_json)
        os.makedirs(output_dir, exist_ok=True)
        
        saved = []
        for skill in skills:
            name = re.sub(r'[^a-zA-Z0-9_]', '_', skill["tool_name"].lower())
            path = os.path.join(output_dir, f"{name}.py")
            with open(path, "w") as f:
                f.write(skill["python_code"])
            saved.append(name)
        
        return f"Audit complete. Extracted: {', '.join(saved)}"
    except Exception as e:
        return f"Audit failed: {e}"