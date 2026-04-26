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
                        FOREIGN KEY (parent_id) REFERENCES comments (id)
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
                        total_feedback INTEGER DEFAULT 0
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
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
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
        
        Returns:
            Optional[int]: Last insert ID or None if no recent insert
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get last insert ID: {e}")
            return None
    
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
        """
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