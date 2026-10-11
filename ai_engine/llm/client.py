"""
==========================================================
AI Engine LLM - Client
==========================================================
"""

from typing import Optional
from utils.llm import call_llm

class LLMClient:
    @staticmethod
    def query(prompt: str, json_format: bool = False) -> str:
        return call_llm(prompt, json_format=json_format)

llm_client = LLMClient()
