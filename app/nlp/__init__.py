# NLP module
from .text_normalizer import normalize_text
from .sectioner import segment_sections
from .transformer import ner_service
from .entity_resolver import resolve_entities
from .heuristics import apply_heuristics

__all__ = ["normalize_text", "segment_sections", "ner_service", "resolve_entities", "apply_heuristics"]
