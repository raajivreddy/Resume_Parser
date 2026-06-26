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
            # A. PREPROCESSING
            # BERT was trained on sentence structures. Raw newlines (\n) heavily disrupt tokenization
            # and positional embeddings, causing empty outputs or bizarre hallucinations.
            # We map single newlines to commas, and double newlines to periods.
            clean_text = text.replace('\n\n', '. ').replace('\n', ', ')
            
            # Safe truncation
            safe_text = clean_text[:2000]
            
            entities = self._pipeline(safe_text)

            # C. GRACEFUL DEGRADATION
            if not entities:
                logger.warning(f"NER returned an empty list for text snippet: {safe_text[:50]}...")
                return []

            # B. POST-PROCESSING
            filtered_entities = []
            stop_words = {"and", "with", "the", "a", "an", "of", "in", "for", "to", "at", "by", "on"}
            
            for entity in entities:
                word = entity.get("word", "").strip()
                score = float(entity.get("score", 0.0))
                
                # 1. Skip empty strings
                if not word:
                    continue
                # 2. Skip subword fragments that escaped simple aggregation
                if word.startswith("##"):
                    continue
                # 3. Skip punctuation-only entities
                if len(word) == 1 and not word.isalnum():
                    continue
                # 4. Skip obvious stop-word hallucinations
                if word.lower() in stop_words:
                    continue
                    
                entity["score"] = score
                filtered_entities.append(entity)

            # Deduplicate entities based on word and group, keeping the highest score
            dedup = {}
            for e in filtered_entities:
                key = f"{e['entity_group']}_{e['word']}"
                if key not in dedup or e['score'] > dedup[key]['score']:
                    dedup[key] = e

            return list(dedup.values())

        except Exception as e:
            logger.error(f"Transformer inference failed: {str(e)}")
            # Fail gracefully, return empty list so heuristics can still try to extract basic info
            return []

# Expose a pre-instantiated singleton instance
ner_service = ResumeNERService()
