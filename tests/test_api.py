from unittest.mock import patch
from app.models.schemas import ParseResponse, ResumeData

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data

def test_version_endpoint(client):
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_parse_invalid_file_type(client):
    # Pass a .txt file. The API should reject it instantly with a 415 Unsupported Media Type.
    file_content = b"fake data"
    files = {"file": ("test.txt", file_content, "text/plain")}
    response = client.post("/api/v1/parse/file", files=files)
    
    assert response.status_code == 415
    assert "Unsupported file format" in response.json()["message"]

@patch("app.api.routes.extract_text_from_upload")
@patch("app.api.routes.parse_resume_text")
def test_parse_valid_pdf(mock_parse, mock_extract, client):
    """
    End-to-End test of the API endpoint using Mocks.
    We mock the disk-I/O (extract) and the heavy deep learning (parse) 
    to ensure the unit test runs in <0.01 seconds.
    """
    # 1. Setup Mock Returns
    mock_extract.return_value = "Fake Extracted Text"
    fake_data = ResumeData(contact={"name": "John Doe", "email": "john@example.com"})
    mock_parse.return_value = ParseResponse(status="success", data=fake_data, message="Parsed successfully")

    # 2. Execute Request
    files = {"file": ("resume.pdf", b"fake pdf content", "application/pdf")}
    response = client.post("/api/v1/parse/file", files=files)
    
    # 3. Assertions
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "success"
    assert json_resp["data"]["contact"]["name"] == "John Doe"
    
    # Verify the mocks were actually called
    mock_extract.assert_called_once()
    mock_parse.assert_called_once_with("Fake Extracted Text")
