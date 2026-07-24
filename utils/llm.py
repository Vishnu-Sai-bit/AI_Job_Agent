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
    Send prompt to LLM. Detects GEMINI_API_KEY environment variable.
    If present, calls Gemini API. Otherwise, falls back to local Ollama.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
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
    else:
        info("No Gemini key found. Calling local Ollama instance.")
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
