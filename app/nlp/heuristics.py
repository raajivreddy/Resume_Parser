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
    matches = re.findall(r'\b(?:19|20)\d{2}\b', text)
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

def fallback_experience(text: str) -> List[Dict[str, str]]:
    """Heuristic fallback if NER completely misses the experience section."""
    experiences = []
    current_exp = {}
    titles = ["engineer", "developer", "scientist", "analyst", "intern", "manager", "consultant"]
    
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        
        # Infer position: contains keyword, relatively short
        if any(t in line.lower() for t in titles) and len(line) < 60:
            if current_exp.get("position"):
                experiences.append(current_exp)
                current_exp = {}
            current_exp["position"] = line
            continue
            
        # Infer company: short, mostly title case, happens after a position
        if len(line) < 40 and line.istitle() and current_exp.get("position") and not current_exp.get("company"):
            current_exp["company"] = line

    if current_exp:
        experiences.append(current_exp)
    return experiences

def fallback_education(edu: Dict[str, str]) -> Dict[str, str]:
    degree = edu.get("degree", "")

    # Only attempt splitting if the string looks merged
    if len(degree.split()) > 4 and not edu.get("institution"):

        # 1. Extract and remove graduation year
        year_match = re.search(r"\b(?:19|20)\d{2}\b", degree)
        if year_match:
            edu["graduation_year"] = year_match.group(0)
            degree = degree.replace(year_match.group(0), "").strip()

        # 2. Split degree and institution
        institution_keywords = {
            "University",
            "College",
            "Institute",
            "School",
        }

        parts = degree.split()

        split_found = False

        for i, word in enumerate(parts):
            if word in institution_keywords and i > 0:
                edu["degree"] = " ".join(parts[: i - 1]).strip()
                edu["institution"] = " ".join(parts[i - 1 :]).strip()
                split_found = True
                break

        # 3. Final fallback if no institution keyword exists
        if not split_found and len(parts) >= 4:
            edu["degree"] = " ".join(parts[:3]).strip()
            edu["institution"] = " ".join(parts[3:]).strip()

    return edu

def apply_heuristics(resolved_data: Dict[str, Any], raw_text: str, sections: Dict[str, str] = None) -> Dict[str, Any]:
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

    # 2. Education Heuristics (Dates & Merged splits)
    for i, edu in enumerate(resolved_data.get("education", [])):
        if not edu.get("graduation_year"):
            combined_text = f"{edu.get('degree', '')} {edu.get('institution', '')}"
            year = extract_graduation_year(combined_text)
            if year:
                edu["graduation_year"] = year
        
        # Attempt to split merged strings
        resolved_data["education"][i] = fallback_education(edu)

    # 3. Experience Fallback (If NER returned [])
    if not resolved_data.get("experience") and sections and sections.get("experience"):
        resolved_data["experience"] = fallback_experience(sections["experience"])

    # 4. Skills Normalization
    if "skills" in resolved_data:
        resolved_data["skills"] = normalize_skills(resolved_data["skills"])

    return resolved_data
