import os
import zipfile
from typing import Tuple, Optional

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

def validate_uploaded_file(file_storage, max_size: int = MAX_FILE_SIZE) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates uploaded file filename, extension, file size, and magic bytes.
    Returns (is_valid, error_message, file_type).
    """
    if not file_storage or not file_storage.filename:
        return False, "No file selected.", None

    filename = file_storage.filename
    if "." not in filename:
        return False, "File lacks an extension.", None

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '.{ext}'. Allowed types are PDF and DOCX.", None

    # Check file size by seeking
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)

    if file_size == 0:
        return False, "Uploaded file is empty.", None

    if file_size > max_size:
        return False, f"File exceeds maximum allowed size ({max_size // (1024 * 1024)}MB).", None

    # Header / Magic bytes verification
    header = file_storage.read(8)
    file_storage.seek(0)

    if ext == "pdf":
        if not header.startswith(b"%PDF-"):
            return False, "Invalid PDF file structure or corrupted document.", None
    elif ext == "docx":
        if not header.startswith(b"PK\x03\x04"):
            return False, "Invalid DOCX file: missing zip header.", None
        try:
            with zipfile.ZipFile(file_storage) as zf:
                if "word/document.xml" not in zf.namelist():
                    file_storage.seek(0)
                    return False, "Corrupted DOCX: missing word/document.xml.", None
        except Exception as e:
            file_storage.seek(0)
            return False, f"Corrupted DOCX archive: {str(e)}", None
        finally:
            file_storage.seek(0)

    return True, None, ext
