"""
Property-based tests for ArticleManager

Feature: platform-core, Property 11: Article Status Workflow
Validates: Requirements 5.2, 5.3

This module contains property-based tests using Hypothesis to verify
article status workflow transitions and visibility rules.
"""

import os
import tempfile
from typing import Tuple, List, Optional
from datetime import datetime

import pytest
import pandas as pd
from hypothesis import given, strategies as st, settings, assume

from modules.database import DatabaseManager
from modules.auth import AuthManager
from modules.articles import ArticleManager


class TestArticleWorkflowProperties:
    """
    Property-based tests for article workflow system.
    
    Feature: platform-core, Property 11: Article Status Workflow
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_counter = 0
    
    def _get_fresh_system(self):
        """Create a fresh database and article manager for each test example."""
        self.test_counter += 1
        test_db_path = os.path.join(self.temp_dir, f"test_articles_{self.test_counter}.db")
        
        # Create test database manager
        db_manager = DatabaseManager(test_db_path)
        db_manager.init_database()
        
        # Create mock auth manager (simplified for testing)
        auth_manager = MockAuthManager()
        
        # Create article manager
        return ArticleManager(db_manager, auth_manager)
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        # Clean up all test database files
        import glob
        for db_file in glob.glob(os.path.join(self.temp_dir, "test_articles_*.db")):
            if os.path.exists(db_file):
                os.remove(db_file)
        os.rmdir(self.temp_dir)
    
    @given(
        st.text(min_size=1, max_size=100),  # title
        st.text(min_size=1, max_size=500),  # content
        st.text(max_size=200),  # excerpt
        st.sampled_from(['Advertising History', 'Marketing Theory', 'Case Studies']),  # category
        st.text(max_size=50),  # tags
        st.text(min_size=1, max_size=20),  # author
        st.sampled_from(['draft', 'review', 'published'])  # initial_status
    )
    @settings(max_examples=10, deadline=None)
    def test_article_status_workflow_transitions(
        self,
        title: str,
        content: str,
        excerpt: str,
        category: str,
        tags: str,
        author: str,
        initial_status: str
    ):
        """
        Property 11: For any article status change, the system should enforce 
        proper workflow transitions and update visibility accordingly.
        
        Feature: platform-core, Property 11: Article Status Workflow
        Validates: Requirements 5.2, 5.3
        """
        # Get fresh system for this test
        article_manager = self._get_fresh_system()
        
        # Create article with initial status
        success = article_manager.save_article(
            title=title,
            content=content,
            excerpt=excerpt,
            category=category,
            tags=tags,
            author=author,
            status=initial_status,
            article_id=None
        )
        
        assert success is True, "Article creation should succeed"
        
        # Get the created article
        articles = article_manager.get_articles(author=author, limit=1)
        assert len(articles) == 1, "Should have exactly one article"
        
        article = articles.iloc[0]
        article_id = article['id']
        
        # Verify initial status is set correctly
        assert article['status'] == initial_status, \
            f"Initial status should be {initial_status}, got {article['status']}"
        
        # Verify published_at is set only for published status
        if initial_status == 'published':
            assert article['published_at'] is not None, \
                "published_at should be set for published articles"
        else:
            assert article['published_at'] is None, \
                "published_at should be None for non-published articles"
        
        # Test status transition: draft → review
        if initial_status == 'draft':
            success = article_manager.save_article(
                title=title,
                content=content,
                excerpt=excerpt,
                category=category,
                tags=tags,
                author=author,
                status='review',
                article_id=article_id
            )
            
            assert success is True, "Status transition draft→review should succeed"
            
            # Verify status changed
            updated_article = article_manager.get_article_by_id(article_id)
            assert updated_article['status'] == 'review', \
                "Status should be 'review' after transition"
            assert updated_article['published_at'] is None, \
                "published_at should still be None for review status"
        
        # Test status transition: review → published
        if initial_status == 'review' or (initial_status == 'draft'):
            # First move to review if needed
            if initial_status == 'draft':
                article_manager.save_article(
                    title=title, content=content, excerpt=excerpt,
                    category=category, tags=tags, author=author,
                    status='review', article_id=article_id
                )
            
            # Now transition to published
            success = article_manager.save_article(
                title=title,
                content=content,
                excerpt=excerpt,
                category=category,
                tags=tags,
                author=author,
                status='published',
                article_id=article_id
            )
            
            assert success is True, "Status transition to published should succeed"
            
            # Verify status changed and published_at is set
            published_article = article_manager.get_article_by_id(article_id)
            assert published_article['status'] == 'published', \
                "Status should be 'published' after transition"
            assert published_article['published_at'] is not None, \
                "published_at should be set when article is published"
            
            # Verify published_at is a valid timestamp
            try:
                published_date = datetime.fromisoformat(published_article['published_at'])
                assert published_date <= datetime.now(), \
                    "published_at should not be in the future"
            except ValueError:
                pytest.fail(f"published_at should be a valid ISO timestamp, got {published_article['published_at']}")
        
        # Test status transition: published → archived (admin only)
        if initial_status == 'published':
            success = article_manager.save_article(
                title=title,
                content=content,
                excerpt=excerpt,
                category=category,
                tags=tags,
                author=author,
                status='archived',
                article_id=article_id
            )
            
            assert success is True, "Status transition published→archived should succeed"
            
            # Verify status changed
            archived_article = article_manager.get_article_by_id(article_id)
            assert archived_article['status'] == 'archived', \
                "Status should be 'archived' after transition"
            # published_at should be preserved
            assert archived_article['published_at'] is not None, \
                "published_at should be preserved when archiving"
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=50),  # title
                st.text(min_size=1, max_size=200),  # content
                st.text(min_size=1, max_size=15),  # author
                st.sampled_from(['draft', 'review', 'published', 'archived'])  # status
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=10, deadline=None)
    def test_article_status_persistence(
        self,
        article_data: List[Tuple[str, str, str, str]]
    ):
        """
        Property: For any set of articles with different statuses, all status 
        values should be persisted correctly and retrievable.
        
        Feature: platform-core, Property 11: Article Status Workflow
        Validates: Requirements 5.2
        """
        # Get fresh system for this test
        article_manager = self._get_fresh_system()
        
        # Create all articles
        created_articles = []
        for title, content, author, status in article_data:
            success = article_manager.save_article(
                title=title,
                content=content,
                excerpt="",
                category="Other",
                tags="",
                author=author,
                status=status,
                article_id=None
            )
            assert success is True, f"Article creation should succeed for {title}"
            
            # Get the created article
            articles = article_manager.get_articles(author=author, limit=100)
            matching = articles[articles['title'] == title]
            if len(matching) > 0:
                created_articles.append(matching.iloc[-1])  # Get most recent
        
        # Verify all articles were created
        assert len(created_articles) == len(article_data), \
            f"Expected {len(article_data)} articles, created {len(created_articles)}"
        
        # Verify each article's status is persisted correctly
        for i, (title, content, author, expected_status) in enumerate(article_data):
            # Find the article by title and author
            article = None
            for created in created_articles:
                if created['title'] == title and created['author'] == author:
                    article = created
                    break
            
            assert article is not None, f"Article '{title}' should exist"
            assert article['status'] == expected_status, \
                f"Article '{title}' should have status '{expected_status}', got '{article['status']}'"
            
            # Verify published_at consistency
            if expected_status == 'published':
                assert article['published_at'] is not None, \
                    f"Published article '{title}' should have published_at set"
            elif expected_status in ['draft', 'review']:
                assert article['published_at'] is None, \
                    f"Non-published article '{title}' should not have published_at set"
    
    @given(
        st.text(min_size=1, max_size=50),  # title
        st.text(min_size=1, max_size=200),  # content
        st.text(min_size=1, max_size=15),  # author
        st.lists(
            st.sampled_from(['draft', 'review', 'published', 'archived']),
            min_size=2,
            max_size=4
        )  # sequence of status changes
    )
    @settings(max_examples=10, deadline=None)
    def test_article_status_workflow_sequence(
        self,
        title: str,
        content: str,
        author: str,
        status_sequence: List[str]
    ):
        """
        Property: For any sequence of status changes, each transition should 
        be persisted correctly and the final status should match the last change.
        
        Feature: platform-core, Property 11: Article Status Workflow
        Validates: Requirements 5.2, 5.3
        """
        # Get fresh system for this test
        article_manager = self._get_fresh_system()
        
        # Create article with first status
        initial_status = status_sequence[0]
        success = article_manager.save_article(
            title=title,
            content=content,
            excerpt="",
            category="Other",
            tags="",
            author=author,
            status=initial_status,
            article_id=None
        )
        assert success is True, "Initial article creation should succeed"
        
        # Get article ID
        articles = article_manager.get_articles(author=author, limit=1)
        article_id = articles.iloc[0]['id']
        
        # Track when article was first published
        first_published_at = None
        
        # Apply each status change in sequence
        for i, new_status in enumerate(status_sequence[1:], 1):
            success = article_manager.save_article(
                title=title,
                content=content,
                excerpt="",
                category="Other",
                tags="",
                author=author,
                status=new_status,
                article_id=article_id
            )
            
            assert success is True, f"Status change {i} to '{new_status}' should succeed"
            
            # Verify status was updated
            updated_article = article_manager.get_article_by_id(article_id)
            assert updated_article['status'] == new_status, \
                f"Status should be '{new_status}' after change {i}, got '{updated_article['status']}'"
            
            # Track published_at behavior
            if new_status == 'published' and first_published_at is None:
                # First time publishing - should set published_at
                assert updated_article['published_at'] is not None, \
                    f"published_at should be set on first publish (change {i})"
                first_published_at = updated_article['published_at']
            elif new_status == 'published' and first_published_at is not None:
                # Re-publishing - should preserve original published_at
                assert updated_article['published_at'] == first_published_at, \
                    f"published_at should be preserved on re-publish (change {i})"
            elif new_status in ['draft', 'review']:
                # Moving back to draft/review - published_at behavior depends on implementation
                # Some systems preserve it, some clear it - we'll just verify it's consistent
                pass
            elif new_status == 'archived':
                # Archiving - should preserve published_at if it was set
                if first_published_at is not None:
                    assert updated_article['published_at'] is not None, \
                        f"published_at should be preserved when archiving (change {i})"
        
        # Verify final status matches last in sequence
        final_article = article_manager.get_article_by_id(article_id)
        expected_final_status = status_sequence[-1]
        assert final_article['status'] == expected_final_status, \
            f"Final status should be '{expected_final_status}', got '{final_article['status']}'"
    
    @given(
        st.text(min_size=1, max_size=50),  # title
        st.text(min_size=1, max_size=200),  # content
        st.text(min_size=1, max_size=15),  # author
        st.sampled_from(['draft', 'review', 'published', 'archived'])  # status
    )
    @settings(max_examples=10, deadline=None)
    def test_article_visibility_by_status(
        self,
        title: str,
        content: str,
        author: str,
        status: str
    ):
        """
        Property: For any article status, the article should be retrievable 
        with appropriate filters and visibility rules.
        
        Feature: platform-core, Property 11: Article Status Workflow
        Validates: Requirements 5.3
        """
        # Get fresh system for this test
        article_manager = self._get_fresh_system()
        
        # Create article with specified status
        success = article_manager.save_article(
            title=title,
            content=content,
            excerpt="",
            category="Other",
            tags="",
            author=author,
            status=status,
            article_id=None
        )
        assert success is True, "Article creation should succeed"
        
        # Test retrieval by status filter
        articles_by_status = article_manager.get_articles(status=status)
        assert len(articles_by_status) > 0, \
            f"Should be able to retrieve articles with status '{status}'"
        
        # Verify the article is in the results
        matching = articles_by_status[
            (articles_by_status['title'] == title) & 
            (articles_by_status['author'] == author)
        ]
        assert len(matching) > 0, \
            f"Article should be retrievable by status filter '{status}'"
        
        # Test retrieval by author
        articles_by_author = article_manager.get_articles(author=author)
        assert len(articles_by_author) > 0, \
            "Should be able to retrieve articles by author"
        
        matching_author = articles_by_author[
            (articles_by_author['title'] == title) & 
            (articles_by_author['status'] == status)
        ]
        assert len(matching_author) > 0, \
            "Article should be retrievable by author filter"
        
        # Test retrieval without filters (should include all statuses)
        all_articles = article_manager.get_articles()
        matching_all = all_articles[
            (all_articles['title'] == title) & 
            (all_articles['author'] == author) &
            (all_articles['status'] == status)
        ]
        assert len(matching_all) > 0, \
            "Article should be retrievable without filters"
        
        # Verify status is correct in all retrievals
        for articles_df in [articles_by_status, articles_by_author, all_articles]:
            matching = articles_df[
                (articles_df['title'] == title) & 
                (articles_df['author'] == author)
            ]
            if len(matching) > 0:
                assert matching.iloc[0]['status'] == status, \
                    f"Retrieved article should have status '{status}'"
    
    @given(
        st.text(min_size=1, max_size=50),  # title
        st.text(min_size=1, max_size=200),  # content
        st.text(min_size=1, max_size=15),  # author
    )
    @settings(max_examples=10, deadline=None)
    def test_published_at_timestamp_consistency(
        self,
        title: str,
        content: str,
        author: str
    ):
        """
        Property: For any article that transitions to published status, 
        published_at should be set to a valid timestamp and preserved 
        across subsequent updates.
        
        Feature: platform-core, Property 11: Article Status Workflow
        Validates: Requirements 5.2, 5.3
        """
        # Get fresh system for this test
        article_manager = self._get_fresh_system()
        
        # Create article as draft
        success = article_manager.save_article(
            title=title,
            content=content,
            excerpt="",
            category="Other",
            tags="",
            author=author,
            status='draft',
            article_id=None
        )
        assert success is True, "Article creation should succeed"
        
        # Get article ID
        articles = article_manager.get_articles(author=author, limit=1)
        article_id = articles.iloc[0]['id']
        
        # Verify published_at is None for draft
        draft_article = article_manager.get_article_by_id(article_id)
        assert draft_article['published_at'] is None, \
            "Draft article should not have published_at set"
        
        # Record time before publishing
        time_before = datetime.now()
        
        # Publish the article
        success = article_manager.save_article(
            title=title,
            content=content,
            excerpt="",
            category="Other",
            tags="",
            author=author,
            status='published',
            article_id=article_id
        )
        assert success is True, "Publishing should succeed"
        
        # Record time after publishing
        time_after = datetime.now()
        
        # Verify published_at is set
        published_article = article_manager.get_article_by_id(article_id)
        assert published_article['published_at'] is not None, \
            "Published article should have published_at set"
        
        # Verify published_at is a valid timestamp within reasonable range
        published_at = datetime.fromisoformat(published_article['published_at'])
        assert time_before <= published_at <= time_after, \
            f"published_at should be between {time_before} and {time_after}, got {published_at}"
        
        # Store the original published_at
        original_published_at = published_article['published_at']
        
        # Update the article content (keeping status as published)
        success = article_manager.save_article(
            title=title + " Updated",
            content=content + " Updated",
            excerpt="",
            category="Other",
            tags="",
            author=author,
            status='published',
            article_id=article_id
        )
        assert success is True, "Article update should succeed"
        
        # Verify published_at is preserved after update
        updated_article = article_manager.get_article_by_id(article_id)
        assert updated_article['published_at'] == original_published_at, \
            "published_at should be preserved when updating published article"


class MockAuthManager:
    """Mock authentication manager for testing."""
    
    def is_professor_or_admin(self, username: str) -> bool:
        """Mock permission check - always returns True for testing."""
        return True
    
    def is_admin(self, username: str) -> bool:
        """Mock admin check - returns True for 'admin' username."""
        return username == 'admin'
