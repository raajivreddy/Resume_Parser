# Extractors module
from .pdf_reader import extract_text_from_pdf
from .docx_reader import extract_text_from_docx
from .doc_reader import extract_text_from_doc

__all__ = ["extract_text_from_pdf", "extract_text_from_docx", "extract_text_from_doc"]
