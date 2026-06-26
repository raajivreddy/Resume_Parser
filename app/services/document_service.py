import os
import tempfile
import logging
from fastapi import UploadFile
from app.extractors import extract_text_from_pdf, extract_text_from_docx, extract_text_from_doc

logger = logging.getLogger("resume_parser.services.document")

async def extract_text_from_upload(file: UploadFile) -> str:
    """
    Handles the ingestion of raw HTTP UploadFiles.
    Saves the file stream to a temporary disk location, routes it to the correct 
    extractor based on its extension, and guarantees disk cleanup afterwards.
    """
    filename = file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()
    
    # Validation
    if ext not in [".pdf", ".docx", ".doc"]:
        raise ValueError(f"Unsupported file format: {ext}. Expected .pdf, .docx, or .doc")

    # FastAPI UploadFiles reside in memory (if small) or spool to disk (if large).
    # C-based libraries like PyMuPDF prefer reading from a real absolute file path.
    # So we write the stream to a temporary file.
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        # Read the file bytes asynchronously so we don't block the FastAPI event loop
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Routing to the appropriate extraction engine
        logger.info(f"Extracting text from {ext} file...")
        if ext == ".pdf":
            text = extract_text_from_pdf(tmp_path)
        elif ext == ".docx":
            text = extract_text_from_docx(tmp_path)
        elif ext == ".doc":
            text = extract_text_from_doc(tmp_path)
            
        if not text.strip():
            raise ValueError("Extraction succeeded, but the file was empty or contained only images (scanned PDF without OCR).")
            
        return text

    finally:
        # 12-Factor App methodology: ALWAYS clean up temporary state.
        # This executes even if the extraction throws an exception.
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
