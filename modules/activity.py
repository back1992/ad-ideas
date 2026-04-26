"""
Activity Logging System for 广告思想简史 Platform

This module provides comprehensive user activity tracking and logging
with privacy-compliant data collection and retrieval capabilities.
"""

import logging
from utils.logger import create_logger
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from modules.database import DatabaseManager


class ActivityLogger:
    """
    Centralized activity logging system for tracking user actions.
    
    Handles logging of all user activities across the platform including
    authentication, content interaction, feedback, comments, and article management.
    Implements privacy-compliant data collection with no sensitive information storage.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize ActivityLogger with database manager.
        
        Args:
            db_manager: Database manager instance for data persistence
        """
        self.db_manager = db_manager
        self.logger = create_logger('ActivityLogger')
        
    
    def log_activity(self, username: str, action: str, 
                    target_type: Optional[str] = None,
                    target_id: Optional[str] = None,
                    details: Optional[str] = None) -> bool:
        """
        Log a user activity to the database.
        
        Args:
            username: Username performing the action
            action: Action type (e.g., 'login', 'comment', 'feedback', 'article_create')
            target_type: Type of target content (optional)
            target_id: Target content identifier (optional)
            details: Additional details about the action (optional, privacy-compliant)
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            # Sanitize details to ensure no sensitive information
            sanitized_details = self._sanitize_details(details)
            
            query = """
                INSERT INTO user_activity 
                (username, action, target_type, target_id, details)
                VALUES (?, ?, ?, ?, ?)
            """
            
            affected_rows = self.db_manager.execute_update(
                query,
                (username, action, target_type, target_id, sanitized_details)
            )
            
            if affected_rows > 0:
                self.logger.debug(f"Activity logged: {username} - {action}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error logging activity: {e}")
            return False
    
    def log_login(self, username: str, success: bool = True) -> bool:
        """
        Log user login activity.
        
        Args:
            username: Username attempting login
            success: Whether login was successful
            
        Returns:
            bool: True if logged successfully
        """
        action = 'login' if success else 'login_failed'
        details = 'User logged in successfully' if success else 'Failed login attempt'
        return self.log_activity(username, action, details=details)
    
    def log_logout(self, username: str) -> bool:
        """
        Log user logout activity.
        
        Args:
            username: Username logging out
            
        Returns:
            bool: True if logged successfully
        """
        return self.log_activity(username, 'logout', details='User logged out')
    
    def log_feedback(self, username: str, target_type: str, target_id: str,
                    feedback_type: str) -> bool:
        """
        Log feedback submission activity.
        
        Args:
            username: Username submitting feedback
            target_type: Type of content receiving feedback
            target_id: Content identifier
            feedback_type: Type of feedback (thumbs, stars, faces)
            
        Returns:
            bool: True if logged successfully
        """
        return self.log_activity(
            username,
            'feedback_submitted',
            target_type,
            target_id,
            f'Submitted {feedback_type} feedback'
        )
    
    def log_comment(self, username: str, target_type: str, target_id: str,
                   is_reply: bool = False) -> bool:
        """
        Log comment posting activity.
        
        Args:
            username: Username posting comment
            target_type: Type of content being commented on
            target_id: Content identifier
            is_reply: Whether this is a reply to another comment
            
        Returns:
            bool: True if logged successfully
        """
        action = 'comment_reply' if is_reply else 'comment_posted'
        details = 'Posted reply' if is_reply else 'Posted comment'
        return self.log_activity(username, action, target_type, target_id, details)
    
    def log_article_action(self, username: str, action: str, article_id: Optional[int],
                          article_title: Optional[str] = None) -> bool:
        """
        Log article-related activity.
        
        Args:
            username: Username performing action
            action: Action type (create, edit, publish, delete, view)
            article_id: Article identifier
            article_title: Article title (truncated for privacy)
            
        Returns:
            bool: True if logged successfully
        """
        details = None
        if article_title:
            # Truncate title to avoid storing too much content
            details = f"Article: {article_title[:50]}..."
        
        return self.log_activity(
            username,
            f'article_{action}',
            'article',
            str(article_id) if article_id else None,
            details
        )
    
    def log_content_view(self, username: str, target_type: str, target_id: str) -> bool:
        """
        Log content viewing activity.
        
        Args:
            username: Username viewing content
            target_type: Type of content being viewed
            target_id: Content identifier
            
        Returns:
            bool: True if logged successfully
        """
        return self.log_activity(
            username,
            'content_viewed',
            target_type,
            target_id,
            f'Viewed {target_type}'
        )
    
    def log_moderation_action(self, username: str, action: str, 
                             target_type: str, target_id: str) -> bool:
        """
        Log moderation activity.
        
        Args:
            username: Username performing moderation
            action: Moderation action (approve, reject, remove, edit)
            target_type: Type of content being moderated
            target_id: Content identifier
            
        Returns:
            bool: True if logged successfully
        """
        return self.log_activity(
            username,
            f'moderation_{action}',
            target_type,
            target_id,
            f'Moderation action: {action}'
        )
    
    def get_user_activity(self, username: str, limit: int = 100,
                         action_filter: Optional[str] = None) -> pd.DataFrame:
        """
        Get activity history for a specific user.
        
        Args:
            username: Username to get activity for
            limit: Maximum number of records to return
            action_filter: Filter by specific action type (optional)
            
        Returns:
            pd.DataFrame: User activity history
        """
        try:
            if action_filter:
                query = """
                    SELECT * FROM user_activity 
                    WHERE username = ? AND action = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                params = (username, action_filter, limit)
            else:
                query = """
                    SELECT * FROM user_activity 
                    WHERE username = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                params = (username, limit)
            
            return self.db_manager.execute_query(query, params)
            
        except Exception as e:
            self.logger.error(f"Error getting user activity: {e}")
            return pd.DataFrame()
    
    def get_recent_activity(self, hours: int = 24, limit: int = 100) -> pd.DataFrame:
        """
        Get recent activity across all users.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of records to return
            
        Returns:
            pd.DataFrame: Recent activity data
        """
        try:
            query = """
                SELECT * FROM user_activity 
                WHERE timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
                LIMIT ?
            """
            
            return self.db_manager.execute_query(query, (hours, limit))
            
        except Exception as e:
            self.logger.error(f"Error getting recent activity: {e}")
            return pd.DataFrame()
    
    def get_activity_by_action(self, action: str, limit: int = 100) -> pd.DataFrame:
        """
        Get activity filtered by action type.
        
        Args:
            action: Action type to filter by
            limit: Maximum number of records to return
            
        Returns:
            pd.DataFrame: Filtered activity data
        """
        try:
            query = """
                SELECT * FROM user_activity 
                WHERE action = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            
            return self.db_manager.execute_query(query, (action, limit))
            
        except Exception as e:
            self.logger.error(f"Error getting activity by action: {e}")
            return pd.DataFrame()
    
    def get_activity_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary statistics of platform activity.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Activity summary statistics
        """
        try:
            # Total activities
            query_total = """
                SELECT COUNT(*) as total_activities
                FROM user_activity
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            """
            total_result = self.db_manager.execute_query(query_total, (days,))
            total_activities = total_result.iloc[0]['total_activities'] if not total_result.empty else 0
            
            # Unique active users
            query_users = """
                SELECT COUNT(DISTINCT username) as active_users
                FROM user_activity
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            """
            users_result = self.db_manager.execute_query(query_users, (days,))
            active_users = users_result.iloc[0]['active_users'] if not users_result.empty else 0
            
            # Activity by type
            query_by_type = """
                SELECT action, COUNT(*) as count
                FROM user_activity
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY action
                ORDER BY count DESC
            """
            by_type_result = self.db_manager.execute_query(query_by_type, (days,))
            
            # Most active users
            query_top_users = """
                SELECT username, COUNT(*) as activity_count
                FROM user_activity
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY username
                ORDER BY activity_count DESC
                LIMIT 10
            """
            top_users_result = self.db_manager.execute_query(query_top_users, (days,))
            
            return {
                'total_activities': int(total_activities),
                'active_users': int(active_users),
                'activities_per_user': round(total_activities / active_users, 2) if active_users > 0 else 0,
                'activity_by_type': by_type_result.to_dict('records') if not by_type_result.empty else [],
                'top_users': top_users_result.to_dict('records') if not top_users_result.empty else [],
                'period_days': days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting activity summary: {e}")
            return {
                'total_activities': 0,
                'active_users': 0,
                'activities_per_user': 0,
                'activity_by_type': [],
                'top_users': [],
                'period_days': days
            }
    
    def get_daily_activity_trend(self, days: int = 30) -> pd.DataFrame:
        """
        Get daily activity trend data.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            pd.DataFrame: Daily activity counts
        """
        try:
            query = """
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as activity_count,
                    COUNT(DISTINCT username) as unique_users
                FROM user_activity
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """
            
            return self.db_manager.execute_query(query, (days,))
            
        except Exception as e:
            self.logger.error(f"Error getting daily activity trend: {e}")
            return pd.DataFrame()
    
    def get_user_engagement_metrics(self, username: str, days: int = 30) -> Dict[str, Any]:
        """
        Get engagement metrics for a specific user.
        
        Args:
            username: Username to analyze
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: User engagement metrics
        """
        try:
            # Total activities
            query_total = """
                SELECT COUNT(*) as total_activities
                FROM user_activity
                WHERE username = ? AND timestamp >= datetime('now', '-' || ? || ' days')
            """
            total_result = self.db_manager.execute_query(query_total, (username, days))
            total_activities = total_result.iloc[0]['total_activities'] if not total_result.empty else 0
            
            # Activities by type
            query_by_type = """
                SELECT action, COUNT(*) as count
                FROM user_activity
                WHERE username = ? AND timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY action
                ORDER BY count DESC
            """
            by_type_result = self.db_manager.execute_query(query_by_type, (username, days))
            
            # Active days
            query_active_days = """
                SELECT COUNT(DISTINCT DATE(timestamp)) as active_days
                FROM user_activity
                WHERE username = ? AND timestamp >= datetime('now', '-' || ? || ' days')
            """
            active_days_result = self.db_manager.execute_query(query_active_days, (username, days))
            active_days = active_days_result.iloc[0]['active_days'] if not active_days_result.empty else 0
            
            # Last activity
            query_last = """
                SELECT timestamp, action, details
                FROM user_activity
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """
            last_result = self.db_manager.execute_query(query_last, (username,))
            last_activity = last_result.iloc[0].to_dict() if not last_result.empty else None
            
            return {
                'total_activities': int(total_activities),
                'active_days': int(active_days),
                'activities_per_day': round(total_activities / days, 2) if days > 0 else 0,
                'activity_by_type': by_type_result.to_dict('records') if not by_type_result.empty else [],
                'last_activity': last_activity,
                'period_days': days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user engagement metrics: {e}")
            return {
                'total_activities': 0,
                'active_days': 0,
                'activities_per_day': 0,
                'activity_by_type': [],
                'last_activity': None,
                'period_days': days
            }
    
    def _sanitize_details(self, details: Optional[str]) -> Optional[str]:
        """
        Sanitize activity details to ensure privacy compliance.
        
        Removes or truncates sensitive information from activity details.
        
        Args:
            details: Raw details string
            
        Returns:
            Optional[str]: Sanitized details
        """
        if not details:
            return None
        
        # Truncate long details to avoid storing too much content
        max_length = 500
        if len(details) > max_length:
            details = details[:max_length] + "..."
        
        # Remove any potential email addresses (basic pattern)
        import re
        details = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[email]', details)
        
        # Remove any potential phone numbers (basic pattern)
        details = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[phone]', details)
        
        return details
    
    def anonymize_user_data(self, username: str) -> bool:
        """
        Anonymize activity data for a specific user (for privacy compliance).
        
        Replaces username with anonymized identifier while preserving activity patterns.
        
        Args:
            username: Username to anonymize
            
        Returns:
            bool: True if successful
        """
        try:
            # Generate anonymized identifier
            import hashlib
            anon_id = f"anon_{hashlib.md5(username.encode()).hexdigest()[:8]}"
            
            query = """
                UPDATE user_activity
                SET username = ?
                WHERE username = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, (anon_id, username))
            
            if affected_rows > 0:
                self.logger.info(f"Anonymized activity data for user: {username}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error anonymizing user data: {e}")
            return False
    
    def delete_user_activity(self, username: str, days_to_keep: int = 0) -> bool:
        """
        Delete activity data for a user (for privacy compliance).
        
        Args:
            username: Username to delete activity for
            days_to_keep: Keep activity from last N days (0 = delete all)
            
        Returns:
            bool: True if successful
        """
        try:
            if days_to_keep > 0:
                query = """
                    DELETE FROM user_activity
                    WHERE username = ? 
                    AND timestamp < datetime('now', '-' || ? || ' days')
                """
                params = (username, days_to_keep)
            else:
                query = """
                    DELETE FROM user_activity
                    WHERE username = ?
                """
                params = (username,)
            
            affected_rows = self.db_manager.execute_update(query, params)
            
            self.logger.info(f"Deleted activity data for user: {username} (kept last {days_to_keep} days)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting user activity: {e}")
            return False


# Global activity logger instance
_activity_logger = None

def get_activity_logger(db_manager: DatabaseManager) -> ActivityLogger:
    """
    Get singleton activity logger instance.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        ActivityLogger: Singleton activity logger instance
    """
    global _activity_logger
    if _activity_logger is None:
        _activity_logger = ActivityLogger(db_manager)
    return _activity_logger
