from fastapi import APIRouter, UploadFile, File
import logging
from app.utils.config import settings
from app.models.schemas import ParseResponse
from app.services.document_service import extract_text_from_upload
from app.services.parsing_service import parse_resume_text
from app.utils.exceptions import UnsupportedFormatError, NLPProcessingError

logger = logging.getLogger("resume_parser.api")

router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

@router.get("/version", tags=["System"])
async def get_version():
    return {
        "version": settings.app_version
    }

@router.post("/parse/file", response_model=ParseResponse, tags=["Parser"])
async def parse_file(file: UploadFile = File(...)):
    """
    Ingests a resume file (PDF, DOCX, DOC), extracts the raw text, 
    and processes it through the NLP pipeline to return structured JSON.
    """
    logger.info(f"Received parsing request for file: {file.filename}")
    
    try:
        # 1. I/O Bound Task: Extract raw text from the uploaded binary
        raw_text = await extract_text_from_upload(file)
    except ValueError as ve:
        # 415 Unsupported Media Type (mapped to UnsupportedFormatError)
        logger.warning(f"File extraction error: {str(ve)}")
        raise UnsupportedFormatError(str(ve))

    # 2. CPU Bound Task: Run the Transformer NLP pipeline
    # The parsing service is wrapped in a catch-all and guaranteed to return a ParseResponse object
    response = parse_resume_text(raw_text)
    
    # If the parsing pipeline failed gracefully, map it to a RESTful 422 Unprocessable Entity
    if response.status == "error":
        # We return the response model but alter the HTTP status code
        raise NLPProcessingError(response.message)
        
    return response
