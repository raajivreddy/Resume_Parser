import logging
from typing import List, Dict, Any

logger = logging.getLogger("resume_parser.nlp.resolver")

def resolve_entities(entities: List[Dict[str, Any]], confidence_threshold: float = 0.6) -> Dict[str, Any]:
    """
    Transforms a flat list of NER predictions into structured hierarchical data.
    - Filters out entities below the confidence threshold.
    - Groups related entities (e.g., Company + Job Title) into singular objects using a state machine.
    """
    # Initialize the structured payload that maps roughly to our Pydantic schemas
    resolved_data = {
        "contact": {},
        "experience": [],
        "education": [],
        "skills": []
    }
    
    if not entities:
        return resolved_data

    # State machine buffers
    current_experience = {}
    current_education = {}

    for entity in entities:
        score = entity.get("score", 0.0)
        
        # 1. Confidence Scoring
        if score < confidence_threshold:
            logger.debug(f"Dropped entity {entity.get('word')} due to low confidence: {score:.2f}")
            continue

        group = entity.get("entity_group", "")
        # Clean up whitespace and artifacts
        word = entity.get("word", "").strip()
        
        if not word:
            continue

        # 2. Contact Routing
        if group == "Name":
            resolved_data["contact"]["name"] = word
        elif group == "Location":
            resolved_data["contact"]["location"] = word
            
        # 3. Skills Routing (Deduplicated)
        elif group == "Skills":
            if word not in resolved_data["skills"]:
                resolved_data["skills"].append(word)

        # 4. Experience Resolution (State Machine)
        elif group in ["Designation", "JobTitle"]:
            # If we already have a position in the buffer, this implies a new job entry has started
            if "position" in current_experience:
                resolved_data["experience"].append(current_experience)
                current_experience = {}
            current_experience["position"] = word
            
        elif group in ["Companies worked at", "Company"]:
            # If we already have a company in the buffer, flush to list
            if "company" in current_experience:
                resolved_data["experience"].append(current_experience)
                current_experience = {}
            current_experience["company"] = word
            
        elif group in ["Years of Experience", "Duration"]:
            current_experience["duration"] = word

        # 5. Education Resolution (State Machine)
        elif group == "Degree":
            if "degree" in current_education:
                resolved_data["education"].append(current_education)
                current_education = {}
            current_education["degree"] = word
            
        elif group in ["College Name", "University"]:
            if "institution" in current_education:
                resolved_data["education"].append(current_education)
                current_education = {}
            current_education["institution"] = word

    # 6. Flush remaining buffers after the loop ends
    if current_experience:
        resolved_data["experience"].append(current_experience)
    if current_education:
        resolved_data["education"].append(current_education)

    return resolved_data
