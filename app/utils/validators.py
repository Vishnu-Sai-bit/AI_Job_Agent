"""
==========================================================
AI Job Copilot - App Input Validators
==========================================================
"""

import re
from typing import Tuple

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip())) if email else False

def validate_resume_file(filename: str, max_size_bytes: int = 10 * 1024 * 1024) -> Tuple[bool, str]:
    allowed = {".pdf", ".docx", ".doc", ".txt"}
    if not any(filename.lower().endswith(ext) for ext in allowed):
        return False, "File format not supported. Please upload a PDF or DOCX file."
    return True, "Valid"
