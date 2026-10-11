"""
==========================================================
AI Engine Resume - DOCX Reader
==========================================================
"""

from pathlib import Path
import docx

def read_docx(file_path: Path) -> str:
    doc = docx.Document(str(file_path))
    return "\n".join([p.text for p in doc.paragraphs if p.text])
