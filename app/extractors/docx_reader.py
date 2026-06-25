import docx
import logging

logger = logging.getLogger("resume_parser.extractors.docx")

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    Iterates through paragraphs and joins them.
    """
    try:
        doc = docx.Document(file_path)
        text = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
        return "\n".join(text)
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX: {file_path}. Error: {str(e)}")
        raise ValueError(f"DOCX extraction failed: {str(e)}")
