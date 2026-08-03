"""
==========================================================
AI JobAgent - Unified LLM Service (Ollama / Gemini Hybrid)
Author : Antigravity
==========================================================
"""

import os
import requests
from config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT
from utils.logger import info, exception
from exceptions import OllamaConnectionError, ResumeAnalyzerError

def call_llm(prompt: str, json_format: bool = True) -> str:
    """
    Send prompt to LLM. Tries each cloud provider in order,
    and falls back to local Ollama if all fail or are not configured.
    """
    # 1. Gather all API keys from environment
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    together_key = os.getenv("TOGETHER_API_KEY", "").strip()
    cohere_key = os.getenv("COHERE_API_KEY", "").strip()
    hf_key = os.getenv("HF_API_KEY", "").strip() or os.getenv("HF_TOKEN", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    cloud_errors = []

    # --- 1. Try Groq (Primary) ---
    if groq_key:
        try:
            info("Calling Groq API...")
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            if json_format:
                payload["response_format"] = {"type": "json_object"}
                
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            err_msg = f"Groq API failed: {e}"
            exception(err_msg)
            cloud_errors.append(err_msg)

    # --- 2. Try OpenRouter (Secondary) ---
    if openrouter_key:
        try:
            info("Calling OpenRouter API...")
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            if json_format:
                payload["response_format"] = {"type": "json_object"}
                
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            err_msg = f"OpenRouter API failed: {e}"
            exception(err_msg)
            cloud_errors.append(err_msg)

    # --- 3. Try Together AI (Tertiary) ---
    if together_key:
        try:
            info("Calling Together AI API...")
            url = "https://api.together.xyz/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {together_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "meta-llama/Meta-Llama-3-8B-Instruct-Lite",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            if json_format:
                payload["response_format"] = {"type": "json_object"}
                
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            err_msg = f"Together AI API failed: {e}"
            exception(err_msg)
            cloud_errors.append(err_msg)

    # --- 4. Try Cohere (Quaternary) ---
    if cohere_key:
        try:
            info("Calling Cohere API...")
            url = "https://api.cohere.com/v1/chat"
            headers = {
                "Authorization": f"Bearer {cohere_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "message": prompt,
                "model": "command-r-plus",
                "temperature": 0.1
            }
            if json_format:
                payload["response_format"] = {"type": "json_object"}
                
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            response.raise_for_status()
            return response.json()["text"]
        except Exception as e:
            err_msg = f"Cohere API failed: {e}"
            exception(err_msg)
            cloud_errors.append(err_msg)

    # --- 5. Try Hugging Face Serverless (Quinary) ---
    if hf_key:
        try:
            info("Calling Hugging Face Inference API...")
            url = "https://api-inference.huggingface.co/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {hf_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "Qwen/Qwen2.5-72B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 1024
            }
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            err_msg = f"Hugging Face API failed: {e}"
            exception(err_msg)
            cloud_errors.append(err_msg)

    # --- 6. Try Google Gemini (Senary) ---
    if gemini_key:
        models_to_try = [
            "gemini-3.6-flash",
            "gemini-3.6-flash-lite",
            "gemini-2.5-flash-lite"
        ]
        for model_name in models_to_try:
            try:
                info(f"Calling Google Gemini API ({model_name})...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": 8192
                    }
                }
                if json_format:
                    payload["generationConfig"]["responseMimeType"] = "application/json"
                    
                response = requests.post(url, json=payload, timeout=60)
                if response.status_code == 429:
                    warning(f"Gemini model {model_name} hit rate limit (429). Retrying next available model...")
                    import time
                    time.sleep(1.2)
                    continue
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                err_msg = f"Gemini ({model_name}) API failed: {e}"
                exception(err_msg)
                cloud_errors.append(err_msg)

    # --- 7. Fallback to Local Ollama ---
    info("No active cloud APIs succeeded. Falling back to local Ollama.")
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    if json_format:
        payload["format"] = "json"
        
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.ConnectionError:
        exception("Unable to connect to local Ollama.")
        detail_msg = "Ollama server is not running."
        if cloud_errors:
            detail_msg += " Cloud providers attempted: " + " | ".join(cloud_errors)
        else:
            detail_msg += " No cloud API keys were configured in your environment variables."
        raise OllamaConnectionError(detail_msg)
    except Exception as e:
        exception("Ollama request failed.")
        raise ResumeAnalyzerError(str(e))


def get_embedding(text: str) -> list[float]:
    """
    Generate vector embeddings for a given text using a high-speed token hashing vectorizer.
    Runs locally in <1ms without external network calls, completely eliminating API rate limits and timeouts.
    """
    import math
    vector = [0.0] * 384
    words = text.lower().split()
    if not words:
        return vector
    for word in words:
        h = 0
        for char in word:
            h = (31 * h + ord(char)) % 384
        vector[h] += 1.0
        
    # L2 Normalization
    magnitude = math.sqrt(sum(v * v for v in vector))
    if magnitude > 0:
        vector = [v / magnitude for v in vector]
    return vector
