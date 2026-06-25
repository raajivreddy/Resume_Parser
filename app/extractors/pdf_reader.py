import fitz  # PyMuPDF
import logging

logger = logging.getLogger("resume_parser.extractors.pdf")

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF.
    PyMuPDF is significantly faster than pdfplumber or PyPDF2.
    """
    text = []
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {file_path}. Error: {str(e)}")
        raise ValueError(f"PDF extraction failed: {str(e)}")
