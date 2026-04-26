"""
Comment System for 广告思想简史 Platform

This module provides comprehensive comment and discussion functionality
with threading, moderation, and user interaction features.
"""

import streamlit as st
import logging
from utils.logger import create_logger
from utils.i18n import t
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import hashlib
from modules.database import DatabaseManager


class CommentSystem:
    """
    Comprehensive comment system with threading, moderation, and interactions.
    
    Handles comment submission, display, threading, likes/dislikes, reporting,
    and moderation functionality for the platform.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize CommentSystem with database manager.
        
        Args:
            db_manager: Database manager instance for data persistence
        """
        self.db_manager = db_manager
        self.logger = create_logger('CommentSystem')
        
    
    def display_comments_section(self, target_type: str, target_id: str, 
                                 username: Optional[str] = None) -> None:
        """
        Display complete comments section with input and existing comments.
        
        Args:
            target_type: Type of content ('timeline', 'figures', 'campaigns', 'article')
            target_id: Unique identifier for the content
            username: Current user's username (from session state if None)
        """
        try:
            # Get username from session state if not provided
            if username is None:
                username = st.session_state.get('username')
            
            st.markdown("---")
            st.markdown(f"### 💬 {t('comments_title')}")

            # Show comment input if user is logged in
            if username:
                self._display_comment_input(target_type, target_id, username)
            else:
                st.info(t('login_to_comment'))
            
            # Display existing comments
            self._display_comments(target_type, target_id, username)
            
        except Exception as e:
            self.logger.error(f"Error displaying comments section: {e}")
            st.error("Unable to load comments. Please try refreshing the page.")
    
    def _display_comment_input(self, target_type: str, target_id: str, 
                               username: str, parent_id: Optional[int] = None) -> None:
        """
        Display comment input form.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            username: Username submitting comment
            parent_id: Parent comment ID for replies (None for top-level comments)
        """
        try:
            # Create unique key for this input
            input_key = f"comment_input_{target_type}_{target_id}"
            if parent_id:
                input_key += f"_reply_{parent_id}"
                st.markdown(f"**{t('reply_to_comment')}:**")
            else:
                st.markdown(f"**{t('add_comment')}:**")

            # Comment text area
            comment_text = st.text_area(
                t('your_comment'),
                key=input_key,
                max_chars=2000,
                height=100,
                label_visibility="collapsed"
            )
            
            # Submit button
            submit_key = f"submit_{input_key}"
            if st.button("Post Comment", key=submit_key, type="primary"):
                if comment_text.strip():
                    success = self.add_comment(
                        username=username,
                        target_type=target_type,
                        target_id=target_id,
                        content=comment_text.strip(),
                        parent_id=parent_id
                    )
                    
                    if success:
                        st.success("✅ Comment posted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to post comment. Please try again.")
                else:
                    st.warning("Please enter a comment before posting.")
            
        except Exception as e:
            self.logger.error(f"Error displaying comment input: {e}")
            st.error("Unable to display comment input.")
    
    def _display_comments(self, target_type: str, target_id: str, 
                         current_username: Optional[str] = None) -> None:
        """
        Display all comments for content with threading.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            current_username: Current user's username for interaction features
        """
        try:
            # Get all approved comments for this content
            comments = self.get_comments(target_type, target_id, approved_only=True)
            
            if comments.empty:
                st.info("No comments yet. Be the first to share your thoughts!")
                return
            
            # Display comment count
            st.markdown(f"**{len(comments)} Comment{'s' if len(comments) != 1 else ''}**")
            
            # Separate top-level comments and replies
            top_level_comments = comments[comments['parent_id'].isna()]
            
            # Display each top-level comment with its replies
            for _, comment in top_level_comments.iterrows():
                self._display_single_comment(
                    comment, 
                    comments, 
                    target_type, 
                    target_id, 
                    current_username
                )
            
        except Exception as e:
            self.logger.error(f"Error displaying comments: {e}")
            st.error("Unable to load comments.")
    
    def _display_single_comment(self, comment: pd.Series, all_comments: pd.DataFrame,
                                target_type: str, target_id: str,
                                current_username: Optional[str] = None,
                                indent_level: int = 0) -> None:
        """
        Display a single comment with its replies (recursive for threading).
        
        Args:
            comment: Comment data as pandas Series
            all_comments: All comments DataFrame for finding replies
            target_type: Type of content
            target_id: Content identifier
            current_username: Current user's username
            indent_level: Indentation level for nested replies
        """
        try:
            comment_id = comment['id']
            
            # Create container with indentation for replies
            if indent_level > 0:
                # Use columns for indentation
                col1, col2 = st.columns([indent_level * 0.5, 10 - indent_level * 0.5])
                with col2:
                    container = st.container()
            else:
                container = st.container()
            
            with container:
                # Comment header with avatar and username
                col1, col2 = st.columns([0.5, 9.5])
                
                with col1:
                    # Display user avatar
                    avatar = self.generate_user_avatar(comment['username'])
                    st.markdown(f"<div style='font-size: 2em;'>{avatar}</div>", 
                              unsafe_allow_html=True)
                
                with col2:
                    # Username and timestamp
                    timestamp = self._format_timestamp(comment['timestamp'])
                    st.markdown(f"**{comment['username']}** · {timestamp}")
                    
                    # Comment content
                    st.markdown(comment['content'])
                    
                    # Comment actions (like, reply, report)
                    self._display_comment_actions(
                        comment_id, 
                        comment['likes'],
                        target_type,
                        target_id,
                        current_username,
                        comment['username']
                    )
                
                # Display replies recursively
                if indent_level < 3:  # Limit nesting depth to 3 levels
                    replies = all_comments[all_comments['parent_id'] == comment_id]
                    for _, reply in replies.iterrows():
                        self._display_single_comment(
                            reply,
                            all_comments,
                            target_type,
                            target_id,
                            current_username,
                            indent_level + 1
                        )
                
                st.markdown("---")
            
        except Exception as e:
            self.logger.error(f"Error displaying single comment: {e}")
    
    def _display_comment_actions(self, comment_id: int, likes: int,
                                 target_type: str, target_id: str,
                                 current_username: Optional[str],
                                 comment_author: str) -> None:
        """
        Display comment action buttons (like, reply, report).
        
        Args:
            comment_id: Comment ID
            likes: Current like count
            target_type: Type of content
            target_id: Content identifier
            current_username: Current user's username
            comment_author: Username of comment author
        """
        try:
            col1, col2, col3, col4 = st.columns([1, 1, 1, 7])
            
            with col1:
                # Like button
                if current_username:
                    like_key = f"like_{comment_id}"
                    if st.button(f"👍 {likes}", key=like_key):
                        self.like_comment(comment_id, current_username)
                        st.rerun()
                else:
                    st.caption(f"👍 {likes}")
            
            with col2:
                # Reply button
                if current_username:
                    reply_key = f"reply_{comment_id}"
                    if st.button("💬 Reply", key=reply_key):
                        # Store reply state in session
                        st.session_state[f'replying_to_{comment_id}'] = True
                        st.rerun()
            
            with col3:
                # Report button
                if current_username and current_username != comment_author:
                    report_key = f"report_{comment_id}"
                    if st.button("🚩 Report", key=report_key):
                        self.report_comment(comment_id, current_username)
                        st.success("Comment reported for moderation.")
                        st.rerun()
            
            # Show reply input if user clicked reply
            if current_username and st.session_state.get(f'replying_to_{comment_id}', False):
                with st.container():
                    self._display_comment_input(target_type, target_id, current_username, comment_id)
                    # Clear reply state after displaying
                    if st.button("Cancel Reply", key=f"cancel_reply_{comment_id}"):
                        st.session_state[f'replying_to_{comment_id}'] = False
                        st.rerun()
            
        except Exception as e:
            self.logger.error(f"Error displaying comment actions: {e}")
    
    def add_comment(self, username: str, target_type: str, target_id: str,
                   content: str, parent_id: Optional[int] = None) -> bool:
        """
        Add a new comment to the database.
        
        Args:
            username: Username posting the comment
            target_type: Type of content
            target_id: Content identifier
            content: Comment text content
            parent_id: Parent comment ID for replies (None for top-level)
            
        Returns:
            bool: True if comment added successfully, False otherwise
        """
        try:
            # Convert parent_id to Python int if not None to avoid numpy.int64 issues
            if parent_id is not None:
                parent_id = int(parent_id)
            
            query = """
                INSERT INTO comments 
                (username, target_type, target_id, content, parent_id, is_approved)
                VALUES (?, ?, ?, ?, ?, 1)
            """
            
            affected_rows = self.db_manager.execute_update(
                query,
                (username, target_type, target_id, content, parent_id)
            )
            
            if affected_rows > 0:
                self.logger.info(f"Comment added by {username} on {target_type}:{target_id}")
                
                # Log user activity
                self._log_user_activity(
                    username, 
                    'comment_posted',
                    target_type,
                    target_id,
                    f"Posted comment: {content[:50]}..."
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error adding comment: {e}")
            return False
    
    def get_comments(self, target_type: str, target_id: str,
                    approved_only: bool = True) -> pd.DataFrame:
        """
        Get all comments for specific content.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            approved_only: Whether to return only approved comments
            
        Returns:
            pd.DataFrame: Comments data
        """
        try:
            if approved_only:
                query = """
                    SELECT * FROM comments 
                    WHERE target_type = ? AND target_id = ? AND is_approved = 1
                    ORDER BY timestamp ASC
                """
            else:
                query = """
                    SELECT * FROM comments 
                    WHERE target_type = ? AND target_id = ?
                    ORDER BY timestamp ASC
                """
            
            return self.db_manager.execute_query(query, (target_type, target_id))
            
        except Exception as e:
            self.logger.error(f"Error getting comments: {e}")
            return pd.DataFrame()
    
    def like_comment(self, comment_id: int, username: str) -> bool:
        """
        Increment like count for a comment.
        
        Args:
            comment_id: Comment ID to like
            username: Username liking the comment
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Python int to avoid numpy.int64 issues with SQLite
            comment_id = int(comment_id)
            
            query = """
                UPDATE comments 
                SET likes = likes + 1 
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, (comment_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Comment {comment_id} liked by {username}")
                
                # Log user activity
                self._log_user_activity(
                    username,
                    'comment_liked',
                    None,
                    str(comment_id),
                    f"Liked comment {comment_id}"
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error liking comment: {e}")
            return False
    
    def report_comment(self, comment_id: int, reporter_username: str,
                      reason: str = "User reported") -> bool:
        """
        Report a comment for moderation.
        
        Args:
            comment_id: Comment ID to report
            reporter_username: Username reporting the comment
            reason: Reason for reporting
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Log the report in user_activity table
            self._log_user_activity(
                reporter_username,
                'comment_reported',
                'comment',
                str(comment_id),
                f"Reported comment {comment_id}: {reason}"
            )
            
            self.logger.info(f"Comment {comment_id} reported by {reporter_username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error reporting comment: {e}")
            return False
    
    def generate_user_avatar(self, username: str) -> str:
        """
        Generate a simple user avatar based on username.
        
        Args:
            username: Username to generate avatar for
            
        Returns:
            str: Avatar emoji or initials
        """
        try:
            # Use hash of username to consistently generate same avatar
            hash_value = int(hashlib.md5(username.encode()).hexdigest(), 16)
            
            # List of avatar emojis
            avatars = [
                "👤", "👨", "👩", "🧑", "👨‍💼", "👩‍💼", "👨‍🎓", "👩‍🎓",
                "👨‍🏫", "👩‍🏫", "👨‍💻", "👩‍💻", "🧑‍💻", "🧑‍🎓"
            ]
            
            # Select avatar based on hash
            avatar_index = hash_value % len(avatars)
            return avatars[avatar_index]
            
        except Exception as e:
            self.logger.error(f"Error generating avatar: {e}")
            return "👤"
    
    def _format_timestamp(self, timestamp: str) -> str:
        """
        Format timestamp for display.
        
        Args:
            timestamp: Timestamp string from database
            
        Returns:
            str: Formatted timestamp
        """
        try:
            dt = datetime.fromisoformat(timestamp)
            now = datetime.now()
            diff = now - dt
            
            if diff.days == 0:
                if diff.seconds < 60:
                    return "just now"
                elif diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                else:
                    hours = diff.seconds // 3600
                    return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.days == 1:
                return "yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            else:
                return dt.strftime("%b %d, %Y")
                
        except Exception as e:
            self.logger.error(f"Error formatting timestamp: {e}")
            return str(timestamp)
    
    def _log_user_activity(self, username: str, action: str,
                          target_type: Optional[str], target_id: Optional[str],
                          details: str) -> None:
        """
        Log user activity to database.
        
        Args:
            username: Username performing action
            action: Action type
            target_type: Type of target content
            target_id: Target content identifier
            details: Additional details
        """
        try:
            query = """
                INSERT INTO user_activity 
                (username, action, target_type, target_id, details)
                VALUES (?, ?, ?, ?, ?)
            """
            
            self.db_manager.execute_update(
                query,
                (username, action, target_type, target_id, details)
            )
            
        except Exception as e:
            self.logger.error(f"Error logging user activity: {e}")


# Global comment system instance
_comment_system = None

def get_comment_system(db_manager: DatabaseManager) -> CommentSystem:
    """
    Get singleton comment system instance.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        CommentSystem: Singleton comment system instance
    """
    global _comment_system
    if _comment_system is None:
        _comment_system = CommentSystem(db_manager)
    return _comment_system



class CommentModerationSystem:
    """
    Comment moderation system for administrators.
    
    Provides moderation queue, approval/rejection, editing, and removal
    functionality for managing user-generated comments.
    """
    
    def __init__(self, comment_system: CommentSystem):
        """
        Initialize moderation system with comment system.
        
        Args:
            comment_system: CommentSystem instance
        """
        self.comment_system = comment_system
        self.db_manager = comment_system.db_manager
        self.logger = comment_system.logger
    
    def display_moderation_queue(self, admin_username: str) -> None:
        """
        Display moderation queue for administrators.
        
        Args:
            admin_username: Username of administrator
        """
        try:
            st.markdown("## 🛡️ Comment Moderation Queue")
            
            # Get reported comments
            reported_comments = self.get_reported_comments()
            
            # Get unapproved comments (if any)
            unapproved_comments = self.get_unapproved_comments()
            
            # Display tabs for different moderation views
            tab1, tab2, tab3 = st.tabs([
                f"Reported ({len(reported_comments)})",
                f"Pending Approval ({len(unapproved_comments)})",
                "All Comments"
            ])
            
            with tab1:
                self._display_reported_comments(reported_comments, admin_username)
            
            with tab2:
                self._display_unapproved_comments(unapproved_comments, admin_username)
            
            with tab3:
                self._display_all_comments_management(admin_username)
            
        except Exception as e:
            self.logger.error(f"Error displaying moderation queue: {e}")
            st.error("Unable to load moderation queue.")
    
    def _display_reported_comments(self, reported_comments: pd.DataFrame,
                                   admin_username: str) -> None:
        """
        Display reported comments for moderation.
        
        Args:
            reported_comments: DataFrame of reported comments
            admin_username: Username of administrator
        """
        try:
            if reported_comments.empty:
                st.success("✅ No reported comments to review!")
                return
            
            st.markdown("### Reported Comments")
            st.info(f"Found {len(reported_comments)} reported comment(s) requiring review.")
            
            for _, report in reported_comments.iterrows():
                with st.expander(
                    f"Comment by {report['comment_username']} - "
                    f"Reported by {report['reporter_username']}"
                ):
                    # Display comment details
                    st.markdown(f"**Comment ID:** {report['comment_id']}")
                    st.markdown(f"**Posted:** {report['comment_timestamp']}")
                    st.markdown(f"**Content:** {report['target_type']} - {report['target_id']}")
                    st.markdown(f"**Report Reason:** {report['details']}")
                    
                    st.markdown("---")
                    st.markdown("**Comment Content:**")
                    
                    # Get the actual comment
                    comment = self.get_comment_by_id(report['comment_id'])
                    if comment is not None:
                        st.markdown(f"> {comment['content']}")
                        
                        # Moderation actions
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(
                                "✅ Approve & Keep",
                                key=f"approve_reported_{report['comment_id']}"
                            ):
                                # Just mark as reviewed (already approved)
                                st.success("Comment approved and kept.")
                                self._log_moderation_action(
                                    admin_username,
                                    report['comment_id'],
                                    'approved_reported',
                                    'Comment reviewed and approved'
                                )
                                st.rerun()
                        
                        with col2:
                            if st.button(
                                "❌ Remove Comment",
                                key=f"remove_reported_{report['comment_id']}"
                            ):
                                if self.remove_comment(report['comment_id'], admin_username):
                                    st.success("Comment removed successfully.")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove comment.")
                        
                        with col3:
                            if st.button(
                                "✏️ Edit Comment",
                                key=f"edit_reported_{report['comment_id']}"
                            ):
                                st.session_state[f'editing_{report["comment_id"]}'] = True
                                st.rerun()
                        
                        # Show edit interface if editing
                        if st.session_state.get(f'editing_{report["comment_id"]}', False):
                            new_content = st.text_area(
                                "Edit comment content:",
                                value=comment['content'],
                                key=f"edit_content_{report['comment_id']}"
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(
                                    "Save Changes",
                                    key=f"save_edit_{report['comment_id']}"
                                ):
                                    if self.edit_comment(
                                        report['comment_id'],
                                        new_content,
                                        admin_username
                                    ):
                                        st.success("Comment updated successfully.")
                                        st.session_state[f'editing_{report["comment_id"]}'] = False
                                        st.rerun()
                                    else:
                                        st.error("Failed to update comment.")
                            
                            with col2:
                                if st.button(
                                    "Cancel",
                                    key=f"cancel_edit_{report['comment_id']}"
                                ):
                                    st.session_state[f'editing_{report["comment_id"]}'] = False
                                    st.rerun()
                    else:
                        st.warning("Comment not found or already removed.")
            
        except Exception as e:
            self.logger.error(f"Error displaying reported comments: {e}")
            st.error("Unable to display reported comments.")
    
    def _display_unapproved_comments(self, unapproved_comments: pd.DataFrame,
                                    admin_username: str) -> None:
        """
        Display unapproved comments for moderation.
        
        Args:
            unapproved_comments: DataFrame of unapproved comments
            admin_username: Username of administrator
        """
        try:
            if unapproved_comments.empty:
                st.success("✅ No comments pending approval!")
                return
            
            st.markdown("### Comments Pending Approval")
            
            for _, comment in unapproved_comments.iterrows():
                with st.expander(
                    f"Comment by {comment['username']} - {comment['timestamp']}"
                ):
                    st.markdown(f"**Comment ID:** {comment['id']}")
                    st.markdown(f"**Content:** {comment['target_type']} - {comment['target_id']}")
                    st.markdown(f"**Posted:** {comment['timestamp']}")
                    
                    st.markdown("---")
                    st.markdown("**Comment Content:**")
                    st.markdown(f"> {comment['content']}")
                    
                    # Moderation actions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(
                            "✅ Approve",
                            key=f"approve_{comment['id']}"
                        ):
                            if self.approve_comment(comment['id'], admin_username):
                                st.success("Comment approved!")
                                st.rerun()
                            else:
                                st.error("Failed to approve comment.")
                    
                    with col2:
                        if st.button(
                            "❌ Reject",
                            key=f"reject_{comment['id']}"
                        ):
                            if self.reject_comment(comment['id'], admin_username):
                                st.success("Comment rejected and removed.")
                                st.rerun()
                            else:
                                st.error("Failed to reject comment.")
            
        except Exception as e:
            self.logger.error(f"Error displaying unapproved comments: {e}")
            st.error("Unable to display unapproved comments.")
    
    def _display_all_comments_management(self, admin_username: str) -> None:
        """
        Display all comments with management options.
        
        Args:
            admin_username: Username of administrator
        """
        try:
            st.markdown("### All Comments Management")
            
            # Filters
            col1, col2 = st.columns(2)
            
            with col1:
                target_type_filter = st.selectbox(
                    "Filter by content type:",
                    ["All", "timeline", "figures", "campaigns", "article"],
                    key="mod_target_type_filter"
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Sort by:",
                    ["Newest First", "Oldest First", "Most Likes"],
                    key="mod_sort_by"
                )
            
            # Get all comments
            all_comments = self.get_all_comments(
                target_type=None if target_type_filter == "All" else target_type_filter,
                sort_by=sort_by
            )
            
            if all_comments.empty:
                st.info("No comments found.")
                return
            
            st.markdown(f"**Total Comments:** {len(all_comments)}")
            
            # Display comments with management options
            for _, comment in all_comments.iterrows():
                with st.expander(
                    f"{comment['username']} on {comment['target_type']} - "
                    f"{comment['timestamp'][:10]}"
                ):
                    st.markdown(f"**Comment ID:** {comment['id']}")
                    st.markdown(f"**User:** {comment['username']}")
                    st.markdown(f"**Content:** {comment['target_type']} - {comment['target_id']}")
                    st.markdown(f"**Posted:** {comment['timestamp']}")
                    st.markdown(f"**Likes:** {comment['likes']}")
                    st.markdown(f"**Status:** {'Approved' if comment['is_approved'] else 'Pending'}")
                    
                    st.markdown("---")
                    st.markdown(f"> {comment['content']}")
                    
                    # Management actions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(
                            "✏️ Edit",
                            key=f"edit_all_{comment['id']}"
                        ):
                            st.session_state[f'editing_all_{comment["id"]}'] = True
                            st.rerun()
                    
                    with col2:
                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_all_{comment['id']}"
                        ):
                            if self.remove_comment(comment['id'], admin_username):
                                st.success("Comment deleted.")
                                st.rerun()
                            else:
                                st.error("Failed to delete comment.")
                    
                    # Show edit interface if editing
                    if st.session_state.get(f'editing_all_{comment["id"]}', False):
                        new_content = st.text_area(
                            "Edit comment content:",
                            value=comment['content'],
                            key=f"edit_content_all_{comment['id']}"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(
                                "Save Changes",
                                key=f"save_edit_all_{comment['id']}"
                            ):
                                if self.edit_comment(
                                    comment['id'],
                                    new_content,
                                    admin_username
                                ):
                                    st.success("Comment updated.")
                                    st.session_state[f'editing_all_{comment["id"]}'] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update comment.")
                        
                        with col2:
                            if st.button(
                                "Cancel",
                                key=f"cancel_edit_all_{comment['id']}"
                            ):
                                st.session_state[f'editing_all_{comment["id"]}'] = False
                                st.rerun()
            
        except Exception as e:
            self.logger.error(f"Error displaying all comments management: {e}")
            st.error("Unable to display comments management.")
    
    def get_reported_comments(self) -> pd.DataFrame:
        """
        Get all reported comments from user activity log.
        
        Returns:
            pd.DataFrame: Reported comments data
        """
        try:
            query = """
                SELECT 
                    ua.id as report_id,
                    ua.username as reporter_username,
                    ua.target_id as comment_id,
                    ua.details,
                    ua.timestamp as report_timestamp,
                    c.username as comment_username,
                    c.target_type,
                    c.target_id,
                    c.timestamp as comment_timestamp
                FROM user_activity ua
                JOIN comments c ON ua.target_id = CAST(c.id AS TEXT)
                WHERE ua.action = 'comment_reported'
                AND c.is_approved = 1
                ORDER BY ua.timestamp DESC
            """
            
            return self.db_manager.execute_query(query)
            
        except Exception as e:
            self.logger.error(f"Error getting reported comments: {e}")
            return pd.DataFrame()
    
    def get_unapproved_comments(self) -> pd.DataFrame:
        """
        Get all unapproved comments.
        
        Returns:
            pd.DataFrame: Unapproved comments data
        """
        try:
            query = """
                SELECT * FROM comments 
                WHERE is_approved = 0
                ORDER BY timestamp DESC
            """
            
            return self.db_manager.execute_query(query)
            
        except Exception as e:
            self.logger.error(f"Error getting unapproved comments: {e}")
            return pd.DataFrame()
    
    def get_all_comments(self, target_type: Optional[str] = None,
                        sort_by: str = "Newest First") -> pd.DataFrame:
        """
        Get all comments with optional filtering and sorting.
        
        Args:
            target_type: Filter by content type (None for all)
            sort_by: Sort order ("Newest First", "Oldest First", "Most Likes")
            
        Returns:
            pd.DataFrame: Comments data
        """
        try:
            # Build query based on filters
            if target_type:
                query = "SELECT * FROM comments WHERE target_type = ?"
                params = (target_type,)
            else:
                query = "SELECT * FROM comments"
                params = ()
            
            # Add sorting
            if sort_by == "Newest First":
                query += " ORDER BY timestamp DESC"
            elif sort_by == "Oldest First":
                query += " ORDER BY timestamp ASC"
            elif sort_by == "Most Likes":
                query += " ORDER BY likes DESC, timestamp DESC"
            
            return self.db_manager.execute_query(query, params)
            
        except Exception as e:
            self.logger.error(f"Error getting all comments: {e}")
            return pd.DataFrame()
    
    def get_comment_by_id(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific comment by ID.
        
        Args:
            comment_id: Comment ID
            
        Returns:
            Optional[Dict[str, Any]]: Comment data or None if not found
        """
        try:
            query = "SELECT * FROM comments WHERE id = ?"
            result = self.db_manager.execute_query(query, (comment_id,))
            
            if not result.empty:
                return result.iloc[0].to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting comment by ID: {e}")
            return None
    
    def approve_comment(self, comment_id: int, admin_username: str) -> bool:
        """
        Approve a comment for display.
        
        Args:
            comment_id: Comment ID to approve
            admin_username: Username of administrator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure comment_id is Python int
            comment_id = int(comment_id)
            
            query = "UPDATE comments SET is_approved = 1 WHERE id = ?"
            affected_rows = self.db_manager.execute_update(query, (comment_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Comment {comment_id} approved by {admin_username}")
                self._log_moderation_action(
                    admin_username,
                    comment_id,
                    'comment_approved',
                    f"Approved comment {comment_id}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error approving comment: {e}")
            return False
    
    def reject_comment(self, comment_id: int, admin_username: str) -> bool:
        """
        Reject and remove a comment.
        
        Args:
            comment_id: Comment ID to reject
            admin_username: Username of administrator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure comment_id is Python int
            comment_id = int(comment_id)
            
            query = "DELETE FROM comments WHERE id = ?"
            affected_rows = self.db_manager.execute_update(query, (comment_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Comment {comment_id} rejected by {admin_username}")
                self._log_moderation_action(
                    admin_username,
                    comment_id,
                    'comment_rejected',
                    f"Rejected and removed comment {comment_id}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error rejecting comment: {e}")
            return False
    
    def remove_comment(self, comment_id: int, admin_username: str) -> bool:
        """
        Remove a comment from the system.
        
        Args:
            comment_id: Comment ID to remove
            admin_username: Username of administrator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = "DELETE FROM comments WHERE id = ?"
            affected_rows = self.db_manager.execute_update(query, (comment_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Comment {comment_id} removed by {admin_username}")
                self._log_moderation_action(
                    admin_username,
                    comment_id,
                    'comment_removed',
                    f"Removed comment {comment_id}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing comment: {e}")
            return False
    
    def edit_comment(self, comment_id: int, new_content: str,
                    admin_username: str) -> bool:
        """
        Edit a comment's content.
        
        Args:
            comment_id: Comment ID to edit
            new_content: New comment content
            admin_username: Username of administrator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure comment_id is Python int
            comment_id = int(comment_id)
            
            query = "UPDATE comments SET content = ? WHERE id = ?"
            affected_rows = self.db_manager.execute_update(
                query,
                (new_content, comment_id)
            )
            
            if affected_rows > 0:
                self.logger.info(f"Comment {comment_id} edited by {admin_username}")
                self._log_moderation_action(
                    admin_username,
                    comment_id,
                    'comment_edited',
                    f"Edited comment {comment_id}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error editing comment: {e}")
            return False
    
    def _log_moderation_action(self, admin_username: str, comment_id: int,
                               action: str, details: str) -> None:
        """
        Log moderation action to database.
        
        Args:
            admin_username: Username of administrator
            comment_id: Comment ID being moderated
            action: Action type
            details: Additional details
        """
        try:
            query = """
                INSERT INTO user_activity 
                (username, action, target_type, target_id, details)
                VALUES (?, ?, 'comment', ?, ?)
            """
            
            self.db_manager.execute_update(
                query,
                (admin_username, action, str(comment_id), details)
            )
            
        except Exception as e:
            self.logger.error(f"Error logging moderation action: {e}")


def get_comment_moderation_system(comment_system: CommentSystem) -> CommentModerationSystem:
    """
    Get comment moderation system instance.
    
    Args:
        comment_system: CommentSystem instance
        
    Returns:
        CommentModerationSystem: Moderation system instance
    """
    return CommentModerationSystem(comment_system)
