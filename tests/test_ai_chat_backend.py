"""Tests for AI backend initialization and error handling."""
import os
import pytest
from unittest.mock import patch, MagicMock


def test_ai_chat_initializes_with_ollama_when_available():
    """AIChat should initialize successfully when Ollama is available."""
    with patch.dict(os.environ, {'AI_BACKEND': 'ollama'}, clear=False):
        # Mock the OllamaChat connection check to return True
        with patch('chat_ollama.OllamaChat.check_connection', return_value=True):
            from modules.ai_chat import AIChat
            
            chat = AIChat()
            
            assert chat.client is not None
            assert chat.backend == 'ollama'


def test_ai_chat_handles_missing_api_key_gracefully():
    """AIChat should handle missing API keys without crashing."""
    with patch.dict(os.environ, {'AI_BACKEND': 'groq'}, clear=False):
        # Remove GROQ_API_KEY if it exists
        env = os.environ.copy()
        env.pop('GROQ_API_KEY', None)
        
        with patch.dict(os.environ, env, clear=True):
            from modules.ai_chat import AIChat
            
            chat = AIChat()
            
            # Should not crash, client should be None
            assert chat.client is None


def test_ai_chat_handles_connection_failure():
    """AIChat should handle connection failures gracefully."""
    with patch.dict(os.environ, {'AI_BACKEND': 'ollama'}, clear=False):
        # Mock the OllamaChat connection check to return False
        with patch('chat_ollama.OllamaChat.check_connection', return_value=False):
            from modules.ai_chat import AIChat
            
            chat = AIChat()
            
            # Should not crash, client should be None
            assert chat.client is None


def test_ai_chat_unsupported_backend():
    """AIChat should handle unsupported backend gracefully."""
    with patch.dict(os.environ, {'AI_BACKEND': 'unsupported_backend'}, clear=False):
        from modules.ai_chat import AIChat
        
        chat = AIChat()
        
        # Should not crash, client should be None
        assert chat.client is None
