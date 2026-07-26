"""
==========================================================
AI JobAgent - Resume Parser
Author : Beere Vishnu Sai

Description:
    Extract text from resumes.

Supported Formats
-----------------
• PDF
• DOCX
• DOC
• TXT
• RTF
• ODT

This service is responsible ONLY for extracting text.
It does NOT perform AI analysis.

Used By
-------
- resume_analyzer.py
- app.py
- Streamlit UI
==========================================================
"""

from pathlib import Path
from typing import Callable

import fitz
import textract
from docx import Document
from odf.opendocument import load
from odf import text
from striprtf.striprtf import rtf_to_text

from config import (
    SUPPORTED_RESUME_FORMATS,
    MAX_RESUME_TEXT_LENGTH,
)

from utils import (
    info,
    warning,
    exception,
)

from exceptions import ResumeParserError


# ==========================================================
# PDF Parser
# ==========================================================

def extract_pdf(file_path: Path) -> str:
    """
    Extract text from PDF with 2-column block sorting and scanned PDF check.
    """

    info(f"Reading PDF: {file_path.name}")

    try:

        resume_text = ""

        with fitz.open(file_path) as pdf:

            for page in pdf:

                blocks = page.get_text("blocks")
                mid_x = page.rect.width / 2

                def get_block_key(b):
                    x0, y0, x1, y1, text, block_no, block_type = b
                    if x1 <= mid_x:
                        col = 0
                    elif x0 >= mid_x:
                        col = 1
                    else:
                        col = 0
                    return (col, y0)

                sorted_blocks = sorted(blocks, key=get_block_key)

                for b in sorted_blocks:
                    if len(b) > 4 and b[4].strip():
                        resume_text += b[4].strip() + "\n"

        # Check for scanned PDF
        if len(resume_text.strip()) < 50:
            warning("Extracted text is very short. Scanned PDF or image-only PDF detected.")

        return resume_text

    except Exception as e:

        exception("Failed to parse PDF.")

        raise ResumeParserError(str(e))


# ==========================================================
# DOCX Parser
# ==========================================================

def extract_docx(file_path: Path) -> str:
    """
    Extract text from DOCX.
    """

    info(f"Reading DOCX: {file_path.name}")

    try:

        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                paragraphs.append(

                    paragraph.text.strip()

                )

        return "\n".join(paragraphs)

    except Exception as e:

        exception("Failed to parse DOCX.")

        raise ResumeParserError(str(e))


# ==========================================================
# DOC Parser
# ==========================================================

def extract_doc(file_path: Path) -> str:
    """
    Extract text from legacy DOC files.
    """

    info(f"Reading DOC: {file_path.name}")

    try:

        content = textract.process(file_path)

        return content.decode(

            "utf-8",

            errors="ignore"

        )

    except Exception as e:

        exception("Failed to parse DOC.")

        raise ResumeParserError(str(e))
    
# ==========================================================
# TXT Parser
# ==========================================================

def extract_txt(file_path: Path) -> str:
    """
    Extract text from TXT files.
    """

    info(f"Reading TXT: {file_path.name}")

    try:

        return file_path.read_text(

            encoding="utf-8",

            errors="ignore"

        )

    except Exception as e:

        exception("Failed to parse TXT.")

        raise ResumeParserError(str(e))


# ==========================================================
# RTF Parser
# ==========================================================

def extract_rtf(file_path: Path) -> str:
    """
    Extract text from RTF files.
    """

    info(f"Reading RTF: {file_path.name}")

    try:

        rtf = file_path.read_text(

            encoding="utf-8",

            errors="ignore"

        )

        return rtf_to_text(rtf)

    except Exception as e:

        exception("Failed to parse RTF.")

        raise ResumeParserError(str(e))


# ==========================================================
# ODT Parser
# ==========================================================

def extract_odt(file_path: Path) -> str:
    """
    Extract text from ODT files.
    """

    info(f"Reading ODT: {file_path.name}")

    try:

        document = load(file_path)

        paragraphs = []

        for paragraph in document.getElementsByType(text.P):

            if paragraph.firstChild:

                paragraphs.append(

                    paragraph.firstChild.data

                )

        return "\n".join(paragraphs)

    except Exception as e:

        exception("Failed to parse ODT.")

        raise ResumeParserError(str(e))


# ==========================================================
# Clean Resume Text
# ==========================================================

def clean_text(resume_text: str) -> str:
    """
    Clean extracted resume text.
    """

    info("Cleaning extracted resume text.")

    if not resume_text:

        return ""

    resume_text = resume_text.replace("\r", "\n")

    cleaned_lines = []

    for line in resume_text.splitlines():

        line = " ".join(line.split())

        if line:

            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    return cleaned_text[:MAX_RESUME_TEXT_LENGTH]


# ==========================================================
# Validate Resume
# ==========================================================

def validate_resume(file_path: Path) -> None:
    """
    Validate uploaded resume.
    """

    if not file_path.exists():

        warning("Resume file not found.")

        raise ResumeParserError(

            f"Resume not found: {file_path}"

        )

    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_RESUME_FORMATS:

        warning(f"Unsupported format: {suffix}")

        raise ResumeParserError(

            f"Unsupported resume format: {suffix}"

        )


# ==========================================================
# Parser Registry
# ==========================================================

PARSERS: dict[str, Callable[[Path], str]] = {

    ".pdf": extract_pdf,

    ".docx": extract_docx,

    ".doc": extract_doc,

    ".txt": extract_txt,

    ".rtf": extract_rtf,

    ".odt": extract_odt,

}

# ==========================================================
# Extract Resume Text
# ==========================================================

def extract_resume_text(file_path: str | Path) -> str:
    """
    Extract text from a resume file.

    Parameters
    ----------
    file_path : str | Path
        Path to the resume file.

    Returns
    -------
    str
        Cleaned resume text.

    Raises
    ------
    ResumeParserError
        If parsing fails.
    """

    path = Path(file_path)

    info(f"Resume parsing started: {path.name}")

    try:

        # Validate file
        validate_resume(path)

        suffix = path.suffix.lower()

        parser = PARSERS.get(suffix)

        if parser is None:

            raise ResumeParserError(

                f"No parser available for '{suffix}'."

            )

        # Extract text
        resume_text = parser(path)

        # Clean text
        resume_text = clean_text(resume_text)

        # Validate extracted text
        if not resume_text:

            raise ResumeParserError(

                "No readable text found in the resume."

            )

        info(

            f"Resume parsed successfully ({len(resume_text)} characters)."

        )

        return resume_text

    except ResumeParserError:

        raise

    except Exception as e:

        exception("Unexpected error while parsing resume.")

        raise ResumeParserError(str(e))


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print(" AI JobAgent - Resume Parser Test ")
    print("=" * 60)

    resume_path = input(

        "\nEnter Resume Path: "

    ).strip()

    try:

        text = extract_resume_text(resume_path)

        print("\nResume Parsed Successfully")

        print("\nCharacters :", len(text))

        print("\nPreview:\n")

        print(text[:3000])

    except ResumeParserError as e:

        print("\nResume Parser Error")

        print(e)

    except Exception as e:

        print("\nUnexpected Error")

        print(e)