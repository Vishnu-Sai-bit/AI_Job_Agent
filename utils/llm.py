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
    Send prompt to LLM. Detects GROQ_API_KEY first, then GEMINI_API_KEY.
    If neither is present, falls back to local Ollama.
    """
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if groq_key:
        info("Groq API Key detected. Calling Groq API in cloud mode.")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1
        }
        if json_format:
            payload["response_format"] = {"type": "json_object"}
            
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            exception(f"Groq API request failed: {e}")
            # Try falling back to Gemini if available instead of raising immediately
            if gemini_key:
                info("Groq failed. Falling back to Gemini API.")
            else:
                raise ResumeAnalyzerError(f"Groq API request failed: {e}")

    if gemini_key:
        info("Gemini API Key detected. Calling Google Gemini API in cloud mode.")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        if json_format:
            payload["generationConfig"] = {"responseMimeType": "application/json"}
            
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            exception(f"Gemini API request failed: {e}")
            raise ResumeAnalyzerError(f"Gemini API request failed: {e}")
            
    # Fallback to local Ollama
    info("No cloud API keys found. Calling local Ollama instance.")
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    if json_format:
        payload["format"] = "json"
        
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except requests.ConnectionError:
        exception("Unable to connect to Ollama. Make sure it is running locally.")
        raise OllamaConnectionError("Ollama server is not running.")
    except Exception as e:
        exception("Ollama request failed.")
        raise ResumeAnalyzerError(str(e))
