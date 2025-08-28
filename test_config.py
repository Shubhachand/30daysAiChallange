import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_save_api_keys():
    response = client.post("/api/save-api-keys", json={
        "MURF_API_KEY": "test_murf_key",
        "ASSEMBLYAI_API_KEY": "test_assemblyai_key",
        "GEMINI_API_KEY": "test_gemini_key",
        "TAVILY_API_KEY": "test_tavily_key",
        "NEWS_API_KEY": "test_news_key"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "API keys saved successfully"}

    # Verify that the keys are set in the environment
    assert os.getenv("USER_MURF_API_KEY") == "test_murf_key"
    assert os.getenv("USER_ASSEMBLYAI_API_KEY") == "test_assemblyai_key"
    assert os.getenv("USER_GEMINI_API_KEY") == "test_gemini_key"
    assert os.getenv("USER_TAVILY_API_KEY") == "test_tavily_key"
    assert os.getenv("USER_NEWS_API_KEY") == "test_news_key"
