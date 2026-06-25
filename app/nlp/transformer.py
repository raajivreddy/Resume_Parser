import logging
from typing import List, Dict, Any
from transformers import pipeline

logger = logging.getLogger("resume_parser.nlp.transformer")

class ResumeNERService:
    """
    Singleton service to handle HuggingFace Transformer inference.
    We use a Singleton pattern so the massive model is only loaded into memory once,
    and we use Lazy Loading so the API can boot up instantly without waiting for weights to download.
    """
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResumeNERService, cls).__new__(cls)
        return cls._instance

    def _load_model(self):
        """
        Lazy loads the BERT model onto the CPU.
        """
        if self._pipeline is None:
            logger.info("Initializing HuggingFace Pipeline: yashpwr/resume-ner-bert-v2")
            try:
                # device=-1 explicitly forces CPU inference to avoid CUDA overhead/errors
                # aggregation_strategy="simple" groups B-I-O tags into full entities
                self._pipeline = pipeline(
                    task="token-classification",
                    model="yashpwr/resume-ner-bert-v2",
                    tokenizer="yashpwr/resume-ner-bert-v2",
                    device=-1,
                    aggregation_strategy="simple"
                )
                logger.info("Transformer NER model loaded successfully into RAM.")
            except Exception as e:
                logger.error(f"Failed to load Transformer model. Ensure you have internet access for the first run. Error: {str(e)}")
                raise RuntimeError(f"Model loading failed: {str(e)}")

    def predict(self, text: str) -> List[Dict[str, Any]]:
        """
        Executes NER on the text to extract entities like Name, Company, Degree.
        Returns a list of dictionaries containing the entity group, score, and text snippet.
        """
        if not text or not text.strip():
            return []

        # Load model only when the first request actually hits the service
        self._load_model()

        try:
            # We process the text in chunks. BERT has a strict 512 token limit.
            # 512 tokens is roughly 2000-2500 characters. 
            # Splitting purely by character count can cut words in half, so we split by newlines.
            paragraphs = text.split('\n\n')
            all_entities = []

            for paragraph in paragraphs:
                if not paragraph.strip():
                    continue
                
                # To prevent arbitrary paragraphs from exceeding the limit, truncate safely
                safe_text = paragraph[:2000]
                
                entities = self._pipeline(safe_text)
                all_entities.extend(entities)

            # Convert numpy.float32 scores to native python floats for JSON serialization
            for entity in all_entities:
                if 'score' in entity:
                    entity['score'] = float(entity['score'])

            return all_entities

        except Exception as e:
            logger.error(f"Transformer inference failed: {str(e)}")
            # Fail gracefully, return empty list so heuristics can still try to extract basic info
            return []

# Expose a pre-instantiated singleton instance
ner_service = ResumeNERService()
