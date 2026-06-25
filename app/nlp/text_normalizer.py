import re
import unicodedata
import logging

logger = logging.getLogger("resume_parser.nlp.normalizer")

def normalize_text(text: str) -> str:
    """
    Cleans and normalizes raw text extracted from documents to prepare it for NLP models.
    Handles unicode normalization, bullet points, invisible characters, and excessive whitespace.
    """
    if not text:
        return ""

    try:
        # 1. Unicode Normalization: NFKC converts ligatures (ﬁ -> fi) and standardizes characters
        text = unicodedata.normalize("NFKC", text)

        # 2. Standardize bullet points
        # Resumes use heavy styling. We map various bullets to a simple dash for the sectioner.
        text = re.sub(r'[•◦▪►✓✔☑●■◆]', '-', text)

        # 3. Standardize quotes
        text = re.sub(r'[“”]', '"', text)
        text = re.sub(r'[‘’`]', "'", text)

        # 4. Strip invisible formatting characters (zero-width spaces, soft hyphens, BOM)
        text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad]', '', text)

        # 5. Collapse horizontal whitespace (spaces, tabs) into a single space
        # We don't touch \n here because newlines are critical for section segmentation
        text = re.sub(r'[ \t]+', ' ', text)

        # 6. Clean up line-by-line whitespace
        # A line with just a space becomes empty, removing trailing/leading spaces per line
        lines = [line.strip() for line in text.split('\n')]

        # 7. Collapse vertical whitespace
        # 3+ newlines usually mean a major section break, but we normalize it to exactly 2
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    except Exception as e:
        logger.error(f"Text normalization failed: {str(e)}")
        # In a robust pipeline, if normalization fails, we return the raw text 
        # rather than crashing the entire request, though logging the error.
        return text.strip()
