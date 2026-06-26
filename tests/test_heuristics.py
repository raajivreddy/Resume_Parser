from app.nlp.heuristics import extract_name, fallback_experience, is_valid_education, normalize_skills

def test_extract_name():
    # Valid Name
    text = "John Doe\nSoftware Engineer\njohn@doe.com"
    assert extract_name(text) == "John Doe"

    # Invalid Name (Contains github link)
    bad_text = "github.com/johndoe\nSoftware Engineer"
    assert extract_name(bad_text) is None

    # Invalid Name (Too long)
    long_text = "John Jacob Jingleheimer Schmidt Smith\nSoftware Engineer"
    assert extract_name(long_text) is None

def test_normalize_skills():
    # Tests splitting by comma, slash, semicolon, and canonical capitalization
    raw_skills = ["python, c++, aws/gcp", "fastapi; sql"]
    cleaned = normalize_skills(raw_skills)
    assert cleaned == ["AWS", "C++", "FastAPI", "GCP", "Python", "SQL"]

def test_is_valid_education():
    # True positives
    assert is_valid_education({"degree": "B.S. in Computer Science", "institution": "MIT"}) is True
    assert is_valid_education({"degree": "Master of Engineering"}) is True
    
    # False positives (sentences that the Transformer hallucinated into degrees)
    assert is_valid_education({"degree": "Worked on a science project"}) is False
    assert is_valid_education({"institution": "Developed highly scalable systems"}) is False

def test_fallback_experience():
    text = "Software Engineer\nGoogle\nBuilt APIs"
    experiences = fallback_experience(text)
    
    assert len(experiences) == 1
    assert experiences[0]["position"] == "Software Engineer"
    assert experiences[0]["company"] == "Google"

def test_fallback_experience_ignores_invalid_companies():
    # Company string starts with '-', so it should be rejected
    text = "Software Engineer\n- Built scalable microservices"
    experiences = fallback_experience(text)
    
    assert len(experiences) == 1
    assert experiences[0]["position"] == "Software Engineer"
    assert "company" not in experiences[0]
