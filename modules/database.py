"""
Database Manager for 广告思想简史 Platform

This module provides centralized database operations and schema management
for the advertising history platform using SQLite.
"""

import sqlite3
import logging
from utils.logger import create_logger
import pandas as pd
from typing import Optional, Any, List, Tuple
from datetime import datetime
import os


class DatabaseManager:
    """
    Centralized database manager for SQLite operations.
    
    Handles database initialization, connection management, and provides
    safe query execution with proper error handling and logging.
    """
    
    def __init__(self, db_path: str = "platform.db"):
        """
        Initialize DatabaseManager with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = create_logger('DatabaseManager')
        self._last_insert_id: Optional[int] = None
        
    
    def init_database(self) -> None:
        """
        Initialize database with all required tables.
        
        Creates all tables defined in the schema if they don't exist.
        Handles errors gracefully and logs all operations.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create user_feedback table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        target_type TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        feedback_type TEXT NOT NULL,
                        feedback_value INTEGER,
                        feedback_text TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ip_address TEXT,
                        user_agent TEXT
                    )
                """)
                
                # Create comments table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        target_type TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        likes INTEGER DEFAULT 0,
                        parent_id INTEGER,
                        is_approved BOOLEAN DEFAULT 1,
                        deleted_at DATETIME DEFAULT NULL,
                        edited_at DATETIME DEFAULT NULL,
                        edited_by TEXT DEFAULT NULL,
                        FOREIGN KEY (parent_id) REFERENCES comments (id)
                    )
                """)
                
                # Create comment_likes table for tracking who liked what
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS comment_likes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        comment_id INTEGER NOT NULL,
                        username TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(comment_id, username),
                        FOREIGN KEY (comment_id) REFERENCES comments(id)
                    )
                """)
                
                # Create comment_reports table for tracking reports
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS comment_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        comment_id INTEGER NOT NULL,
                        reporter_username TEXT NOT NULL,
                        reason TEXT,
                        status TEXT DEFAULT 'pending',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        resolved_at DATETIME DEFAULT NULL,
                        resolved_by TEXT DEFAULT NULL,
                        UNIQUE(comment_id, reporter_username),
                        FOREIGN KEY (comment_id) REFERENCES comments(id)
                    )
                """)
                
                # Create comment_notifications table for reply notifications
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS comment_notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        comment_id INTEGER NOT NULL,
                        parent_comment_id INTEGER,
                        target_username TEXT NOT NULL,
                        notification_type TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT 0,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (comment_id) REFERENCES comments(id),
                        FOREIGN KEY (parent_comment_id) REFERENCES comments(id)
                    )
                """)
                
                # Create articles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        excerpt TEXT,
                        category TEXT,
                        tags TEXT,
                        author TEXT NOT NULL,
                        status TEXT DEFAULT 'draft',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        published_at DATETIME,
                        views INTEGER DEFAULT 0,
                        avg_rating REAL DEFAULT 0.0,
                        total_feedback INTEGER DEFAULT 0,
                        review_feedback TEXT DEFAULT NULL
                    )
                """)
                
                # Create content_stats table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS content_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        target_type TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        thumbs_up INTEGER DEFAULT 0,
                        thumbs_down INTEGER DEFAULT 0,
                        avg_stars REAL DEFAULT 0.0,
                        total_ratings INTEGER DEFAULT 0,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(target_type, target_id)
                    )
                """)
                
                # Create user_activity table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        action TEXT NOT NULL,
                        target_type TEXT,
                        target_id TEXT,
                        details TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create chat_history table for conversation memory
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        sources TEXT,
                        follow_up_questions TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully with all tables")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during database initialization: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection with proper configuration.
        
        Returns:
            sqlite3.Connection: Configured database connection
        """
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            conn.execute("PRAGMA journal_mode = WAL")  # Enable WAL mode for better concurrency
            return conn
        except sqlite3.Error as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def execute_query(self, query: str, params: Tuple = ()) -> pd.DataFrame:
        """
        Execute SELECT query and return results as DataFrame.
        
        Args:
            query: SQL SELECT query
            params: Query parameters tuple
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                self.logger.debug(f"Query executed successfully: {query[:50]}...")
                return df
                
        except sqlite3.Error as e:
            self.logger.error(f"Query execution failed: {e}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during query execution: {e}")
            raise
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """
        Execute INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query
            params: Query parameters tuple
            
        Returns:
            int: Number of affected rows
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                affected_rows = cursor.rowcount
                self._last_insert_id = cursor.lastrowid
                self.logger.debug(f"Update executed successfully, {affected_rows} rows affected")
                return affected_rows
                
        except sqlite3.Error as e:
            self.logger.error(f"Update execution failed: {e}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during update execution: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute query with multiple parameter sets (batch operation).
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
            
        Returns:
            int: Number of affected rows
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                affected_rows = cursor.rowcount
                self.logger.debug(f"Batch update executed successfully, {affected_rows} rows affected")
                return affected_rows
                
        except sqlite3.Error as e:
            self.logger.error(f"Batch update execution failed: {e}")
            self.logger.error(f"Query: {query}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during batch update execution: {e}")
            raise
    
    def get_last_insert_id(self) -> Optional[int]:
        """
        Get the ID of the last inserted row.
        
        Returns the rowid captured from the most recent execute_update() call.
        Call immediately after an insert for reliable results.
        
        Returns:
            Optional[int]: Last insert ID or None if no recent insert
        """
        return self._last_insert_id
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        try:
            query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """
            result = self.execute_query(query, (table_name,))
            return len(result) > 0
        except Exception as e:
            self.logger.error(f"Error checking table existence: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get information about table structure.
        
        Args:
            table_name: Name of the table
            
        Returns:
            pd.DataFrame: Table structure information
            
        Raises:
            ValueError: If table_name contains invalid characters
        """
        import re
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        try:
            query = f"PRAGMA table_info({table_name})"
            return self.execute_query(query)
        except Exception as e:
            self.logger.error(f"Error getting table info for {table_name}: {e}")
            raise
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for the backup file
            
        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            with self.get_connection() as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            self.logger.info(f"Database backed up successfully to {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def close(self) -> None:
        """Close database connection and cleanup resources."""
        # SQLite connections are automatically closed when using context managers
        # This method is provided for interface completeness
        self.logger.info("Database manager closed")

    def save_chat_message(self, username: str, session_id: str, role: str, content: str,
                          sources: list = None, follow_up_questions: list = None) -> int:
        """Save a chat message to history."""
        import json
        sources_json = json.dumps(sources) if sources else None
        follow_up_json = json.dumps(follow_up_questions) if follow_up_questions else None
        
        return self.execute_update(
            """INSERT INTO chat_history 
               (username, session_id, role, content, sources, follow_up_questions)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (username, session_id, role, content, sources_json, follow_up_json)
        )

    def get_chat_history(self, username: str, session_id: str, limit: int = 50) -> list:
        """Get chat history for a session."""
        import json
        import math
        results = self.execute_query(
            """SELECT role, content, sources, follow_up_questions, timestamp
               FROM chat_history
               WHERE username = ? AND session_id = ?
               ORDER BY timestamp ASC
               LIMIT ?""",
            (username, session_id, limit)
        )
        
        history = []
        for _, row in results.iterrows():
            msg = {
                'role': row['role'],
                'content': row['content'],
                'timestamp': row['timestamp']
            }
            # Handle None/NaN values
            sources = row['sources']
            if sources is not None and not (isinstance(sources, float) and math.isnan(sources)):
                msg['sources'] = json.loads(sources)
            
            follow_up = row['follow_up_questions']
            if follow_up is not None and not (isinstance(follow_up, float) and math.isnan(follow_up)):
                msg['follow_up_questions'] = json.loads(follow_up)
            
            history.append(msg)
        
        return history

    def get_user_sessions(self, username: str) -> list:
        """Get all session IDs for a user."""
        results = self.execute_query(
            """SELECT DISTINCT session_id, MAX(timestamp) as last_activity
               FROM chat_history
               WHERE username = ?
               GROUP BY session_id
               ORDER BY last_activity DESC""",
            (username,)
        )
        return [(row['session_id'], row['last_activity']) for _, row in results.iterrows()]

    def clear_chat_history(self, username: str, session_id: str) -> int:
        """Clear chat history for a session."""
        return self.execute_update(
            "DELETE FROM chat_history WHERE username = ? AND session_id = ?",
            (username, session_id)
        )



# Global database manager instance
_db_manager = None

def get_database_manager(db_path: str = "platform.db") -> DatabaseManager:
    """
    Get singleton database manager instance.
    
    Args:
        db_path: Path to database file
        
    Returns:
        DatabaseManager: Singleton database manager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
        _db_manager.init_database()
    return _db_manager
