"""
Database utilities for 广告思想简史 Platform (China-compatible version)

This module provides database connectivity that works in China without Google APIs.
Uses SQLite database instead of Google Sheets for data persistence.
"""

import pandas as pd
import streamlit as st
from modules.database import get_database_manager
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Legacy constants (kept for compatibility)
SHEET_NAME = "Database"
LEGACY_SPREADSHEET_ID = "1rkMVLvh3JrBq_tbi4Ho0qjCDAP3vYdNuWOEjYpkJLNU"


@st.cache_resource
def connect():
    """
    Create a database connection using SQLite instead of Google Sheets.
    This function maintains API compatibility with the original Google Sheets version.
    
    Returns:
        DatabaseManager: Database manager instance
    """
    try:
        db_manager = get_database_manager()
        logger.info("Database connection established successfully")
        return db_manager
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def collect(db_connector) -> pd.DataFrame:
    """
    Collect data from database (replaces Google Sheets collection).
    
    Args:
        db_connector: DatabaseManager instance
        
    Returns:
        pd.DataFrame: Data from the database
    """
    try:
        # Query user activity data (equivalent to the original A:C range)
        query = """
            SELECT username, action, timestamp 
            FROM user_activity 
            ORDER BY timestamp DESC 
            LIMIT 1000
        """
        df = db_connector.execute_query(query)
        logger.info(f"Collected {len(df)} records from database")
        return df
    except Exception as e:
        logger.error(f"Failed to collect data: {e}")
        # Return empty DataFrame with expected columns for compatibility
        return pd.DataFrame(columns=['username', 'action', 'timestamp'])


def insert(db_connector, row) -> None:
    """
    Insert data into database (replaces Google Sheets insertion).
    
    Args:
        db_connector: DatabaseManager instance
        row: List of values to insert [username, action, details]
    """
    try:
        if len(row) >= 2:
            username = row[0] if len(row) > 0 else 'anonymous'
            action = row[1] if len(row) > 1 else 'unknown'
            details = row[2] if len(row) > 2 else None
            
            query = """
                INSERT INTO user_activity (username, action, details) 
                VALUES (?, ?, ?)
            """
            db_connector.execute_update(query, (username, action, details))
            logger.info(f"Inserted activity record: {username} - {action}")
        else:
            logger.warning("Invalid row data provided for insertion")
    except Exception as e:
        logger.error(f"Failed to insert data: {e}")
        raise


# Compatibility functions for legacy code
def get_gsheet_url():
    """Return a placeholder URL since Google Sheets is not accessible in China."""
    return f"Database stored locally (Google Sheets not available in China)"


def is_china_compatible():
    """Check if the current database setup is China-compatible."""
    return True  # SQLite is always China-compatible