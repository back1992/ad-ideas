"""
Unified Moderation System for 广告思想简史 Platform

This module provides a unified moderation dashboard combining article and comment
moderation with bulk actions and comprehensive audit logging.
"""

import streamlit as st
import logging
from utils.logger import create_logger
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from modules.database import DatabaseManager
from modules.auth import AuthManager
from modules.comments import CommentModerationSystem, get_comment_moderation_system
from modules.articles import ArticleReviewSystem, get_article_review_system


class UnifiedModerationDashboard:
    """
    Unified moderation dashboard combining articles and comments.
    
    Provides a centralized interface for administrators to moderate all
    user-generated content with bulk actions and audit logging.
    """
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager,
                 comment_mod_system: CommentModerationSystem,
                 article_review_system: ArticleReviewSystem):
        """
        Initialize unified moderation dashboard.
        
        Args:
            db_manager: Database manager instance
            auth_manager: Authentication manager instance
            comment_mod_system: Comment moderation system instance
            article_review_system: Article review system instance
        """
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.comment_mod_system = comment_mod_system
        self.article_review_system = article_review_system
        self.logger = create_logger('UnifiedModerationDashboard')
    
    
    def show_dashboard(self, admin_username: str) -> None:
        """
        Display unified moderation dashboard.
        
        Args:
            admin_username: Username of administrator
        """
        try:
            # Check admin permissions
            if not self.auth_manager.is_admin(admin_username):
                st.error("Access denied. Only administrators can access the moderation dashboard.")
                return
            
            st.markdown("# 🛡️ Unified Moderation Dashboard")
            st.markdown("Manage all platform content from one central location")
            
            # Get moderation statistics
            stats = self.get_moderation_statistics()
            
            # Display statistics overview
            self._display_statistics_overview(stats)
            
            st.markdown("---")
            
            # Create tabs for different moderation areas
            tab1, tab2, tab3, tab4 = st.tabs([
                f"📋 Articles ({stats['articles_pending']})",
                f"💬 Comments ({stats['comments_reported']})",
                f"📊 Audit Log",
                f"⚡ Bulk Actions"
            ])
            
            with tab1:
                self._display_article_moderation(admin_username)
            
            with tab2:
                self._display_comment_moderation(admin_username)
            
            with tab3:
                self._display_audit_log(admin_username)
            
            with tab4:
                self._display_bulk_actions(admin_username)
            
        except Exception as e:
            self.logger.error(f"Error displaying moderation dashboard: {e}")
            st.error("Unable to load moderation dashboard.")
    
    def get_moderation_statistics(self) -> Dict[str, int]:
        """
        Get moderation statistics for dashboard overview.
        
        Returns:
            Dict[str, int]: Statistics dictionary
        """
        try:
            stats = {
                'articles_pending': 0,
                'articles_total': 0,
                'comments_reported': 0,
                'comments_unapproved': 0,
                'comments_total': 0,
                'moderation_actions_today': 0
            }
            
            # Get article statistics
            articles_query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'review' THEN 1 ELSE 0 END) as pending
                FROM articles
            """
            articles_result = self.db_manager.execute_query(articles_query)
            if not articles_result.empty:
                stats['articles_total'] = int(articles_result.iloc[0]['total'])
                stats['articles_pending'] = int(articles_result.iloc[0]['pending'])
            
            # Get comment statistics
            comments_query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_approved = 0 THEN 1 ELSE 0 END) as unapproved
                FROM comments
            """
            comments_result = self.db_manager.execute_query(comments_query)
            if not comments_result.empty:
                stats['comments_total'] = int(comments_result.iloc[0]['total'])
                stats['comments_unapproved'] = int(comments_result.iloc[0]['unapproved'])
            
            # Get reported comments count
            reported_query = """
                SELECT COUNT(DISTINCT target_id) as reported
                FROM user_activity
                WHERE action = 'comment_reported'
                AND target_id IN (SELECT CAST(id AS TEXT) FROM comments WHERE is_approved = 1)
            """
            reported_result = self.db_manager.execute_query(reported_query)
            if not reported_result.empty:
                stats['comments_reported'] = int(reported_result.iloc[0]['reported'])
            
            # Get moderation actions today
            actions_query = """
                SELECT COUNT(*) as actions
                FROM user_activity
                WHERE action IN (
                    'article_approved', 'article_rejected', 'article_changes_requested',
                    'comment_approved', 'comment_rejected', 'comment_removed', 'comment_edited'
                )
                AND DATE(timestamp) = DATE('now')
            """
            actions_result = self.db_manager.execute_query(actions_query)
            if not actions_result.empty:
                stats['moderation_actions_today'] = int(actions_result.iloc[0]['actions'])
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting moderation statistics: {e}")
            return {
                'articles_pending': 0,
                'articles_total': 0,
                'comments_reported': 0,
                'comments_unapproved': 0,
                'comments_total': 0,
                'moderation_actions_today': 0
            }
    
    def _display_statistics_overview(self, stats: Dict[str, int]) -> None:
        """Display statistics overview cards."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📋 Articles Pending Review",
                stats['articles_pending'],
                delta=f"{stats['articles_total']} total"
            )
        
        with col2:
            st.metric(
                "🚩 Comments Reported",
                stats['comments_reported'],
                delta="Needs attention" if stats['comments_reported'] > 0 else "All clear"
            )
        
        with col3:
            st.metric(
                "💬 Comments Unapproved",
                stats['comments_unapproved'],
                delta=f"{stats['comments_total']} total"
            )
        
        with col4:
            st.metric(
                "⚡ Actions Today",
                stats['moderation_actions_today']
            )
    
    def _display_article_moderation(self, admin_username: str) -> None:
        """Display article moderation interface."""
        st.markdown("### 📋 Article Moderation")
        
        # Use existing article review system
        self.article_review_system.show_review_queue(admin_username)
    
    def _display_comment_moderation(self, admin_username: str) -> None:
        """Display comment moderation interface."""
        st.markdown("### 💬 Comment Moderation")
        
        # Use existing comment moderation system
        self.comment_mod_system.display_moderation_queue(admin_username)
    
    def _display_audit_log(self, admin_username: str) -> None:
        """Display moderation audit log."""
        st.markdown("### 📊 Moderation Audit Log")
        st.markdown("View all moderation actions taken on the platform")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            action_filter = st.selectbox(
                "Filter by Action",
                ["All Actions", "Article Actions", "Comment Actions", "User Actions"],
                key="audit_action_filter"
            )
        
        with col2:
            days_back = st.selectbox(
                "Time Period",
                [1, 7, 30, 90, 365],
                format_func=lambda x: f"Last {x} day{'s' if x > 1 else ''}",
                index=1,
                key="audit_days_filter"
            )
        
        with col3:
            moderator_filter = st.text_input(
                "Filter by Moderator",
                placeholder="Enter username",
                key="audit_moderator_filter"
            )
        
        # Get audit log
        audit_log = self.get_audit_log(
            action_filter=action_filter,
            days_back=days_back,
            moderator=moderator_filter if moderator_filter else None
        )
        
        if audit_log.empty:
            st.info("No moderation actions found for the selected filters.")
            return
        
        st.markdown(f"**Found {len(audit_log)} moderation action(s)**")
        
        # Display audit log
        for _, log_entry in audit_log.iterrows():
            with st.expander(
                f"{log_entry['action']} by {log_entry['username']} - "
                f"{log_entry['timestamp'][:16]}"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Moderator:** {log_entry['username']}")
                    st.markdown(f"**Action:** {log_entry['action']}")
                    st.markdown(f"**Timestamp:** {log_entry['timestamp']}")
                
                with col2:
                    if log_entry['target_type']:
                        st.markdown(f"**Target Type:** {log_entry['target_type']}")
                    if log_entry['target_id']:
                        st.markdown(f"**Target ID:** {log_entry['target_id']}")
                
                if log_entry['details']:
                    st.markdown("**Details:**")
                    st.markdown(f"> {log_entry['details']}")
    
    def get_audit_log(self, action_filter: str = "All Actions",
                     days_back: int = 7, moderator: Optional[str] = None) -> pd.DataFrame:
        """
        Get moderation audit log with filters.
        
        Args:
            action_filter: Filter by action type
            days_back: Number of days to look back
            moderator: Filter by moderator username
            
        Returns:
            pd.DataFrame: Audit log entries
        """
        try:
            # Build query based on filters
            query = """
                SELECT *
                FROM user_activity
                WHERE action IN (
                    'article_approved', 'article_rejected', 'article_changes_requested',
                    'comment_approved', 'comment_rejected', 'comment_removed', 'comment_edited',
                    'user_role_changed', 'user_suspended', 'user_activated'
                )
            """
            params = []
            
            # Apply action filter
            if action_filter == "Article Actions":
                query += " AND action LIKE 'article_%'"
            elif action_filter == "Comment Actions":
                query += " AND action LIKE 'comment_%'"
            elif action_filter == "User Actions":
                query += " AND action LIKE 'user_%'"
            
            # Apply time filter
            query += " AND datetime(timestamp) >= datetime('now', '-' || ? || ' days')"
            params.append(days_back)
            
            # Apply moderator filter
            if moderator:
                query += " AND username = ?"
                params.append(moderator)
            
            query += " ORDER BY timestamp DESC LIMIT 100"
            
            return self.db_manager.execute_query(query, tuple(params))
            
        except Exception as e:
            self.logger.error(f"Error getting audit log: {e}")
            return pd.DataFrame()
    
    def _display_bulk_actions(self, admin_username: str) -> None:
        """Display bulk moderation actions interface."""
        st.markdown("### ⚡ Bulk Moderation Actions")
        st.markdown("Perform actions on multiple items at once for efficiency")
        
        # Select content type
        content_type = st.radio(
            "Select content type:",
            ["Comments", "Articles"],
            horizontal=True,
            key="bulk_content_type"
        )
        
        if content_type == "Comments":
            self._display_bulk_comment_actions(admin_username)
        else:
            self._display_bulk_article_actions(admin_username)
    
    def _display_bulk_comment_actions(self, admin_username: str) -> None:
        """Display bulk comment moderation actions."""
        st.markdown("#### Bulk Comment Actions")
        
        # Get comments that need moderation
        reported_comments = self.comment_mod_system.get_reported_comments()
        unapproved_comments = self.comment_mod_system.get_unapproved_comments()
        
        # Select which queue to work with
        queue_type = st.selectbox(
            "Select queue:",
            ["Reported Comments", "Unapproved Comments"],
            key="bulk_comment_queue"
        )
        
        if queue_type == "Reported Comments":
            comments_df = reported_comments
            if comments_df.empty:
                st.success("✅ No reported comments!")
                return
        else:
            comments_df = unapproved_comments
            if comments_df.empty:
                st.success("✅ No unapproved comments!")
                return
        
        st.markdown(f"**{len(comments_df)} comment(s) available for bulk action**")
        
        # Initialize session state for selections
        if 'bulk_comment_selections' not in st.session_state:
            st.session_state.bulk_comment_selections = []
        
        # Display comments with checkboxes
        st.markdown("**Select comments:**")
        
        selected_ids = []
        for idx, comment in comments_df.iterrows():
            if queue_type == "Reported Comments":
                comment_id = comment['comment_id']
                # Get the actual comment
                actual_comment = self.comment_mod_system.get_comment_by_id(comment_id)
                if actual_comment:
                    label = f"ID {comment_id}: {actual_comment['content'][:50]}... (by {actual_comment['username']})"
                else:
                    continue
            else:
                comment_id = comment['id']
                label = f"ID {comment_id}: {comment['content'][:50]}... (by {comment['username']})"
            
            if st.checkbox(label, key=f"bulk_comment_{comment_id}"):
                selected_ids.append(comment_id)
        
        if selected_ids:
            st.markdown(f"**{len(selected_ids)} comment(s) selected**")
            
            # Bulk action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Approve All Selected", type="primary"):
                    success_count = self.bulk_approve_comments(selected_ids, admin_username)
                    st.success(f"Approved {success_count} comment(s)")
                    st.rerun()
            
            with col2:
                if st.button("❌ Remove All Selected"):
                    success_count = self.bulk_remove_comments(selected_ids, admin_username)
                    st.success(f"Removed {success_count} comment(s)")
                    st.rerun()
            
            with col3:
                if st.button("🔄 Clear Selection"):
                    st.session_state.bulk_comment_selections = []
                    st.rerun()
        else:
            st.info("Select comments to perform bulk actions")
    
    def _display_bulk_article_actions(self, admin_username: str) -> None:
        """Display bulk article moderation actions."""
        st.markdown("#### Bulk Article Actions")
        
        # Get articles pending review
        from modules.articles import get_article_manager
        article_manager = get_article_manager(self.db_manager, self.auth_manager)
        pending_articles = article_manager.get_articles(status='review')
        
        if pending_articles.empty:
            st.success("✅ No articles pending review!")
            return
        
        st.markdown(f"**{len(pending_articles)} article(s) pending review**")
        
        # Display articles with checkboxes
        st.markdown("**Select articles:**")
        
        selected_ids = []
        for _, article in pending_articles.iterrows():
            label = f"ID {article['id']}: {article['title']} (by {article['author']})"
            if st.checkbox(label, key=f"bulk_article_{article['id']}"):
                selected_ids.append(article['id'])
        
        if selected_ids:
            st.markdown(f"**{len(selected_ids)} article(s) selected**")
            
            # Bulk action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Approve & Publish All", type="primary"):
                    success_count = self.bulk_approve_articles(selected_ids, admin_username)
                    st.success(f"Approved and published {success_count} article(s)")
                    st.rerun()
            
            with col2:
                if st.button("❌ Reject All"):
                    reason = st.text_input(
                        "Rejection reason:",
                        key="bulk_reject_reason"
                    )
                    if reason:
                        success_count = self.bulk_reject_articles(selected_ids, admin_username, reason)
                        st.success(f"Rejected {success_count} article(s)")
                        st.rerun()
                    else:
                        st.warning("Please provide a rejection reason")
            
            with col3:
                if st.button("🔄 Clear Selection"):
                    st.rerun()
        else:
            st.info("Select articles to perform bulk actions")
    
    def bulk_approve_comments(self, comment_ids: List[int], admin_username: str) -> int:
        """
        Approve multiple comments at once.
        
        Args:
            comment_ids: List of comment IDs to approve
            admin_username: Username of administrator
            
        Returns:
            int: Number of comments successfully approved
        """
        success_count = 0
        for comment_id in comment_ids:
            if self.comment_mod_system.approve_comment(comment_id, admin_username):
                success_count += 1
        
        self.logger.info(f"Bulk approved {success_count} comments by {admin_username}")
        return success_count
    
    def bulk_remove_comments(self, comment_ids: List[int], admin_username: str) -> int:
        """
        Remove multiple comments at once.
        
        Args:
            comment_ids: List of comment IDs to remove
            admin_username: Username of administrator
            
        Returns:
            int: Number of comments successfully removed
        """
        success_count = 0
        for comment_id in comment_ids:
            if self.comment_mod_system.remove_comment(comment_id, admin_username):
                success_count += 1
        
        self.logger.info(f"Bulk removed {success_count} comments by {admin_username}")
        return success_count
    
    def bulk_approve_articles(self, article_ids: List[int], admin_username: str) -> int:
        """
        Approve and publish multiple articles at once.
        
        Args:
            article_ids: List of article IDs to approve
            admin_username: Username of administrator
            
        Returns:
            int: Number of articles successfully approved
        """
        success_count = 0
        for article_id in article_ids:
            if self.article_review_system.approve_article(article_id, admin_username):
                success_count += 1
        
        self.logger.info(f"Bulk approved {success_count} articles by {admin_username}")
        return success_count
    
    def bulk_reject_articles(self, article_ids: List[int], admin_username: str, reason: str) -> int:
        """
        Reject multiple articles at once.
        
        Args:
            article_ids: List of article IDs to reject
            admin_username: Username of administrator
            reason: Rejection reason
            
        Returns:
            int: Number of articles successfully rejected
        """
        success_count = 0
        for article_id in article_ids:
            if self.article_review_system.reject_article(article_id, admin_username, reason):
                success_count += 1
        
        self.logger.info(f"Bulk rejected {success_count} articles by {admin_username}")
        return success_count


def get_unified_moderation_dashboard(db_manager: DatabaseManager,
                                     auth_manager: AuthManager,
                                     comment_mod_system: CommentModerationSystem,
                                     article_review_system: ArticleReviewSystem) -> UnifiedModerationDashboard:
    """
    Get unified moderation dashboard instance.
    
    Args:
        db_manager: Database manager instance
        auth_manager: Authentication manager instance
        comment_mod_system: Comment moderation system instance
        article_review_system: Article review system instance
        
    Returns:
        UnifiedModerationDashboard: Dashboard instance
    """
    return UnifiedModerationDashboard(
        db_manager,
        auth_manager,
        comment_mod_system,
        article_review_system
    )
