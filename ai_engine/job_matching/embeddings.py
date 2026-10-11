"""
==========================================================
AI Engine Job Matching - Embeddings
==========================================================
"""

from typing import List

def get_text_embedding(text: str) -> List[float]:
    # Deterministic fallback vector representation
    return [round((hash(text + str(i)) % 1000) / 1000.0, 4) for i in range(16)]
