"""
==========================================================
AI JobAgent - Resume Optimizer Service
Author : Antigravity
==========================================================
"""

import json
import time
from typing import Dict, Any

from config import (
    OLLAMA_MAX_RETRIES,
)

from utils import (
    info,
    warning,
    exception,
    call_llm,
)

from exceptions import (
    ResumeAnalyzerError,
    OllamaConnectionError,
    InvalidAIResponseError,
)

PROMPT = """
You are an expert AI Resume Optimizer.
Your job is to analyze the resume text and the target job role, and automatically rewrite and optimize parts of the resume.

Specifically:
1. Rewrite the career summary/objective to be highly compelling for the target role.
2. Identify weaker bullet points from the experience section and rewrite them to use strong action verbs (e.g. Led, Optimized, Spearheaded) and quantified metrics where possible.
3. Suggest a list of strong action verbs suited for this target role.
4. Recommend key technical skills to learn to match this target role.

IMPORTANT RULES:
1. Return ONLY valid JSON.
2. Do NOT use markdown code blocks (do NOT wrap response in ```json).
3. Do NOT explain anything outside the JSON.
4. The response MUST begin with { and end with }.
5. Follow this JSON schema exactly:

{
    "improved_summary": "rewritten career summary here",
    "action_verbs": ["verb1", "verb2", "verb3"],
    "bullet_points_improvements": [
        {
            "original": "original bullet point",
            "improved": "improved bullet point using action verbs and metrics",
            "reason": "explanation of what makes this version stronger"
        }
    ],
    "recommended_skills": ["skill1", "skill2", "skill3"]
}

Target Role: {target_role}
Resume:
{resume_text}
"""

def call_ollama(resume_text: str, target_role: str) -> str:
    """
    Send resume and target role to LLM for optimization using unified helper.
    """
    info("Sending resume optimization request to LLM.")
    try:
        formatted_prompt = PROMPT.format(target_role=target_role, resume_text=resume_text)
        return call_llm(formatted_prompt, json_format=True)
    except Exception as e:
        exception("LLM optimization request failed.")
        raise ResumeAnalyzerError(str(e))

def clean_json(ai_response: str) -> str:
    """
    Clean JSON returned by Ollama.
    """
    if not ai_response:
        raise InvalidAIResponseError("Empty response received from AI.")

    cleaned = ai_response.strip()
    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```JSON", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise InvalidAIResponseError("No JSON object found in AI response.")

    return cleaned[start:end + 1]

def parse_json(ai_response: str) -> Dict[str, Any]:
    """
    Convert AI response into Python dictionary.
    """
    try:
        cleaned = clean_json(ai_response)
        data = json.loads(cleaned)
        return data
    except Exception as e:
        exception("Failed to parse optimizer JSON response.")
        raise InvalidAIResponseError(str(e))

def optimize_resume(resume_text: str, target_role: str) -> Dict[str, Any]:
    """
    Optimize resume summary and experience using Ollama.
    """
    info(f"Starting resume optimization for target role: {target_role}")
    
    for attempt in range(1, OLLAMA_MAX_RETRIES + 1):
        try:
            info(f"Ollama optimization attempt {attempt}")
            raw_response = call_ollama(resume_text, target_role)
            data = parse_json(raw_response)
            
            # Simple schema validation
            required = ["improved_summary", "action_verbs", "bullet_points_improvements", "recommended_skills"]
            for field in required:
                if field not in data:
                    data[field] = [] if "s" in field or "v" in field else ""
            
            return {
                "success": True,
                "target_role": target_role,
                "optimization": data
            }
        except OllamaConnectionError:
            raise
        except Exception as e:
            warning(f"Optimization attempt {attempt} failed: {e}")
            if attempt == OLLAMA_MAX_RETRIES:
                raise ResumeAnalyzerError(f"Optimization failed after {OLLAMA_MAX_RETRIES} attempts.")
            time.sleep(2)
            
    return {"success": False, "message": "Failed to optimize resume."}
