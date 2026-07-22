"""
Article Review Notification System

Handles notifications for article review workflow events:
- Article submitted for review
- Article approved/published
- Article rejected
- Changes requested
"""

import logging
import pandas as pd
from typing import Optional, List
from utils.logger import create_logger
from modules.database import DatabaseManager


class ArticleNotificationSystem:
    """Manages notifications for article review workflow."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = create_logger('ArticleNotificationSystem')
    
    def create_notification(
        self,
        article_id: int,
        target_username: str,
        notification_type: str,
        message: Optional[str] = None
    ) -> bool:
        """
        Create a notification for article review event.
        
        Args:
            article_id: Article ID
            target_username: Username to notify
            notification_type: Type (submitted, approved, rejected, changes_requested)
            message: Optional message/reason
            
        Returns:
            bool: True if created successfully
        """
        try:
            query = """
                INSERT INTO article_notifications 
                (article_id, target_username, notification_type, message)
                VALUES (?, ?, ?, ?)
            """
            affected = self.db_manager.execute_update(
                query, (article_id, target_username, notification_type, message)
            )
            if affected > 0:
                self.logger.info(
                    f"Notification created for {target_username}: {notification_type} on article {article_id}"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error creating notification: {e}")
            return False
    
    def get_user_notifications(
        self, 
        username: str, 
        unread_only: bool = True
    ) -> pd.DataFrame:
        """Get notifications for a user."""
        try:
            query = """
                SELECT n.*, a.title as article_title
                FROM article_notifications n
                LEFT JOIN articles a ON n.article_id = a.id
                WHERE n.target_username = ?
            """
            if unread_only:
                query += " AND n.is_read = 0"
            query += " ORDER BY n.timestamp DESC"
            
            return self.db_manager.execute_query(query, (username,))
        except Exception as e:
            self.logger.error(f"Error getting notifications: {e}")
            return pd.DataFrame()
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        try:
            query = "UPDATE article_notifications SET is_read = 1 WHERE id = ?"
            affected = self.db_manager.execute_update(query, (notification_id,))
            return affected > 0
        except Exception as e:
            self.logger.error(f"Error marking notification as read: {e}")
            return False
    
    def mark_all_as_read(self, username: str) -> int:
        """Mark all notifications as read for a user."""
        try:
            query = "UPDATE article_notifications SET is_read = 1 WHERE target_username = ? AND is_read = 0"
            return self.db_manager.execute_update(query, (username,))
        except Exception as e:
            self.logger.error(f"Error marking all notifications as read: {e}")
            return 0
    
    def get_unread_count(self, username: str) -> int:
        """Get count of unread notifications."""
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM article_notifications 
                WHERE target_username = ? AND is_read = 0
            """
            result = self.db_manager.execute_query(query, (username,))
            return int(result.iloc[0]['count']) if not result.empty else 0
        except Exception as e:
            self.logger.error(f"Error getting unread count: {e}")
            return 0
    
    def notify_article_submitted(self, article_id: int, author_username: str, admin_usernames: List[str]) -> None:
        """Notify admins when article is submitted for review."""
        for admin_username in admin_usernames:
            if admin_username != author_username:
                self.create_notification(
                    article_id, admin_username, 'submitted',
                    f"New article submitted for review"
                )
    
    def notify_article_approved(self, article_id: int, author_username: str) -> None:
        """Notify author when article is approved."""
        self.create_notification(
            article_id, author_username, 'approved',
            "Your article has been approved and published!"
        )
    
    def notify_article_rejected(self, article_id: int, author_username: str, reason: str) -> None:
        """Notify author when article is rejected."""
        self.create_notification(
            article_id, author_username, 'rejected',
            f"Your article was rejected. Reason: {reason}"
        )
    
    def notify_changes_requested(self, article_id: int, author_username: str, feedback: str) -> None:
        """Notify author when changes are requested."""
        self.create_notification(
            article_id, author_username, 'changes_requested',
            f"Changes requested on your article. Feedback: {feedback}"
        )


def get_article_notification_system(db_manager: DatabaseManager) -> ArticleNotificationSystem:
    """Factory function to create ArticleNotificationSystem instance."""
    return ArticleNotificationSystem(db_manager)
