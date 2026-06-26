import logging
from app.models.schemas import ResumeData, ParseResponse
from app.nlp import normalize_text, segment_sections, ner_service, resolve_entities, apply_heuristics

logger = logging.getLogger("resume_parser.services.parsing")

def parse_resume_text(raw_text: str) -> ParseResponse:
    """
    The master orchestrator for the NLP pipeline.
    Passes raw text through the sequential DAG (Directed Acyclic Graph) of NLP tasks.
    Returns a validated Pydantic ParseResponse.
    """
    try:
        if not raw_text or len(raw_text.strip()) < 50:
            return ParseResponse(status="error", data=None, message="Extracted text is too short to be a valid resume.")

        # 1. Normalization (Clean up Unicode and weird whitespace)
        logger.info("Pipeline Step 1: Normalizing text")
        clean_text = normalize_text(raw_text)
        
        # 2. Segmentation (Split into Experience, Education, etc.)
        logger.info("Pipeline Step 2: Segmenting sections")
        sections = segment_sections(clean_text)
        
        all_entities = []
        
        # 3. Transformer Inference (Run BERT on each block)
        logger.info("Pipeline Step 3: Running Transformer NER (Section-Aware)")
        for section_name, section_text in sections.items():
            if not section_text:
                continue
            
            # E. Section-aware inference: Route sections appropriately
            if section_name == "contact":
                # Contact info is better handled by Heuristics (Regex). Skip BERT.
                logger.debug("Skipping NER for contact block (handled by heuristics).")
                continue
            elif section_name == "skills":
                # Inject raw skills directly as mock entities to bypass transformer hallucinations
                skills_list = [s.strip() for s in section_text.split(',') if s.strip()]
                if not skills_list:
                    skills_list = [s.strip() for s in section_text.split('\n') if s.strip()]
                for skill in skills_list:
                    all_entities.append({"entity_group": "skill", "word": skill, "score": 1.0})
                continue
            
            # For Experience, Education, Projects, run Transformer
            entities = ner_service.predict(section_text)
            all_entities.extend(entities)
            
        # 4. Entity Resolution (Group and threshold)
        logger.info("Pipeline Step 4: Resolving entities")
        resolved_data = resolve_entities(all_entities, confidence_threshold=0.6)
        
        # 5. Heuristic Fallbacks (Extract emails, phones, dates, and rescue failed blocks)
        logger.info("Pipeline Step 5: Applying heuristic fallbacks")
        final_dict = apply_heuristics(resolved_data, raw_text, sections)
        
        # 6. Response Cleanup (Remove nulls and empties)
        logger.info("Pipeline Step 6: Response Cleanup")
        for key in ["experience", "education"]:
            clean_list = []
            for item in final_dict.get(key, []):
                cleaned_item = {k: v for k, v in item.items() if v}
                if cleaned_item:
                    clean_list.append(cleaned_item)
            final_dict[key] = clean_list
            
        # 7. Schema Validation (Cast dict to Pydantic object)
        logger.info("Pipeline Step 7: Pydantic Validation")
        resume_data = ResumeData(**final_dict)
        
        return ParseResponse(status="success", data=resume_data, message="Resume parsed successfully")
        
    except Exception as e:
        logger.error(f"Parsing pipeline failed: {str(e)}", exc_info=True)
        # Catch-all failsafe. Prevents the API from throwing an unhandled 500 error.
        return ParseResponse(status="error", data=None, message=f"Internal parsing error: {str(e)}")
