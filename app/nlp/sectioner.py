import re
import logging
from typing import Dict

logger = logging.getLogger("resume_parser.nlp.sectioner")

# Mapping of canonical section names to possible variations found in resumes
SECTION_ALIASES = {
    "experience": ["experience", "employment", "work history", "professional experience", "career", "work experience"],
    "education": ["education", "academic", "qualifications", "academic background", "education & training"],
    "skills": ["skills", "technologies", "technical skills", "core competencies", "tools", "it skills"],
    "projects": ["projects", "personal projects", "portfolio", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses", "courses", "training"]
}

def segment_sections(text: str) -> Dict[str, str]:
    """
    Splits normalized resume text into logical blocks (Experience, Education, etc.).
    Uses a heuristic approach scanning for short, keyword-matching lines.
    """
    sections = {
        "contact": "",
        "experience": "",
        "education": "",
        "skills": "",
        "projects": "",
        "certifications": "",
        "unknown": ""
    }
    
    if not text:
        return sections

    # The top of a resume is almost universally the contact info block, 
    # until the first explicit section header is encountered.
    current_section = "contact"
    
    lines = text.split('\n')
    
    for line in lines:
        stripped_line = line.strip().lower()
        
        # Heuristic 1: Headers are almost always short lines (usually < 40 characters)
        # Heuristic 2: Headers rarely have more than 5 words
        is_header = False
        if len(stripped_line) > 0 and len(stripped_line) < 40 and len(stripped_line.split()) <= 5:
            # Strip trailing colons or dashes from the line before matching (e.g., "EXPERIENCE:")
            clean_header_candidate = re.sub(r'[:-]+$', '', stripped_line).strip()
            
            for section_name, aliases in SECTION_ALIASES.items():
                # Check for exact matches or strings starting with the alias
                if clean_header_candidate in aliases or any(clean_header_candidate.startswith(alias + " ") for alias in aliases):
                    current_section = section_name
                    is_header = True
                    break
        
        if not is_header:
            sections[current_section] += line + "\n"
            
    # Post-processing: clean up trailing/leading whitespace for all extracted blocks
    for key in sections:
        sections[key] = sections[key].strip()
        
    return sections
