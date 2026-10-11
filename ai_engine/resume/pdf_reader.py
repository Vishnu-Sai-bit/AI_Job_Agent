"""
==========================================================
AI Engine Resume - PDF Reader
==========================================================
"""

from pathlib import Path
import fitz  # PyMuPDF

def read_pdf(file_path: Path) -> str:
    text_chunks = []
    with fitz.open(str(file_path)) as doc:
        for page in doc:
            text = page.get_text()
            if text:
                text_chunks.append(text)
    return "\n".join(text_chunks)
