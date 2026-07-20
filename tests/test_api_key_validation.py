"""
API key validation tests.

Run manually to check if API keys are still active:
    pytest tests/test_api_key_validation.py -v -s

These tests are skipped by default in CI since they require network access
and valid credentials. Set RUN_API_KEY_TESTS=1 to enable.
"""

import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

# Skip all tests unless explicitly enabled
pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_API_KEY_TESTS"),
    reason="Set RUN_API_KEY_TESTS=1 to run API key validation"
)


def test_azure_openai_key():
    """Test Azure OpenAI key validity."""
    api_key = os.getenv('AZURE_OPENAI_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '').rstrip('/')
    
    if not api_key or not endpoint:
        pytest.skip("Azure OpenAI not configured")
    
    url = f"{endpoint}/openai/deployments/gpt-4o/chat/completions?api-version=2024-06-01"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    data = {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}
    
    response = requests.post(url, headers=headers, json=data, timeout=10)
    
    assert response.status_code not in [401, 403], \
        f"Azure OpenAI key is invalid (HTTP {response.status_code})"


def test_gemini_key():
    """Test Gemini API key validity."""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        pytest.skip("Gemini not configured")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url, timeout=10)
    
    assert response.status_code not in [400, 403, 404], \
        f"Gemini key is invalid (HTTP {response.status_code})"


def test_ollama_key():
    """Test Ollama API key validity."""
    api_key = os.getenv('OLLAMA_API_KEY')
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    if not api_key:
        pytest.skip("Ollama not configured")
    
    url = f"{base_url}/api/tags"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama service not reachable")
    
    assert response.status_code not in [401, 403], \
        f"Ollama key is invalid (HTTP {response.status_code})"


def test_no_plaintext_secrets_in_repo():
    """Verify .env is not tracked by git."""
    result = os.popen("git ls-files .env").read().strip()
    assert result == "", \
        ".env is tracked by git! Run: git rm --cached .env"
