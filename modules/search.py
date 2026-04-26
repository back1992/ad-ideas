"""
Search System for 广告思想简史 Platform

This module provides comprehensive search functionality across all content types
including articles, comments, timeline events, figures, and campaigns.
"""

import streamlit as st
import logging
from utils.logger import create_logger
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
import re
from datetime import datetime
from modules.database import DatabaseManager


from utils.i18n import t


class SearchSystem:
    """
    Comprehensive search system for platform content.
    
    Provides full-text search across articles, comments, and static content
    with ranking, filtering, and result highlighting capabilities.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize SearchSystem with database manager.
        
        Args:
            db_manager: Database manager instance for data access
        """
        self.db_manager = db_manager
        self.logger = create_logger('SearchSystem')
        
    
    def search(self, query: str, content_types: Optional[List[str]] = None,
               limit: int = 50) -> Dict[str, pd.DataFrame]:
        """
        Perform comprehensive search across platform content.
        
        Args:
            query: Search query string
            content_types: List of content types to search (None = all)
            limit: Maximum results per content type
            
        Returns:
            Dict[str, pd.DataFrame]: Search results by content type
        """
        try:
            if not query or not query.strip():
                return {}
            
            # Sanitize and prepare query
            clean_query = self._sanitize_query(query.strip())
            
            # Default to all content types if not specified
            if content_types is None:
                content_types = ['articles', 'comments']
            
            results = {}
            
            # Search articles
            if 'articles' in content_types:
                results['articles'] = self._search_articles(clean_query, limit)
            
            # Search comments
            if 'comments' in content_types:
                results['comments'] = self._search_comments(clean_query, limit)
            
            # Log search activity
            self.logger.info(f"Search performed: '{query}' - Found {sum(len(df) for df in results.values())} results")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error performing search: {e}")
            return {}
    
    def _search_articles(self, query: str, limit: int) -> pd.DataFrame:
        """
        Search articles by title, content, excerpt, tags, and category.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            pd.DataFrame: Matching articles with relevance scores
        """
        try:
            # Build search query with relevance scoring
            sql_query = """
                SELECT 
                    id,
                    title,
                    excerpt,
                    content,
                    category,
                    tags,
                    author,
                    status,
                    views,
                    avg_rating,
                    created_at,
                    published_at,
                    (
                        CASE WHEN title LIKE ? THEN 10 ELSE 0 END +
                        CASE WHEN excerpt LIKE ? THEN 5 ELSE 0 END +
                        CASE WHEN content LIKE ? THEN 3 ELSE 0 END +
                        CASE WHEN tags LIKE ? THEN 7 ELSE 0 END +
                        CASE WHEN category LIKE ? THEN 4 ELSE 0 END
                    ) as relevance_score
                FROM articles
                WHERE 
                    status = 'published' AND
                    (
                        title LIKE ? OR
                        excerpt LIKE ? OR
                        content LIKE ? OR
                        tags LIKE ? OR
                        category LIKE ?
                    )
                ORDER BY relevance_score DESC, views DESC, avg_rating DESC
                LIMIT ?
            """
            
            # Prepare search pattern
            pattern = f"%{query}%"
            params = (
                pattern, pattern, pattern, pattern, pattern,  # For relevance scoring
                pattern, pattern, pattern, pattern, pattern,  # For WHERE clause
                limit
            )
            
            results = self.db_manager.execute_query(sql_query, params)
            
            # Add result type and highlight matches
            if not results.empty:
                results['result_type'] = 'article'
                results['highlight'] = results.apply(
                    lambda row: self._create_highlight(row, query), axis=1
                )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching articles: {e}")
            return pd.DataFrame()
    
    def _search_comments(self, query: str, limit: int) -> pd.DataFrame:
        """
        Search comments by content and username.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            pd.DataFrame: Matching comments with relevance scores
        """
        try:
            sql_query = """
                SELECT 
                    id,
                    username,
                    content,
                    target_type,
                    target_id,
                    timestamp,
                    likes,
                    parent_id,
                    (
                        CASE WHEN content LIKE ? THEN 10 ELSE 0 END +
                        CASE WHEN username LIKE ? THEN 5 ELSE 0 END
                    ) as relevance_score
                FROM comments
                WHERE 
                    is_approved = 1 AND
                    (
                        content LIKE ? OR
                        username LIKE ?
                    )
                ORDER BY relevance_score DESC, likes DESC, timestamp DESC
                LIMIT ?
            """
            
            pattern = f"%{query}%"
            params = (
                pattern, pattern,  # For relevance scoring
                pattern, pattern,  # For WHERE clause
                limit
            )
            
            results = self.db_manager.execute_query(sql_query, params)
            
            # Add result type and highlight
            if not results.empty:
                results['result_type'] = 'comment'
                results['highlight'] = results['content'].apply(
                    lambda text: self._highlight_text(text, query)
                )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching comments: {e}")
            return pd.DataFrame()
    
    def _sanitize_query(self, query: str) -> str:
        """
        Sanitize search query to prevent SQL injection and improve search.
        
        Args:
            query: Raw search query
            
        Returns:
            str: Sanitized query
        """
        # Remove special SQL characters that could cause issues
        sanitized = re.sub(r'[%_\[\]]', '', query)
        
        # Limit length
        max_length = 200
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    def _highlight_text(self, text: str, query: str, max_length: int = 200) -> str:
        """
        Create highlighted excerpt from text containing query.
        
        Args:
            text: Full text to search
            query: Search query to highlight
            max_length: Maximum excerpt length
            
        Returns:
            str: Highlighted excerpt
        """
        try:
            if not text or not query:
                return text[:max_length] if text else ""
            
            # Find query position (case-insensitive)
            text_lower = text.lower()
            query_lower = query.lower()
            pos = text_lower.find(query_lower)
            
            if pos == -1:
                # Query not found, return beginning
                return text[:max_length] + ("..." if len(text) > max_length else "")
            
            # Calculate excerpt window around match
            start = max(0, pos - 50)
            end = min(len(text), pos + len(query) + 150)
            
            excerpt = text[start:end]
            
            # Add ellipsis if truncated
            if start > 0:
                excerpt = "..." + excerpt
            if end < len(text):
                excerpt = excerpt + "..."
            
            # Highlight the query (case-insensitive replacement)
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            highlighted = pattern.sub(lambda m: f"**{m.group(0)}**", excerpt)
            
            return highlighted
            
        except Exception as e:
            self.logger.error(f"Error highlighting text: {e}")
            return text[:max_length] if text else ""
    
    def _create_highlight(self, row: pd.Series, query: str) -> str:
        """
        Create highlighted excerpt for article search result.
        
        Args:
            row: Article row data
            query: Search query
            
        Returns:
            str: Highlighted excerpt
        """
        try:
            # Check where the match occurred and prioritize
            query_lower = query.lower()
            
            # Title match (highest priority)
            if query_lower in row['title'].lower():
                return self._highlight_text(row['title'], query, 150)
            
            # Excerpt match
            if row['excerpt'] and query_lower in row['excerpt'].lower():
                return self._highlight_text(row['excerpt'], query, 200)
            
            # Content match
            if query_lower in row['content'].lower():
                return self._highlight_text(row['content'], query, 200)
            
            # Tags match
            if row['tags'] and query_lower in row['tags'].lower():
                return f"Tags: {row['tags']}"
            
            # Default to excerpt or content beginning
            return row['excerpt'] if row['excerpt'] else row['content'][:200]
            
        except Exception as e:
            self.logger.error(f"Error creating highlight: {e}")
            return row.get('excerpt', '')[:200]
    
    def display_search_interface(self) -> None:
        """Display search interface with results."""
        try:
            st.markdown(f"## 🔍 {t('search_title')}")
            st.markdown(t('search_subtitle'))
            
            # Search input
            col1, col2 = st.columns([4, 1])

            with col1:
                query = st.text_input(
                    "Search query",
                    placeholder=t('search_query_placeholder'),
                    label_visibility="collapsed",
                    key="search_query"
                )

            with col2:
                search_button = st.button(f"🔍 {t('search_button')}", type="primary", use_container_width=True)

            # Content type filters
            st.markdown(f"**{t('filter_by_type')}:**")
            col1, col2, col3 = st.columns(3)

            with col1:
                search_articles = st.checkbox(f"📄 {t('search_articles')}", value=True)
            with col2:
                search_comments = st.checkbox(f"💬 {t('search_comments')}", value=True)
            with col3:
                search_all = st.checkbox(f"🌐 {t('search_all')}", value=False)

            # Perform search
            if search_button or query:
                if query and query.strip():
                    # Determine content types to search
                    content_types = []
                    if search_articles or search_all:
                        content_types.append('articles')
                    if search_comments or search_all:
                        content_types.append('comments')

                    if not content_types:
                        st.warning(t('no_content_type_selected'))
                        return

                    # Perform search
                    with st.spinner(t('searching')):
                        results = self.search(query, content_types)

                    # Display results
                    self._display_search_results(results, query)
                else:
                    st.info(t('enter_search_query'))

        except Exception as e:
            self.logger.error(f"Error displaying search interface: {e}")
            st.error(t('unable_to_search'))
    
    def _display_search_results(self, results: Dict[str, pd.DataFrame], query: str) -> None:
        """
        Display search results organized by content type.
        
        Args:
            results: Search results by content type
            query: Original search query
        """
        try:
            # Calculate total results
            total_results = sum(len(df) for df in results.values() if not df.empty)
            
            if total_results == 0:
                st.warning(t('no_results_found').format(query=query))
                return

            st.success(t('found_results').format(count=total_results, query=query))
            st.markdown("---")
            
            # Display article results
            if 'articles' in results and not results['articles'].empty:
                self._display_article_results(results['articles'], query)
            
            # Display comment results
            if 'comments' in results and not results['comments'].empty:
                self._display_comment_results(results['comments'], query)
            
        except Exception as e:
            self.logger.error(f"Error displaying search results: {e}")
            st.error("Unable to display search results.")
    
    def _display_article_results(self, articles: pd.DataFrame, query: str) -> None:
        """Display article search results."""
        try:
            st.markdown(f"### 📄 {t('article_results')} ({len(articles)} results)")
            
            for idx, article in articles.iterrows():
                with st.container():
                    # Article title with relevance score
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.markdown(f"#### {article['title']}")
                    
                    with col2:
                        if article['relevance_score'] > 0:
                            st.caption(f"{t('relevance_score')}: {article['relevance_score']}")
                    
                    # Metadata
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.caption(f"👤 {article['author']}")
                    with col2:
                        st.caption(f"📁 {article['category']}")
                    with col3:
                        st.caption(f"👁️ {article['views']} {t('views')}")
                    with col4:
                        st.caption(f"⭐ {article['avg_rating']:.1f}")
                    
                    # Highlighted excerpt
                    st.markdown(article['highlight'])
                    
                    # Tags
                    if article['tags']:
                        st.caption(f"🏷️ {article['tags']}")
                    
                    # View button
                    if st.button(t('view_article'), key=f"view_article_{article['id']}"):
                        st.session_state['view_article_id'] = article['id']
                        st.rerun()
                    
                    st.divider()
            
        except Exception as e:
            self.logger.error(f"Error displaying article results: {e}")
            st.error("Unable to display article results.")
    
    def _display_comment_results(self, comments: pd.DataFrame, query: str) -> None:
        """Display comment search results."""
        try:
            st.markdown(f"### 💬 {t('comment_results')} ({len(comments)} results)")
            
            for idx, comment in comments.iterrows():
                with st.container():
                    # Comment header
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**👤 {comment['username']}**")
                    with col2:
                        st.caption(f"📍 {comment['target_type']}: {comment['target_id']}")
                    with col3:
                        st.caption(f"👍 {comment['likes']}")
                    
                    # Highlighted comment content
                    st.markdown(comment['highlight'])
                    
                    # Timestamp
                    st.caption(f"🕒 {comment['timestamp']}")
                    
                    st.divider()
            
        except Exception as e:
            self.logger.error(f"Error displaying comment results: {e}")
            st.error(t('unable_to_display_comments'))
    
    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial query.
        
        Args:
            partial_query: Partial search query
            limit: Maximum suggestions
            
        Returns:
            List[str]: Search suggestions
        """
        try:
            if not partial_query or len(partial_query) < 2:
                return []
            
            suggestions = []
            
            # Get suggestions from article titles
            query = """
                SELECT DISTINCT title
                FROM articles
                WHERE status = 'published' AND title LIKE ?
                LIMIT ?
            """
            pattern = f"%{partial_query}%"
            results = self.db_manager.execute_query(query, (pattern, limit))
            
            if not results.empty:
                suggestions.extend(results['title'].tolist())
            
            # Get suggestions from tags
            if len(suggestions) < limit:
                query = """
                    SELECT DISTINCT tags
                    FROM articles
                    WHERE status = 'published' AND tags LIKE ?
                    LIMIT ?
                """
                results = self.db_manager.execute_query(query, (pattern, limit - len(suggestions)))
                
                if not results.empty:
                    for tags in results['tags']:
                        if tags:
                            tag_list = [t.strip() for t in tags.split(',')]
                            matching_tags = [t for t in tag_list if partial_query.lower() in t.lower()]
                            suggestions.extend(matching_tags[:limit - len(suggestions)])
            
            return suggestions[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting search suggestions: {e}")
            return []


# Global search system instance
_search_system = None

def get_search_system(db_manager: DatabaseManager) -> SearchSystem:
    """
    Get singleton search system instance.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        SearchSystem: Singleton search system instance
    """
    global _search_system
    if _search_system is None:
        _search_system = SearchSystem(db_manager)
    return _search_system
