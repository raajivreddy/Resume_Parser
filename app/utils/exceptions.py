class ResumeParserException(Exception):
    """Base exception for all application-specific errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class FileExtractionError(ResumeParserException):
    """Raised when PDF, DOCX, or DOC extraction fails or the file is corrupted."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class NLPProcessingError(ResumeParserException):
    """Raised when the NLP pipeline (Transformers, NER, or Heuristics) experiences a critical crash."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class UnsupportedFormatError(ResumeParserException):
    """Raised when a user uploads a file format we do not support."""
    def __init__(self, message: str):
        super().__init__(message, status_code=415) # 415 Unsupported Media Type
