"""
Conversation memory system for AI chat.

Provides persistent chat history storage and retrieval,
enabling the AI to maintain context across sessions.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional
from modules.database import DatabaseManager


class ConversationMemory:
    """Manages conversation history with SQLite persistence."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_session(self, username: str) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        return session_id
    
    def save_message(self, username: str, session_id: str, role: str, content: str,
                     sources: List[str] = None, follow_up_questions: List[str] = None) -> int:
        """Save a message to chat history."""
        return self.db.save_chat_message(
            username=username,
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
            follow_up_questions=follow_up_questions
        )
    
    def get_history(self, username: str, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a session."""
        return self.db.get_chat_history(username, session_id, limit)
    
    def get_recent_messages(self, username: str, session_id: str, n: int = 10) -> List[Dict]:
        """Get the last n messages for context."""
        # Get all messages (use a large limit)
        history = self.get_history(username, session_id, limit=1000)
        # Return the last n messages
        return history[-n:] if len(history) > n else history
    
    def get_sessions(self, username: str) -> List[tuple]:
        """Get all sessions for a user."""
        return self.db.get_user_sessions(username)
    
    def clear_session(self, username: str, session_id: str) -> int:
        """Clear a chat session."""
        return self.db.clear_chat_history(username, session_id)
    
    def format_for_agent(self, messages: List[Dict]) -> List[Dict]:
        """Format messages for Pydantic AI agent."""
        formatted = []
        for msg in messages:
            formatted.append({
                'role': msg['role'],
                'content': msg['content']
            })
        return formatted


# Global instance
_conversation_memory = None


def get_conversation_memory(db_manager: DatabaseManager = None) -> ConversationMemory:
    """Get singleton conversation memory instance."""
    global _conversation_memory
    if _conversation_memory is None:
        if db_manager is None:
            from modules.database import get_database_manager
            db_manager = get_database_manager()
        _conversation_memory = ConversationMemory(db_manager)
    return _conversation_memory
