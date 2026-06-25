import re
from typing import Dict, Any, List

def extract_email(text: str) -> str | None:
    """Extracts the first valid email address found in the text."""
    # Standard RFC 5322 approximation regex
    match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str | None:
    """Extracts standard phone number formats (e.g., +1 (555) 123-4567, 555-555-5555)."""
    # Matches international prefix, area code in parens, and dot/dash separators
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    return match.group(0) if match else None

def extract_graduation_year(text: str) -> str | None:
    """Extracts a plausible 4-digit year (1980-2030) from an education block."""
    matches = re.findall(r'\b(19|20)\d{2}\b', text)
    if matches:
        # Usually the last year mentioned in an education block is the graduation year
        return matches[-1]
    return None

def normalize_skills(skills: List[str]) -> List[str]:
    """
    Cleans, deduplicates, and standardizes capitalization for skills.
    e.g., ['python ', 'PYTHON', 'machine-learning'] -> ['Machine-Learning', 'Python']
    """
    cleaned_skills = set()
    for skill in skills:
        # Remove erratic punctuation but keep valid skill chars like +, #, -, .
        clean = re.sub(r'[^\w\s+#.-]', '', skill).strip().title()
        if len(clean) > 1:
            cleaned_skills.add(clean)
    
    return sorted(list(cleaned_skills))

def apply_heuristics(resolved_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """
    Fills in the data gaps left by the Transformer NER model using targeted Regex rules.
    Deep Learning is used for semantic extraction; Regex is used for pattern extraction.
    """
    # 1. Contact Heuristics
    contact = resolved_data.get("contact", {})
    
    # If the NER model didn't find an email, Regex scan the entire raw text
    if not contact.get("email"):
        contact["email"] = extract_email(raw_text)
        
    if not contact.get("phone"):
        contact["phone"] = extract_phone(raw_text)
        
    resolved_data["contact"] = contact

    # 2. Education Heuristics (Dates)
    # If the model found a Degree but missed the Year, we scan the institution name string
    # (or we could scan the raw education block text, but for MVP we scan what we have)
    for edu in resolved_data.get("education", []):
        if not edu.get("graduation_year"):
            # Attempt to find a year within the extracted degree or institution string
            combined_text = f"{edu.get('degree', '')} {edu.get('institution', '')}"
            year = extract_graduation_year(combined_text)
            if year:
                edu["graduation_year"] = year

    # 3. Skills Normalization
    if "skills" in resolved_data:
        resolved_data["skills"] = normalize_skills(resolved_data["skills"])

    return resolved_data
