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
from datetime import datetime, timezone
import hashlib
import html
import re
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
        
        # Rate limiting: max comments per hour
        self.rate_limit_per_hour = 10
        
        # Pagination: comments per page
        self.comments_per_page = 20
    
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
                # Check rate limit
                if not self.check_rate_limit(username):
                    st.warning(f"⚠️ You've reached the maximum of {self.rate_limit_per_hour} comments per hour. Please try again later.")
                else:
                    self._display_comment_input(target_type, target_id, username)
            else:
                st.info(t('login_to_comment'))
            
            # Display existing comments with pagination and sorting
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
                        # Clear reply state if this was a reply
                        if parent_id:
                            st.session_state[f'replying_to_{parent_id}'] = False
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
        Display all comments for content with threading, pagination, and sorting.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            current_username: Current user's username for interaction features
        """
        try:
            # Sorting options for users
            col1, col2 = st.columns([3, 1])
            with col1:
                sort_option = st.selectbox(
                    "Sort by:",
                    ["Newest First", "Oldest First", "Most Liked"],
                    key=f"sort_{target_type}_{target_id}",
                    label_visibility="collapsed"
                )
            
            # Map display option to sort parameter
            sort_map = {
                "Newest First": "newest",
                "Oldest First": "oldest",
                "Most Liked": "most_liked"
            }
            
            # Get paginated comments
            page_key = f"comments_page_{target_type}_{target_id}"
            page = st.session_state.get(page_key, 0)
            
            comments = self.get_comments_paginated(
                target_type, 
                target_id, 
                page=page,
                per_page=self.comments_per_page,
                sort_by=sort_map[sort_option]
            )
            
            if comments.empty:
                st.info("No comments yet. Be the first to comment!")
                return
            
            # Display comments
            for _, comment in comments.iterrows():
                self._display_single_comment(
                    comment,
                    comments,
                    target_type,
                    target_id,
                    current_username,
                    indent_level=0
                )
            
            # Pagination controls
            total_comments = self.get_comment_count(target_type, target_id)
            total_pages = (total_comments + self.comments_per_page - 1) // self.comments_per_page
            
            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"**Page {page + 1} of {total_pages}**")
                    
                    nav_col1, nav_col2 = st.columns(2)
                    with nav_col1:
                        if page > 0:
                            if st.button("← Previous", key=f"prev_{target_type}_{target_id}"):
                                st.session_state[page_key] = page - 1
                                st.rerun()
                    with nav_col2:
                        if page < total_pages - 1:
                            if st.button("Next →", key=f"next_{target_type}_{target_id}"):
                                st.session_state[page_key] = page + 1
                                st.rerun()
            
        except Exception as e:
            self.logger.error(f"Error displaying comments: {e}")
            st.error("Unable to load comments.")
    
    def _display_single_comment(self, comment: pd.Series, all_comments: pd.DataFrame,
                                target_type: str, target_id: str,
                                current_username: Optional[str],
                                indent_level: int = 0) -> None:
        """
        Display a single comment with threading.
        
        Args:
            comment: Comment data
            all_comments: All comments for threading
            target_type: Type of content
            target_id: Content identifier
            current_username: Current user's username
            indent_level: Nesting level for replies
        """
        try:
            # Skip deleted comments
            if comment.get('deleted_at') is not None:
                return
            
            # Apply indentation for replies
            indent = "&nbsp;" * (indent_level * 4)
            
            with st.container():
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
                    
                    # Show edited indicator if applicable
                    if comment.get('edited_at'):
                        st.caption(f"Edited · {self._format_timestamp(comment['edited_at'])}")
                    
                    # Comment content (sanitized)
                    sanitized_content = self.sanitize_content(comment['content'])
                    st.markdown(sanitized_content)
                    
                    # Comment actions (like, reply, report, edit)
                    self._display_comment_actions(
                        comment,
                        target_type,
                        target_id,
                        current_username
                    )
                
                # Display replies recursively (limit to 3 levels)
                if indent_level < 3:
                    comment_id = int(comment['id'])
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
    
    def _display_comment_actions(self, comment: pd.Series,
                                 target_type: str, target_id: str,
                                 current_username: Optional[str]) -> None:
        """
        Display comment action buttons (like, reply, report, edit).
        
        Args:
            comment: Comment data
            target_type: Type of content
            target_id: Content identifier
            current_username: Current user's username
        """
        try:
            comment_id = int(comment['id'])
            comment_author = comment['username']
            likes = int(comment['likes'])
            
            # Check if current user has already liked
            has_liked = False
            if current_username:
                has_liked = self.has_user_liked(comment_id, current_username)
            
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 5])
            
            with col1:
                # Like button
                if current_username:
                    like_key = f"like_{comment_id}"
                    like_text = f"👍 {likes}" if not has_liked else f"✅ {likes}"
                    if st.button(like_text, key=like_key):
                        if has_liked:
                            self.unlike_comment(comment_id, current_username)
                        else:
                            self.like_comment(comment_id, current_username)
                        st.rerun()
                else:
                    st.caption(f"👍 {likes}")
            
            with col2:
                # Reply button
                if current_username:
                    reply_key = f"reply_{comment_id}"
                    if st.button("💬 Reply", key=reply_key):
                        # Toggle reply state
                        current_state = st.session_state.get(f'replying_to_{comment_id}', False)
                        st.session_state[f'replying_to_{comment_id}'] = not current_state
                        st.rerun()
            
            with col3:
                # Report button (can't report own comment)
                if current_username and current_username != comment_author:
                    report_key = f"report_{comment_id}"
                    if st.button("🚩 Report", key=report_key):
                        self.report_comment(comment_id, current_username)
                        st.success("Comment reported for moderation.")
                        st.rerun()
            
            with col4:
                # Edit button (only for comment author within 24 hours)
                if current_username and current_username == comment_author:
                    if self.can_edit_comment(comment['timestamp']):
                        edit_key = f"edit_{comment_id}"
                        if st.button("✏️ Edit", key=edit_key):
                            st.session_state[f'editing_{comment_id}'] = True
                            st.rerun()
            
            # Show reply input if user clicked reply
            if current_username and st.session_state.get(f'replying_to_{comment_id}', False):
                with st.container():
                    self._display_comment_input(target_type, target_id, current_username, comment_id)
                    # Cancel reply button
                    if st.button("Cancel Reply", key=f"cancel_reply_{comment_id}"):
                        st.session_state[f'replying_to_{comment_id}'] = False
                        st.rerun()
            
            # Show edit input if user clicked edit
            if current_username and st.session_state.get(f'editing_{comment_id}', False):
                with st.container():
                    new_content = st.text_area(
                        "Edit your comment:",
                        value=comment['content'],
                        key=f"edit_content_{comment_id}",
                        max_chars=2000
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save Changes", key=f"save_edit_{comment_id}"):
                            if new_content.strip():
                                if self.edit_comment_by_user(comment_id, new_content.strip(), current_username):
                                    st.success("Comment updated.")
                                    st.session_state[f'editing_{comment_id}'] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update comment.")
                            else:
                                st.warning("Comment cannot be empty.")
                    with col2:
                        if st.button("Cancel", key=f"cancel_edit_{comment_id}"):
                            st.session_state[f'editing_{comment_id}'] = False
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
            # Validate content - only reject None or zero-length strings
            if content is None or len(content) == 0:
                self.logger.warning("Attempted to add empty comment")
                return False
            
            # Check rate limit
            if not self.check_rate_limit(username):
                self.logger.warning(f"Rate limit exceeded for user {username}")
                return False
            
            # Convert parent_id to Python int if not None
            if parent_id is not None:
                parent_id = int(parent_id)
            
            # Determine approval status based on user role
            # Import here to avoid circular dependency
            from modules.auth import get_auth_manager
            auth_manager = get_auth_manager(db_manager=self.db_manager)
            user_role = auth_manager.get_user_role(username)
            
            # Students require approval, professors and admins are auto-approved
            is_approved = 1 if user_role in ['professor', 'admin'] else 0
            
            query = """
                INSERT INTO comments 
                (username, target_type, target_id, content, parent_id, is_approved)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            affected_rows = self.db_manager.execute_update(
                query,
                (username, target_type, target_id, content, parent_id, is_approved)
            )
            
            if affected_rows > 0:
                approval_status = "auto-approved" if is_approved else "pending approval"
                self.logger.info(f"Comment added by {username} on {target_type}:{target_id} ({approval_status})")
                
                # Get the new comment ID
                new_comment_id = self.db_manager._last_insert_id
                
                # Create notification for parent comment author if this is a reply
                if parent_id:
                    self._create_reply_notification(new_comment_id, parent_id, username)
                
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
                    WHERE target_type = ? AND target_id = ? AND is_approved = 1 AND deleted_at IS NULL
                    ORDER BY timestamp ASC
                """
            else:
                query = """
                    SELECT * FROM comments 
                    WHERE target_type = ? AND target_id = ? AND deleted_at IS NULL
                    ORDER BY timestamp ASC
                """
            
            return self.db_manager.execute_query(query, (target_type, target_id))
            
        except Exception as e:
            self.logger.error(f"Error getting comments: {e}")
            return pd.DataFrame()
    
    def get_comments_paginated(self, target_type: str, target_id: str,
                               page: int = 0, per_page: int = 20,
                               sort_by: str = "newest",
                               approved_only: bool = True) -> pd.DataFrame:
        """
        Get paginated comments with sorting.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            page: Page number (0-indexed)
            per_page: Comments per page
            sort_by: Sort order ("newest", "oldest", "most_liked")
            approved_only: Whether to return only approved comments
            
        Returns:
            pd.DataFrame: Paginated comments data
        """
        try:
            # Build ORDER BY clause
            order_clause = "timestamp DESC, id DESC"
            if sort_by == "oldest":
                order_clause = "timestamp ASC, id ASC"
            elif sort_by == "most_liked":
                order_clause = "likes DESC, timestamp DESC, id DESC"
            
            approval_filter = "AND is_approved = 1" if approved_only else ""
            query = f"""
                SELECT * FROM comments 
                WHERE target_type = ? AND target_id = ? {approval_filter} AND deleted_at IS NULL
                ORDER BY {order_clause}
                LIMIT ? OFFSET ?
            """
            
            offset = page * per_page
            return self.db_manager.execute_query(query, (target_type, target_id, per_page, offset))
            
        except Exception as e:
            self.logger.error(f"Error getting paginated comments: {e}")
            return pd.DataFrame()
    
    def get_comment_count(self, target_type: str, target_id: str) -> int:
        """
        Get total count of comments for content.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            
        Returns:
            int: Total comment count
        """
        try:
            query = """
                SELECT COUNT(*) as count FROM comments 
                WHERE target_type = ? AND target_id = ? AND is_approved = 1 AND deleted_at IS NULL
            """
            
            result = self.db_manager.execute_query(query, (target_type, target_id))
            return int(result.iloc[0]['count']) if not result.empty else 0
            
        except Exception as e:
            self.logger.error(f"Error getting comment count: {e}")
            return 0
    
    def like_comment(self, comment_id: int, username: str) -> bool:
        """
        Like a comment (with per-user tracking).
        
        Args:
            comment_id: Comment ID to like
            username: Username liking the comment
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            comment_id = int(comment_id)
            
            # Check if already liked
            if self.has_user_liked(comment_id, username):
                self.logger.info(f"User {username} already liked comment {comment_id}")
                return False
            
            # Add to comment_likes table
            query = """
                INSERT INTO comment_likes (comment_id, username)
                VALUES (?, ?)
            """
            
            self.db_manager.execute_update(query, (comment_id, username))
            
            # Increment like count
            query = """
                UPDATE comments 
                SET likes = likes + 1 
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, (comment_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Comment {comment_id} liked by {username}")
                
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
    
    def unlike_comment(self, comment_id: int, username: str) -> bool:
        """
        Remove a like from a comment.
        
        Args:
            comment_id: Comment ID to unlike
            username: Username unliking the comment
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            comment_id = int(comment_id)
            
            # Remove from comment_likes table
            query = """
                DELETE FROM comment_likes 
                WHERE comment_id = ? AND username = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, (comment_id, username))
            
            if affected_rows > 0:
                # Decrement like count
                query = """
                    UPDATE comments 
                    SET likes = MAX(0, likes - 1)
                    WHERE id = ?
                """
                
                self.db_manager.execute_update(query, (comment_id,))
                
                self.logger.info(f"Comment {comment_id} unliked by {username}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error unliking comment: {e}")
            return False
    
    def has_user_liked(self, comment_id: int, username: str) -> bool:
        """
        Check if user has liked a comment.
        
        Args:
            comment_id: Comment ID
            username: Username to check
            
        Returns:
            bool: True if user has liked, False otherwise
        """
        try:
            comment_id = int(comment_id)
            
            query = """
                SELECT COUNT(*) as count FROM comment_likes
                WHERE comment_id = ? AND username = ?
            """
            
            result = self.db_manager.execute_query(query, (comment_id, username))
            return bool(result.iloc[0]['count'] > 0) if not result.empty else False
            
        except Exception as e:
            self.logger.error(f"Error checking like status: {e}")
            return False
    
    def report_comment(self, comment_id: int, reporter_username: str,
                      reason: str = "User reported") -> bool:
        """
        Report a comment for moderation (with deduplication).
        
        Args:
            comment_id: Comment ID to report
            reporter_username: Username reporting the comment
            reason: Reason for reporting
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            comment_id = int(comment_id)
            
            # Check if already reported by this user
            query = """
                SELECT COUNT(*) as count FROM comment_reports
                WHERE comment_id = ? AND reporter_username = ?
            """
            
            result = self.db_manager.execute_query(query, (comment_id, reporter_username))
            if result.iloc[0]['count'] > 0:
                self.logger.info(f"User {reporter_username} already reported comment {comment_id}")
                return False
            
            # Add to comment_reports table
            query = """
                INSERT INTO comment_reports (comment_id, reporter_username, reason)
                VALUES (?, ?, ?)
            """
            
            self.db_manager.execute_update(query, (comment_id, reporter_username, reason))
            
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
            str: Avatar emoji
        """
        try:
            # Use SHA256 hash for consistent avatar generation
            hash_value = int(hashlib.sha256(username.encode()).hexdigest()[:8], 16)
            
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
    
    def sanitize_content(self, content: str) -> str:
        """
        Sanitize comment content to prevent XSS attacks.
        
        Args:
            content: Raw comment content
            
        Returns:
            str: Sanitized content safe for rendering
        """
        try:
            # Remove dangerous patterns BEFORE escaping (so regex can match actual quotes)
            sanitized = content
            # Remove script tags and event handlers
            sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
            sanitized = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
            
            # Then escape HTML entities
            sanitized = html.escape(sanitized, quote=True)
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"Error sanitizing content: {e}")
            return html.escape(content)

    def _format_timestamp(self, timestamp: str) -> str:
        """
        Format timestamp for display (timezone-aware).
        
        Args:
            timestamp: Timestamp string from database (UTC)
            
        Returns:
            str: Formatted timestamp
        """
        try:
            # Parse timestamp as UTC
            dt = datetime.fromisoformat(timestamp)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            # Convert to local time
            now = datetime.now(timezone.utc)
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
    
    def check_rate_limit(self, username: str) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            username: Username to check
            
        Returns:
            bool: True if within limit, False if exceeded
        """
        try:
            query = """
                SELECT COUNT(*) as count FROM comments
                WHERE username = ? AND timestamp >= datetime('now', '-1 hour')
            """
            
            result = self.db_manager.execute_query(query, (username,))
            count = int(result.iloc[0]['count']) if not result.empty else 0
            
            return count < self.rate_limit_per_hour
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error
    
    def can_edit_comment(self, timestamp: str) -> bool:
        """
        Check if comment can still be edited (within 24 hours).
        
        Args:
            timestamp: Comment timestamp
            
        Returns:
            bool: True if editable, False otherwise
        """
        try:
            dt = datetime.fromisoformat(timestamp)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            diff = now - dt
            
            # Allow editing within 24 hours
            return diff.total_seconds() < 86400  # 24 hours in seconds
            
        except Exception as e:
            self.logger.error(f"Error checking edit permission: {e}")
            return False
    
    def edit_comment_by_user(self, comment_id: int, new_content: str, username: str) -> bool:
        """
        Edit a comment (user self-edit within time limit).
        
        Args:
            comment_id: Comment ID to edit
            new_content: New comment content
            username: Username editing the comment
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if new_content is None or len(new_content) == 0:
                return False
            
            comment_id = int(comment_id)
            
            # Verify user owns the comment and is within time limit
            query = "SELECT username, timestamp FROM comments WHERE id = ?"
            result = self.db_manager.execute_query(query, (comment_id,))
            
            if result.empty:
                return False
            
            comment = result.iloc[0]
            if comment['username'] != username:
                return False
            
            if not self.can_edit_comment(comment['timestamp']):
                return False
            
            # Update comment
            query = """
                UPDATE comments 
                SET content = ?, edited_at = CURRENT_TIMESTAMP, edited_by = ?
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(
                query,
                (new_content, username, comment_id)
            )
            
            if affected_rows > 0:
                self.logger.info(f"Comment {comment_id} edited by {username}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error editing comment: {e}")
            return False
    
    def _create_reply_notification(self, comment_id: int, parent_comment_id: int, 
                                   replier_username: str) -> None:
        """
        Create notification for parent comment author when someone replies.
        
        Args:
            comment_id: New reply comment ID
            parent_comment_id: Parent comment ID
            replier_username: Username who posted the reply
        """
        try:
            # Get parent comment author
            query = "SELECT username FROM comments WHERE id = ?"
            result = self.db_manager.execute_query(query, (parent_comment_id,))
            
            if result.empty:
                return
            
            parent_author = result.iloc[0]['username']
            
            # Don't notify if replying to own comment
            if parent_author == replier_username:
                return
            
            # Create notification
            query = """
                INSERT INTO comment_notifications 
                (comment_id, parent_comment_id, target_username, notification_type)
                VALUES (?, ?, ?, 'reply')
            """
            
            self.db_manager.execute_update(
                query,
                (comment_id, parent_comment_id, parent_author)
            )
            
        except Exception as e:
            self.logger.error(f"Error creating reply notification: {e}")
    
    def get_user_notifications(self, username: str, unread_only: bool = True) -> pd.DataFrame:
        """
        Get notifications for a user.
        
        Args:
            username: Username to get notifications for
            unread_only: Whether to return only unread notifications
            
        Returns:
            pd.DataFrame: Notifications data
        """
        try:
            if unread_only:
                query = """
                    SELECT * FROM comment_notifications
                    WHERE target_username = ? AND is_read = 0
                    ORDER BY timestamp DESC
                """
            else:
                query = """
                    SELECT * FROM comment_notifications
                    WHERE target_username = ?
                    ORDER BY timestamp DESC
                """
            
            return self.db_manager.execute_query(query, (username,))
            
        except Exception as e:
            self.logger.error(f"Error getting notifications: {e}")
            return pd.DataFrame()
    
    def mark_notification_read(self, notification_id: int) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = "UPDATE comment_notifications SET is_read = 1 WHERE id = ?"
            affected_rows = self.db_manager.execute_update(query, (notification_id,))
            return affected_rows > 0
            
        except Exception as e:
            self.logger.error(f"Error marking notification read: {e}")
            return False
    
    def search_comments(self, query_text: str, target_type: Optional[str] = None,
                       username: Optional[str] = None) -> pd.DataFrame:
        """
        Search comments by content.
        
        Args:
            query_text: Search query
            target_type: Filter by content type (optional)
            username: Filter by username (optional)
            
        Returns:
            pd.DataFrame: Search results
        """
        try:
            query = """
                SELECT * FROM comments
                WHERE content LIKE ? AND is_approved = 1 AND deleted_at IS NULL
            """
            params = [f"%{query_text}%"]
            
            if target_type:
                query += " AND target_type = ?"
                params.append(target_type)
            
            if username:
                query += " AND username = ?"
                params.append(username)
            
            query += " ORDER BY timestamp DESC LIMIT 50"
            
            return self.db_manager.execute_query(query, tuple(params))
            
        except Exception as e:
            self.logger.error(f"Error searching comments: {e}")
            return pd.DataFrame()
    
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
            
            # Get unapproved comments
            unapproved_comments = self.get_unapproved_comments()
            
            # Display tabs
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
                    st.markdown(f"**Content Type:** {report['target_type']} - {report['target_id']}")
                    st.markdown(f"**Report Reason:** {report['reason']}")
                    
                    st.markdown("---")
                    st.markdown("**Comment Content:**")
                    
                    # Get the actual comment
                    comment = self.get_comment_by_id(int(report['comment_id']))
                    if comment is not None:
                        st.markdown(f"> {comment['content']}")
                        
                        # Moderation actions
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(
                                "✅ Approve & Keep",
                                key=f"approve_reported_{report['comment_id']}"
                            ):
                                if self.resolve_report(int(report['comment_id']), admin_username, 'approved'):
                                    st.success("Report resolved - comment kept.")
                                    st.rerun()
                        
                        with col2:
                            if st.button(
                                "❌ Remove Comment",
                                key=f"remove_reported_{report['comment_id']}"
                            ):
                                if self.soft_delete_comment(int(report['comment_id']), admin_username):
                                    self.resolve_report(int(report['comment_id']), admin_username, 'removed')
                                    st.success("Comment removed.")
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
                                        int(report['comment_id']),
                                        new_content,
                                        admin_username
                                    ):
                                        self.resolve_report(int(report['comment_id']), admin_username, 'edited')
                                        st.success("Comment updated.")
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
                        st.warning("Comment no longer exists.")
            
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
            
            st.markdown("### Pending Approval")
            
            for _, comment in unapproved_comments.iterrows():
                with st.expander(f"Comment by {comment['username']} - {comment['timestamp'][:10]}"):
                    st.markdown(f"**Content:** {comment['content']}")
                    st.markdown(f"**Target:** {comment['target_type']} - {comment['target_id']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Approve", key=f"approve_{comment['id']}"):
                            if self.approve_comment(int(comment['id']), admin_username):
                                st.success("Comment approved.")
                                st.rerun()
                    
                    with col2:
                        if st.button("❌ Reject", key=f"reject_{comment['id']}"):
                            if self.soft_delete_comment(int(comment['id']), admin_username):
                                st.success("Comment rejected.")
                                st.rerun()
            
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
            
            # Display comments
            for _, comment in all_comments.iterrows():
                with st.expander(
                    f"{comment['username']} on {comment['target_type']} - "
                    f"{comment['timestamp'][:10]}"
                ):
                    st.markdown(f"**Comment ID:** {comment['id']}")
                    st.markdown(f"**User:** {comment['username']}")
                    st.markdown(f"**Target:** {comment['target_type']} - {comment['target_id']}")
                    st.markdown(f"**Posted:** {comment['timestamp']}")
                    st.markdown(f"**Likes:** {comment['likes']}")
                    st.markdown(f"**Status:** {'Approved' if comment['is_approved'] else 'Pending'}")
                    
                    if comment.get('deleted_at'):
                        st.warning("⚠️ This comment has been deleted")
                    
                    st.markdown("---")
                    st.markdown(f"> {comment['content']}")
                    
                    # Management actions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_all_{comment['id']}"):
                            st.session_state[f'editing_all_{comment["id"]}'] = True
                            st.rerun()
                    
                    with col2:
                        if not comment.get('deleted_at'):
                            if st.button("🗑️ Delete", key=f"delete_all_{comment['id']}"):
                                if self.soft_delete_comment(int(comment['id']), admin_username):
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
                            if st.button("Save Changes", key=f"save_edit_all_{comment['id']}"):
                                if self.edit_comment(int(comment['id']), new_content, admin_username):
                                    st.success("Comment updated.")
                                    st.session_state[f'editing_all_{comment["id"]}'] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update comment.")
                        
                        with col2:
                            if st.button("Cancel", key=f"cancel_edit_all_{comment['id']}"):
                                st.session_state[f'editing_all_{comment["id"]}'] = False
                                st.rerun()
            
        except Exception as e:
            self.logger.error(f"Error displaying all comments management: {e}")
            st.error("Unable to display comments management.")
    
    def get_reported_comments(self) -> pd.DataFrame:
        """
        Get all pending reported comments.
        
        Returns:
            pd.DataFrame: Reported comments data
        """
        try:
            query = """
                SELECT 
                    cr.id as report_id,
                    cr.reporter_username,
                    cr.comment_id,
                    cr.reason,
                    cr.timestamp as report_timestamp,
                    c.username as comment_username,
                    c.target_type,
                    c.target_id,
                    c.timestamp as comment_timestamp
                FROM comment_reports cr
                JOIN comments c ON cr.comment_id = c.id
                WHERE cr.status = 'pending'
                ORDER BY cr.timestamp DESC
            """
            
            return self.db_manager.execute_query(query)
            
        except Exception as e:
            self.logger.error(f"Error getting reported comments: {e}")
            return pd.DataFrame()
    
    def resolve_report(self, comment_id: int, admin_username: str, 
                      resolution: str) -> bool:
        """
        Resolve a reported comment.
        
        Args:
            comment_id: Comment ID
            admin_username: Admin username
            resolution: Resolution type ('approved', 'removed', 'edited')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            comment_id = int(comment_id)
            
            query = """
                UPDATE comment_reports
                SET status = ?, resolved_at = CURRENT_TIMESTAMP, resolved_by = ?
                WHERE comment_id = ? AND status = 'pending'
            """
            
            affected_rows = self.db_manager.execute_update(
                query,
                (resolution, admin_username, comment_id)
            )
            
            if affected_rows > 0:
                self.logger.info(f"Report for comment {comment_id} resolved as {resolution} by {admin_username}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error resolving report: {e}")
            return False
    
    def get_unapproved_comments(self) -> pd.DataFrame:
        """
        Get all unapproved comments.
        
        Returns:
            pd.DataFrame: Unapproved comments data
        """
        try:
            query = """
                SELECT * FROM comments 
                WHERE is_approved = 0 AND deleted_at IS NULL
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
            sort_by: Sort order
            
        Returns:
            pd.DataFrame: Comments data
        """
        try:
            if target_type:
                query = "SELECT * FROM comments WHERE target_type = ?"
                params = (target_type,)
            else:
                query = "SELECT * FROM comments"
                params = ()
            
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
    
    def soft_delete_comment(self, comment_id: int, admin_username: str) -> bool:
        """
        Soft delete a comment (mark as deleted but keep in database).
        
        Args:
            comment_id: Comment ID to delete
            admin_username: Username of administrator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            comment_id = int(comment_id)
            
            query = """
                UPDATE comments 
                SET deleted_at = CURRENT_TIMESTAMP, content = '[Deleted by moderator]'
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, (comment_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Comment {comment_id} soft deleted by {admin_username}")
                self._log_moderation_action(
                    admin_username,
                    comment_id,
                    'comment_deleted',
                    f"Soft deleted comment {comment_id}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error soft deleting comment: {e}")
            return False
    
    def reject_comment(self, comment_id: int, admin_username: str) -> bool:
        """
        Reject a comment (alias for soft_delete_comment for backward compatibility).
        
        Args:
            comment_id: Comment ID to reject
            admin_username: Username of administrator
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.soft_delete_comment(comment_id, admin_username)
    
    def edit_comment(self, comment_id: int, new_content: str,
                    admin_username: str) -> bool:
        """
        Edit a comment's content (admin edit).
        
        Args:
            comment_id: Comment ID to edit
            new_content: New comment content
            admin_username: Username of administrator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if new_content is None or len(new_content) == 0:
                return False
            
            comment_id = int(comment_id)
            
            query = """
                UPDATE comments 
                SET content = ?, edited_at = CURRENT_TIMESTAMP, edited_by = ?
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(
                query,
                (new_content, admin_username, comment_id)
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
