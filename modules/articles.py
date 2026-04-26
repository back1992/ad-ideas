"""
Article Management System for 广告思想简史 Platform

This module provides comprehensive article creation, management, and publication
functionality for professors and administrators.
"""

import streamlit as st
import logging
from utils.logger import create_logger
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime
from modules.database import DatabaseManager
from modules.auth import AuthManager
from utils.i18n import t


class ArticleManager:
    """
    Comprehensive article management system with workflow support.
    
    Handles article creation, editing, status management, categorization,
    and publication workflow for the platform.
    """
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        """
        Initialize ArticleManager with database and auth managers.
        
        Args:
            db_manager: Database manager instance for data persistence
            auth_manager: Authentication manager for permission checks
        """
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.logger = create_logger('ArticleManager')
        
    
    def show_article_editor(self, username: str, article_id: Optional[int] = None) -> None:
        """
        Display article editor interface for creating or editing articles.
        
        Args:
            username: Username of the author
            article_id: Article ID for editing (None for new article)
        """
        try:
            # Check permissions
            if not self.auth_manager.is_professor_or_admin(username):
                st.error("Access denied. Only professors and administrators can create articles.")
                return
            
            st.markdown("## 📝 Article Editor")
            
            # Load existing article if editing
            existing_article = None
            if article_id:
                existing_article = self.get_article_by_id(article_id)
                if not existing_article:
                    st.error("Article not found.")
                    return
                
                # Check if user is the author or admin
                if existing_article['author'] != username and not self.auth_manager.is_admin(username):
                    st.error("You can only edit your own articles.")
                    return
            
            # Article form
            with st.form("article_editor_form"):
                # Title
                title = st.text_input(
                    "Article Title",
                    value=existing_article['title'] if existing_article else "",
                    max_chars=200,
                    help="Enter a descriptive title for your article"
                )
                
                # Content (Markdown editor)
                st.markdown("**Article Content** (Markdown supported)")
                content = st.text_area(
                    "Content",
                    value=existing_article['content'] if existing_article else "",
                    height=400,
                    help="Write your article content using Markdown formatting",
                    label_visibility="collapsed"
                )
                
                # Excerpt
                excerpt = st.text_area(
                    t('excerpt_label'),
                    value=existing_article['excerpt'] if existing_article else "",
                    max_chars=500,
                    height=100,
                    help=t('excerpt_help')
                )
                
                # Category and Tags
                col1, col2 = st.columns(2)
                
                with col1:
                    category = st.selectbox(
                        "Category",
                        options=[
                            "Advertising History",
                            "Marketing Theory",
                            "Case Studies",
                            "Industry Analysis",
                            "Creative Strategies",
                            "Digital Marketing",
                            "Other"
                        ],
                        index=self._get_category_index(existing_article['category']) if existing_article else 0
                    )
                
                with col2:
                    tags_input = st.text_input(
                        "Tags (comma-separated)",
                        value=existing_article['tags'] if existing_article else "",
                        help="Enter tags separated by commas (e.g., branding, social media, creativity)"
                    )
                
                # Status selection
                current_status = existing_article['status'] if existing_article else 'draft'
                
                st.markdown("**Article Status**")
                status_options = ['draft', 'review', 'published']
                if self.auth_manager.is_admin(username):
                    status_options.append('archived')
                
                status = st.radio(
                    "Status",
                    options=status_options,
                    index=status_options.index(current_status) if current_status in status_options else 0,
                    horizontal=True,
                    help="Draft: Work in progress | Review: Submit for approval | Published: Make public",
                    label_visibility="collapsed"
                )
                
                # Submit buttons
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    submit_save = st.form_submit_button("💾 Save", type="primary")
                
                with col2:
                    submit_preview = st.form_submit_button("👁️ Preview")
                
                if submit_save:
                    if not title.strip():
                        st.error("Please enter a title for your article.")
                    elif not content.strip():
                        st.error("Please enter content for your article.")
                    else:
                        # Auto-generate excerpt if empty
                        if not excerpt.strip():
                            excerpt = self._generate_excerpt(content)
                        
                        # Save article
                        success = self.save_article(
                            article_id=article_id,
                            title=title.strip(),
                            content=content.strip(),
                            excerpt=excerpt.strip(),
                            category=category,
                            tags=tags_input.strip(),
                            author=username,
                            status=status
                        )
                        
                        if success:
                            st.success("✅ Article saved successfully!")
                            if status == 'review':
                                st.info("📬 Article submitted for review. An administrator will review it soon.")
                            elif status == 'published':
                                st.success("🎉 Article published! It's now visible to all users.")
                            
                            # Log activity
                            self._log_article_activity(
                                username,
                                'article_saved' if article_id else 'article_created',
                                article_id,
                                f"{'Updated' if article_id else 'Created'} article: {title[:50]}"
                            )
                        else:
                            st.error("Failed to save article. Please try again.")
                
                if submit_preview:
                    if title.strip() and content.strip():
                        st.markdown("---")
                        st.markdown("### 👁️ Preview")
                        st.markdown(f"# {title}")
                        st.markdown(f"*By {username} | Category: {category}*")
                        if tags_input.strip():
                            st.markdown(f"**Tags:** {tags_input}")
                        st.markdown("---")
                        st.markdown(content)
                    else:
                        st.warning("Please enter title and content to preview.")
            
        except Exception as e:
            self.logger.error(f"Error displaying article editor: {e}")
            st.error("Unable to display article editor.")
    
    def save_article(self, title: str, content: str, excerpt: str, category: str,
                    tags: str, author: str, status: str, article_id: Optional[int] = None) -> bool:
        """
        Save article to database (create or update).
        
        Args:
            title: Article title
            content: Article content (markdown)
            excerpt: Article excerpt/summary
            category: Article category
            tags: Comma-separated tags
            author: Author username
            status: Article status (draft, review, published, archived)
            article_id: Article ID for updates (None for new article)
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            if article_id:
                # Verify article exists before update
                existing_article = self.get_article_by_id(article_id)
                if not existing_article:
                    return False
                
                # Update existing article
                # Note: We set published_at when transitioning TO published status
                query = """
                    UPDATE articles 
                    SET title = ?, content = ?, excerpt = ?, category = ?, tags = ?,
                        status = ?, updated_at = CURRENT_TIMESTAMP,
                        published_at = CASE 
                                           WHEN ? = 'published' THEN COALESCE(published_at, CURRENT_TIMESTAMP)
                                           ELSE published_at 
                                       END
                    WHERE id = ?
                """
                affected_rows = self.db_manager.execute_update(
                    query,
                    (title, content, excerpt, category, tags, status, status, article_id)
                )
                
                # The UPDATE query always executes successfully even if no rows are affected
                # (e.g., when all values are identical). Since we verified the article exists,
                # and the query executed without exception, we can trust the update succeeded.
                self.logger.info(f"Article updated by {author}: {title}")
                return True
            else:
                # Create new article
                query = """
                    INSERT INTO articles 
                    (title, content, excerpt, category, tags, author, status, published_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 
                            CASE WHEN ? = 'published' THEN CURRENT_TIMESTAMP ELSE NULL END)
                """
                affected_rows = self.db_manager.execute_update(
                    query,
                    (title, content, excerpt, category, tags, author, status, status)
                )
                
                if affected_rows > 0:
                    self.logger.info(f"Article created by {author}: {title}")
                    return True
                
                return False
            
        except Exception as e:
            self.logger.error(f"Error saving article: {e}")
            return False
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Get article by ID.
        
        Args:
            article_id: Article ID
            
        Returns:
            Optional[Dict[str, Any]]: Article data or None if not found
        """
        try:
            # Convert to Python int to avoid numpy issues
            article_id = int(article_id)
            
            query = "SELECT * FROM articles WHERE id = ?"
            result = self.db_manager.execute_query(query, (article_id,))
            
            if not result.empty:
                return result.iloc[0].to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting article by ID: {e}")
            return None
    
    def get_articles(self, status: Optional[str] = None, author: Optional[str] = None,
                    category: Optional[str] = None, limit: int = 50) -> pd.DataFrame:
        """
        Get articles with optional filtering.
        
        Args:
            status: Filter by status (None for all)
            author: Filter by author (None for all)
            category: Filter by category (None for all)
            limit: Maximum number of articles to return
            
        Returns:
            pd.DataFrame: Articles data
        """
        try:
            # Build query with filters
            query = "SELECT * FROM articles WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if author:
                query += " AND author = ?"
                params.append(author)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)
            
            return self.db_manager.execute_query(query, tuple(params))
            
        except Exception as e:
            self.logger.error(f"Error getting articles: {e}")
            return pd.DataFrame()
    
    def show_article_list(self, username: str, status: Optional[str] = None,
                         author: Optional[str] = None) -> None:
        """
        Display list of articles with management options.
        
        Args:
            username: Current user's username
            status: Filter by status (None for all)
            author: Filter by author (None for all)
        """
        try:
            st.markdown("## 📚 Articles")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    options=["All", "draft", "review", "published", "archived"],
                    index=0
                )
                status = None if status_filter == "All" else status_filter
            
            with col2:
                if self.auth_manager.is_admin(username):
                    author_filter = st.selectbox(
                        "Filter by Author",
                        options=["All", "My Articles", "Others"],
                        index=0
                    )
                    if author_filter == "My Articles":
                        author = username
                    elif author_filter == "Others":
                        author = None  # Will need custom query
                    else:
                        author = None
                else:
                    author = username
                    st.info(f"Showing your articles")
            
            with col3:
                category_filter = st.selectbox(
                    "Filter by Category",
                    options=["All", "Advertising History", "Marketing Theory", "Case Studies",
                            "Industry Analysis", "Creative Strategies", "Digital Marketing", "Other"],
                    index=0
                )
                category = None if category_filter == "All" else category_filter
            
            # Get articles
            articles = self.get_articles(status=status, author=author, category=category)
            
            if articles.empty:
                st.info("No articles found. Create your first article!")
                return
            
            st.markdown(f"**Found {len(articles)} article(s)**")
            
            # Display articles
            for _, article in articles.iterrows():
                with st.expander(
                    f"📄 {article['title']} - {article['status'].upper()} - {article['updated_at'][:10]}"
                ):
                    # Article info
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Author:** {article['author']}")
                        st.markdown(f"**Category:** {article['category']}")
                        if article['tags']:
                            st.markdown(f"**Tags:** {article['tags']}")
                        st.markdown(f"**Created:** {article['created_at']}")
                        st.markdown(f"**Updated:** {article['updated_at']}")
                        if article['published_at']:
                            st.markdown(f"**Published:** {article['published_at']}")
                    
                    with col2:
                        st.metric("Views", article['views'])
                        st.metric("Rating", f"{article['avg_rating']:.1f}")
                        st.metric("Feedback", article['total_feedback'])
                    
                    # Excerpt
                    if article['excerpt']:
                        st.markdown("**Summary:**")
                        st.markdown(f"> {article['excerpt']}")
                    
                    # Actions
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("👁️ View", key=f"view_{article['id']}"):
                            self.show_article_detail(article['id'], username)
                    
                    with col2:
                        # Can edit if author or admin
                        if article['author'] == username or self.auth_manager.is_admin(username):
                            if st.button("✏️ Edit", key=f"edit_{article['id']}"):
                                st.session_state[f'editing_article_{article["id"]}'] = True
                                st.rerun()
                    
                    with col3:
                        # Can delete if author or admin
                        if article['author'] == username or self.auth_manager.is_admin(username):
                            if st.button("🗑️ Delete", key=f"delete_{article['id']}"):
                                if self.delete_article(article['id'], username):
                                    st.success("Article deleted.")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete article.")
            
        except Exception as e:
            self.logger.error(f"Error displaying article list: {e}")
            st.error("Unable to display articles.")
    
    def show_article_detail(self, article_id: int, username: Optional[str] = None) -> None:
        """
        Display full article detail view.
        
        Args:
            article_id: Article ID to display
            username: Current user's username (for tracking views)
        """
        try:
            article = self.get_article_by_id(article_id)
            
            if not article:
                st.error("Article not found.")
                return
            
            # Check if article is published or user has permission to view
            if article['status'] != 'published':
                if not username:
                    st.error("This article is not published yet.")
                    return
                
                # Check if user is author or admin
                if article['author'] != username and not self.auth_manager.is_admin(username):
                    st.error("This article is not published yet.")
                    return
            
            # Increment view count
            if username:
                self.increment_article_views(article_id)
            
            # Display article
            st.markdown(f"# {article['title']}")
            
            # Metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Author:** {article['author']}")
            with col2:
                st.markdown(f"**Category:** {article['category']}")
            with col3:
                st.markdown(f"**Published:** {article['published_at'] or 'Not published'}")
            
            if article['tags']:
                st.markdown(f"**Tags:** {article['tags']}")
            
            st.markdown("---")
            
            # Content
            st.markdown(article['content'])
            
            st.markdown("---")
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👁️ Views", article['views'])
            with col2:
                st.metric("⭐ Rating", f"{article['avg_rating']:.1f}")
            with col3:
                st.metric("💬 Feedback", article['total_feedback'])
            
        except Exception as e:
            self.logger.error(f"Error displaying article detail: {e}")
            st.error("Unable to display article.")
    
    def delete_article(self, article_id: int, username: str) -> bool:
        """
        Delete an article.
        
        Args:
            article_id: Article ID to delete
            username: Username requesting deletion
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            # Convert to Python int
            article_id = int(article_id)
            
            # Check permissions
            article = self.get_article_by_id(article_id)
            if not article:
                return False
            
            if article['author'] != username and not self.auth_manager.is_admin(username):
                self.logger.warning(f"User {username} attempted to delete article {article_id} without permission")
                return False
            
            query = "DELETE FROM articles WHERE id = ?"
            affected_rows = self.db_manager.execute_update(query, (article_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Article {article_id} deleted by {username}")
                self._log_article_activity(
                    username,
                    'article_deleted',
                    article_id,
                    f"Deleted article: {article['title']}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting article: {e}")
            return False
    
    def increment_article_views(self, article_id: int) -> bool:
        """
        Increment view count for an article.
        
        Args:
            article_id: Article ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Python int
            article_id = int(article_id)
            
            query = "UPDATE articles SET views = views + 1 WHERE id = ?"
            affected_rows = self.db_manager.execute_update(query, (article_id,))
            
            return affected_rows > 0
            
        except Exception as e:
            self.logger.error(f"Error incrementing article views: {e}")
            return False
    
    def _generate_excerpt(self, content: str, max_length: int = 200) -> str:
        """
        Auto-generate excerpt from content.
        
        Args:
            content: Article content
            max_length: Maximum excerpt length
            
        Returns:
            str: Generated excerpt
        """
        try:
            # Remove markdown formatting
            clean_content = content.replace('#', '').replace('*', '').replace('_', '')
            
            # Take first paragraph or max_length characters
            paragraphs = clean_content.split('\n\n')
            first_para = paragraphs[0].strip() if paragraphs else clean_content
            
            if len(first_para) <= max_length:
                return first_para
            
            # Truncate at word boundary
            excerpt = first_para[:max_length]
            last_space = excerpt.rfind(' ')
            if last_space > 0:
                excerpt = excerpt[:last_space]
            
            return excerpt + "..."
            
        except Exception as e:
            self.logger.error(f"Error generating excerpt: {e}")
            return content[:max_length] + "..."
    
    def _get_category_index(self, category: Optional[str]) -> int:
        """Get index of category in options list."""
        categories = [
            "Advertising History",
            "Marketing Theory",
            "Case Studies",
            "Industry Analysis",
            "Creative Strategies",
            "Digital Marketing",
            "Other"
        ]
        try:
            return categories.index(category) if category in categories else 0
        except:
            return 0
    
    def _log_article_activity(self, username: str, action: str,
                             article_id: Optional[int], details: str) -> None:
        """
        Log article activity to database.
        
        Args:
            username: Username performing action
            action: Action type
            article_id: Article ID
            details: Additional details
        """
        try:
            query = """
                INSERT INTO user_activity 
                (username, action, target_type, target_id, details)
                VALUES (?, ?, 'article', ?, ?)
            """
            
            self.db_manager.execute_update(
                query,
                (username, action, str(article_id) if article_id else None, details)
            )
            
        except Exception as e:
            self.logger.error(f"Error logging article activity: {e}")


# Global article manager instance
_article_manager = None

def get_article_manager(db_manager: DatabaseManager, auth_manager: AuthManager) -> ArticleManager:
    """
    Get singleton article manager instance.
    
    Args:
        db_manager: Database manager instance
        auth_manager: Authentication manager instance
        
    Returns:
        ArticleManager: Singleton article manager instance
    """
    global _article_manager
    if _article_manager is None:
        _article_manager = ArticleManager(db_manager, auth_manager)
    return _article_manager



class ArticleReviewSystem:
    """
    Article review and moderation system for administrators.
    
    Provides review queue, approval/rejection, and publication workflow
    management for articles submitted by professors.
    """
    
    def __init__(self, article_manager: ArticleManager):
        """
        Initialize review system with article manager.
        
        Args:
            article_manager: ArticleManager instance
        """
        self.article_manager = article_manager
        self.db_manager = article_manager.db_manager
        self.auth_manager = article_manager.auth_manager
        self.logger = article_manager.logger
    
    def show_review_queue(self, admin_username: str) -> None:
        """
        Display article review queue for administrators.
        
        Args:
            admin_username: Username of administrator
        """
        try:
            # Check admin permissions
            if not self.auth_manager.is_admin(admin_username):
                st.error("Access denied. Only administrators can access the review queue.")
                return
            
            st.markdown("## 📋 Article Review Queue")
            
            # Get articles pending review
            pending_articles = self.article_manager.get_articles(status='review')
            
            if pending_articles.empty:
                st.success("✅ No articles pending review!")
                return
            
            st.info(f"Found {len(pending_articles)} article(s) awaiting review")
            
            # Display each article
            for _, article in pending_articles.iterrows():
                with st.expander(
                    f"📄 {article['title']} by {article['author']} - Submitted {article['updated_at'][:10]}"
                ):
                    # Article metadata
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Author:** {article['author']}")
                        st.markdown(f"**Category:** {article['category']}")
                        if article['tags']:
                            st.markdown(f"**Tags:** {article['tags']}")
                    
                    with col2:
                        st.markdown(f"**Created:** {article['created_at']}")
                        st.markdown(f"**Submitted:** {article['updated_at']}")
                    
                    # Excerpt
                    if article['excerpt']:
                        st.markdown("**Summary:**")
                        st.markdown(f"> {article['excerpt']}")
                    
                    # Content preview
                    with st.expander("📖 View Full Content"):
                        st.markdown(article['content'])
                    
                    st.markdown("---")
                    
                    # Review actions
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Approve & Publish", key=f"approve_{article['id']}", type="primary"):
                            if self.approve_article(article['id'], admin_username):
                                st.success(f"Article '{article['title']}' approved and published!")
                                st.rerun()
                            else:
                                st.error("Failed to approve article.")
                    
                    with col2:
                        if st.button("❌ Reject", key=f"reject_{article['id']}"):
                            # Show rejection reason input
                            st.session_state[f'rejecting_{article["id"]}'] = True
                            st.rerun()
                    
                    with col3:
                        if st.button("✏️ Request Changes", key=f"changes_{article['id']}"):
                            # Show feedback input
                            st.session_state[f'requesting_changes_{article["id"]}'] = True
                            st.rerun()
                    
                    # Rejection reason form
                    if st.session_state.get(f'rejecting_{article["id"]}', False):
                        with st.form(f"reject_form_{article['id']}"):
                            st.markdown("**Rejection Reason:**")
                            reason = st.text_area(
                                "Explain why this article is being rejected",
                                key=f"reject_reason_{article['id']}",
                                height=100
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Confirm Rejection"):
                                    if reason.strip():
                                        if self.reject_article(article['id'], admin_username, reason):
                                            st.success("Article rejected.")
                                            st.session_state[f'rejecting_{article["id"]}'] = False
                                            st.rerun()
                                        else:
                                            st.error("Failed to reject article.")
                                    else:
                                        st.warning("Please provide a rejection reason.")
                            
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f'rejecting_{article["id"]}'] = False
                                    st.rerun()
                    
                    # Request changes form
                    if st.session_state.get(f'requesting_changes_{article["id"]}', False):
                        with st.form(f"changes_form_{article['id']}"):
                            st.markdown("**Requested Changes:**")
                            feedback = st.text_area(
                                "Provide feedback for the author",
                                key=f"changes_feedback_{article['id']}",
                                height=100
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Send Feedback"):
                                    if feedback.strip():
                                        if self.request_changes(article['id'], admin_username, feedback):
                                            st.success("Feedback sent to author.")
                                            st.session_state[f'requesting_changes_{article["id"]}'] = False
                                            st.rerun()
                                        else:
                                            st.error("Failed to send feedback.")
                                    else:
                                        st.warning("Please provide feedback.")
                            
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f'requesting_changes_{article["id"]}'] = False
                                    st.rerun()
            
        except Exception as e:
            self.logger.error(f"Error displaying review queue: {e}")
            st.error("Unable to display review queue.")
    
    def approve_article(self, article_id: int, admin_username: str) -> bool:
        """
        Approve article and publish it.
        
        Args:
            article_id: Article ID to approve
            admin_username: Username of administrator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Python int
            article_id = int(article_id)
            
            # Update article status to published
            query = """
                UPDATE articles 
                SET status = 'published', 
                    published_at = COALESCE(published_at, CURRENT_TIMESTAMP),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, (article_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Article {article_id} approved and published by {admin_username}")
                
                # Log activity
                article = self.article_manager.get_article_by_id(article_id)
                self.article_manager._log_article_activity(
                    admin_username,
                    'article_approved',
                    article_id,
                    f"Approved and published article: {article['title'] if article else article_id}"
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error approving article: {e}")
            return False
    
    def reject_article(self, article_id: int, admin_username: str, reason: str) -> bool:
        """
        Reject article and change status back to draft.
        
        Args:
            article_id: Article ID to reject
            admin_username: Username of administrator
            reason: Rejection reason
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Python int
            article_id = int(article_id)
            
            # Update article status to draft
            query = """
                UPDATE articles 
                SET status = 'draft', 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, (article_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Article {article_id} rejected by {admin_username}")
                
                # Log activity with reason
                article = self.article_manager.get_article_by_id(article_id)
                self.article_manager._log_article_activity(
                    admin_username,
                    'article_rejected',
                    article_id,
                    f"Rejected article: {article['title'] if article else article_id}. Reason: {reason}"
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error rejecting article: {e}")
            return False
    
    def request_changes(self, article_id: int, admin_username: str, feedback: str) -> bool:
        """
        Request changes to article and send feedback to author.
        
        Args:
            article_id: Article ID
            admin_username: Username of administrator
            feedback: Feedback for author
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Python int
            article_id = int(article_id)
            
            # Update article status to draft
            query = """
                UPDATE articles 
                SET status = 'draft', 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, (article_id,))
            
            if affected_rows > 0:
                self.logger.info(f"Changes requested for article {article_id} by {admin_username}")
                
                # Log activity with feedback
                article = self.article_manager.get_article_by_id(article_id)
                self.article_manager._log_article_activity(
                    admin_username,
                    'article_changes_requested',
                    article_id,
                    f"Requested changes for article: {article['title'] if article else article_id}. Feedback: {feedback}"
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error requesting changes: {e}")
            return False
    
    def show_published_articles(self, limit: int = 20) -> None:
        """
        Display published articles for public viewing.
        
        Args:
            limit: Maximum number of articles to display
        """
        try:
            st.markdown("## 📚 Published Articles")
            
            # Get published articles
            articles = self.article_manager.get_articles(status='published', limit=limit)
            
            if articles.empty:
                st.info("No published articles yet.")
                return
            
            # Display articles in a grid
            for _, article in articles.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### {article['title']}")
                        st.markdown(f"*By {article['author']} | {article['category']} | {article['published_at'][:10]}*")
                        
                        if article['excerpt']:
                            st.markdown(article['excerpt'])
                        
                        if article['tags']:
                            tags = article['tags'].split(',')
                            tag_html = ' '.join([f'<span style="background-color: #f0f0f0; padding: 2px 8px; border-radius: 3px; margin-right: 5px;">{tag.strip()}</span>' for tag in tags])
                            st.markdown(tag_html, unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("👁️", article['views'])
                        st.metric("⭐", f"{article['avg_rating']:.1f}")
                        
                        if st.button("Read More", key=f"read_{article['id']}"):
                            st.session_state[f'viewing_article_{article["id"]}'] = True
                            st.rerun()
                    
                    st.markdown("---")
            
        except Exception as e:
            self.logger.error(f"Error displaying published articles: {e}")
            st.error("Unable to display articles.")


def get_article_review_system(article_manager: ArticleManager) -> ArticleReviewSystem:
    """
    Get article review system instance.
    
    Args:
        article_manager: ArticleManager instance
        
    Returns:
        ArticleReviewSystem: Review system instance
    """
    return ArticleReviewSystem(article_manager)



class ArticleAnalytics:
    """
    Article analytics and engagement tracking system.
    
    Provides view counting, feedback integration, and performance metrics
    for articles on the platform.
    """
    
    def __init__(self, article_manager: ArticleManager):
        """
        Initialize analytics system with article manager.
        
        Args:
            article_manager: ArticleManager instance
        """
        self.article_manager = article_manager
        self.db_manager = article_manager.db_manager
        self.logger = article_manager.logger
    
    def update_article_feedback_stats(self, article_id: int) -> bool:
        """
        Update article feedback statistics from user_feedback table.
        
        Args:
            article_id: Article ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Python int
            article_id = int(article_id)
            
            # Get feedback stats for this article
            query = """
                SELECT 
                    COUNT(*) as total_feedback,
                    AVG(feedback_value) as avg_rating
                FROM user_feedback
                WHERE target_type = 'article' AND target_id = ?
            """
            
            result = self.db_manager.execute_query(query, (str(article_id),))
            
            if not result.empty:
                total_feedback = int(result.iloc[0]['total_feedback'])
                avg_rating = float(result.iloc[0]['avg_rating']) if result.iloc[0]['avg_rating'] else 0.0
                
                # Update article
                update_query = """
                    UPDATE articles 
                    SET total_feedback = ?, avg_rating = ?
                    WHERE id = ?
                """
                
                affected_rows = self.db_manager.execute_update(
                    update_query,
                    (total_feedback, avg_rating, article_id)
                )
                
                return affected_rows > 0
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating article feedback stats: {e}")
            return False
    
    def get_article_performance_metrics(self, article_id: int) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics for an article.
        
        Args:
            article_id: Article ID
            
        Returns:
            Dict[str, Any]: Performance metrics
        """
        try:
            # Convert to Python int
            article_id = int(article_id)
            
            article = self.article_manager.get_article_by_id(article_id)
            
            if not article:
                return {}
            
            # Get feedback breakdown
            feedback_query = """
                SELECT 
                    feedback_type,
                    COUNT(*) as count,
                    AVG(feedback_value) as avg_value
                FROM user_feedback
                WHERE target_type = 'article' AND target_id = ?
                GROUP BY feedback_type
            """
            
            feedback_stats = self.db_manager.execute_query(feedback_query, (str(article_id),))
            
            # Get comment count
            comment_query = """
                SELECT COUNT(*) as comment_count
                FROM comments
                WHERE target_type = 'article' AND target_id = ? AND is_approved = 1
            """
            
            comment_stats = self.db_manager.execute_query(comment_query, (str(article_id),))
            comment_count = int(comment_stats.iloc[0]['comment_count']) if not comment_stats.empty else 0
            
            # Calculate engagement rate (views to feedback ratio)
            engagement_rate = 0.0
            if article['views'] > 0:
                engagement_rate = (article['total_feedback'] + comment_count) / article['views'] * 100
            
            # Calculate days since publication
            days_published = 0
            if article['published_at']:
                try:
                    published_date = datetime.fromisoformat(article['published_at'])
                    days_published = (datetime.now() - published_date).days
                except:
                    pass
            
            metrics = {
                'article_id': article_id,
                'title': article['title'],
                'author': article['author'],
                'status': article['status'],
                'views': article['views'],
                'total_feedback': article['total_feedback'],
                'avg_rating': article['avg_rating'],
                'comment_count': comment_count,
                'engagement_rate': engagement_rate,
                'days_published': days_published,
                'feedback_breakdown': feedback_stats.to_dict('records') if not feedback_stats.empty else [],
                'created_at': article['created_at'],
                'published_at': article['published_at']
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting article performance metrics: {e}")
            return {}
    
    def show_article_analytics_dashboard(self, username: str) -> None:
        """
        Display analytics dashboard for articles.
        
        Args:
            username: Username (shows own articles for professors, all for admins)
        """
        try:
            st.markdown("## 📊 Article Analytics Dashboard")
            
            # Determine which articles to show
            if self.article_manager.auth_manager.is_admin(username):
                articles = self.article_manager.get_articles(status='published', limit=100)
                st.info("Showing analytics for all published articles")
            else:
                articles = self.article_manager.get_articles(author=username, limit=100)
                st.info("Showing analytics for your articles")
            
            if articles.empty:
                st.info("No articles to analyze yet.")
                return
            
            # Overall statistics
            st.markdown("### 📈 Overall Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Articles", len(articles))
            
            with col2:
                total_views = articles['views'].sum()
                st.metric("Total Views", total_views)
            
            with col3:
                total_feedback = articles['total_feedback'].sum()
                st.metric("Total Feedback", total_feedback)
            
            with col4:
                avg_rating = articles['avg_rating'].mean()
                st.metric("Avg Rating", f"{avg_rating:.2f}")
            
            st.markdown("---")
            
            # Top performing articles
            st.markdown("### 🏆 Top Performing Articles")
            
            # Sort by views
            top_articles = articles.nlargest(5, 'views')
            
            for idx, article in top_articles.iterrows():
                metrics = self.get_article_performance_metrics(article['id'])
                
                with st.expander(f"📄 {article['title']} - {article['views']} views"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Views", metrics['views'])
                        st.metric("Feedback", metrics['total_feedback'])
                    
                    with col2:
                        st.metric("Rating", f"{metrics['avg_rating']:.2f}")
                        st.metric("Comments", metrics['comment_count'])
                    
                    with col3:
                        st.metric("Engagement", f"{metrics['engagement_rate']:.1f}%")
                        st.metric("Days Published", metrics['days_published'])
                    
                    # Feedback breakdown
                    if metrics['feedback_breakdown']:
                        st.markdown("**Feedback Breakdown:**")
                        for fb in metrics['feedback_breakdown']:
                            st.write(f"- {fb['feedback_type']}: {fb['count']} ({fb['avg_value']:.1f} avg)")
            
            st.markdown("---")
            
            # Article list with metrics
            st.markdown("### 📋 All Articles")
            
            # Create a sortable dataframe
            display_df = articles[['title', 'author', 'status', 'views', 'avg_rating', 'total_feedback', 'published_at']].copy()
            display_df.columns = ['Title', 'Author', 'Status', 'Views', 'Rating', 'Feedback', 'Published']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
        except Exception as e:
            self.logger.error(f"Error displaying analytics dashboard: {e}")
            st.error("Unable to display analytics dashboard.")
    
    def get_trending_articles(self, days: int = 7, limit: int = 10) -> pd.DataFrame:
        """
        Get trending articles based on recent activity.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of articles to return
            
        Returns:
            pd.DataFrame: Trending articles
        """
        try:
            # Calculate trending score based on recent views and feedback
            query = """
                SELECT 
                    a.*,
                    (a.views * 0.5 + a.total_feedback * 2.0 + a.avg_rating * 10) as trending_score
                FROM articles a
                WHERE a.status = 'published'
                AND datetime(a.published_at) >= datetime('now', '-' || ? || ' days')
                ORDER BY trending_score DESC
                LIMIT ?
            """
            
            return self.db_manager.execute_query(query, (days, limit))
            
        except Exception as e:
            self.logger.error(f"Error getting trending articles: {e}")
            return pd.DataFrame()
    
    def show_trending_articles(self, days: int = 7, limit: int = 5) -> None:
        """
        Display trending articles widget.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of articles to display
        """
        try:
            st.markdown(f"### 🔥 Trending Articles (Last {days} Days)")
            
            trending = self.get_trending_articles(days, limit)
            
            if trending.empty:
                st.info("No trending articles in this period.")
                return
            
            for idx, article in trending.iterrows():
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**{article['title']}**")
                        st.caption(f"By {article['author']} | {article['category']}")
                    
                    with col2:
                        st.metric("👁️", article['views'])
                        st.metric("⭐", f"{article['avg_rating']:.1f}")
                    
                    if st.button("Read", key=f"trending_{article['id']}"):
                        st.session_state[f'viewing_article_{article["id"]}'] = True
                        st.rerun()
                    
                    st.markdown("---")
            
        except Exception as e:
            self.logger.error(f"Error displaying trending articles: {e}")
            st.error("Unable to display trending articles.")


def get_article_analytics(article_manager: ArticleManager) -> ArticleAnalytics:
    """
    Get article analytics system instance.
    
    Args:
        article_manager: ArticleManager instance
        
    Returns:
        ArticleAnalytics: Analytics system instance
    """
    return ArticleAnalytics(article_manager)
