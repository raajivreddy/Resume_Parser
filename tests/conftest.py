import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """
    Creates a new FastAPI TestClient for each test.
    This acts like a real HTTP client hitting the app directly without spinning up a live Uvicorn server.
    """
    return TestClient(app)
