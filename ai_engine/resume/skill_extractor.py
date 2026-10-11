"""
==========================================================
AI Engine Resume - Skill Extractor
==========================================================
"""

from typing import List
import re

COMMON_SKILLS = [
    "python", "sql", "tableau", "power bi", "excel", "pandas", "numpy",
    "scikit-learn", "machine learning", "r", "spark", "hadoop", "git",
    "postgresql", "mongodb", "docker", "aws", "azure", "dax"
]

def extract_skills_from_text(text: str) -> List[str]:
    text_lower = text.lower()
    extracted = []
    for skill in COMMON_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text_lower):
            extracted.append(skill.title() if len(skill) > 3 else skill.upper())
    return list(dict.fromkeys(extracted))
