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
            exception(f"Groq API call failed: {e}")

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
            exception(f"OpenRouter API call failed: {e}")

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
            exception(f"Together AI API call failed: {e}")

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
            exception(f"Cohere API call failed: {e}")

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
            # Note: Serverless HF JSON constraint is usually done via prompting,
            # as OpenAI compatibility structure doesn't support response_format for all backend endpoints.
            
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            exception(f"Hugging Face API call failed: {e}")

    # --- 6. Try Google Gemini (Senary) ---
    if gemini_key:
        try:
            info("Calling Google Gemini API...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if json_format:
                payload["generationConfig"] = {"responseMimeType": "application/json"}
                
            response = requests.post(url, json=payload, timeout=25)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            exception(f"Gemini API call failed: {e}")

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
        raise OllamaConnectionError("Ollama server is not running.")
    except Exception as e:
        exception("Ollama request failed.")
        raise ResumeAnalyzerError(str(e))


def get_embedding(text: str) -> list[float]:
    """
    Generate vector embeddings for a given text.
    Tries Cohere or Gemini, and falls back to a clean token-level TF-IDF vectorizer if keys are missing.
    """
    cohere_key = os.getenv("COHERE_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if cohere_key:
        try:
            url = "https://api.cohere.com/v1/embed"
            headers = {
                "Authorization": f"Bearer {cohere_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "texts": [text],
                "model": "embed-english-v3.0",
                "input_type": "search_document"
            }
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()["embeddings"][0]
        except Exception as e:
            exception(f"Cohere embedding failed: {e}")

    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={gemini_key}"
            payload = {
                "content": {
                    "parts": [{"text": text}]
                }
            }
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            return response.json()["embedding"]["values"]
        except Exception as e:
            exception(f"Gemini embedding failed: {e}")

    # Fallback: Simple token-level tf-idf hash vector (length 384) to avoid external dependency issues
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
