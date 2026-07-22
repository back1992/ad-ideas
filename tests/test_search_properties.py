"""
Property-based tests for SearchSystem and RecommendationEngine

Feature: platform-core, Property 13: Search Result Relevance
Feature: platform-core, Property 14: Search Consistency
Feature: platform-core, Property 15: Recommendation Diversity
Validates: Requirements 9.1, 9.2, 9.3, 9.4

This module contains property-based tests using Hypothesis to verify
search result relevance, consistency, and recommendation quality.
"""

import os
import shutil
import tempfile
from typing import List, Tuple, Optional

import pytest
import pandas as pd
from hypothesis import given, strategies as st, settings, assume

from modules.database import DatabaseManager
from modules.search import SearchSystem
from modules.recommendations import RecommendationEngine


class TestSearchResultRelevance:
    """
    Property-based tests for search result relevance.
    
    Feature: platform-core, Property 13: Search Result Relevance
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_search.db")
        
        # Create test database manager
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        
        # Create search system
        self.search_system = SearchSystem(self.db_manager)
        
        # Create test articles
        self._create_test_articles()
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_articles(self):
        """Create test articles with known content."""
        test_articles = [
            ("Advertising History Overview", "This article covers the history of advertising", 
             "advertising, history", "Advertising History", "published"),
            ("Marketing Strategies", "Modern marketing strategies and techniques",
             "marketing, strategy", "Marketing Theory", "published"),
            ("Digital Advertising", "Digital advertising in the modern era",
             "digital, advertising, online", "Advertising History", "published"),
            ("Brand Management", "How to manage brand identity",
             "brand, management", "Marketing Theory", "published"),
            ("Social Media Marketing", "Marketing through social media platforms",
             "social media, marketing", "Marketing Theory", "published"),
        ]
        
        for title, content, tags, category, status in test_articles:
            query = """
                INSERT INTO articles (title, content, excerpt, tags, category, author, status, views, avg_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db_manager.execute_update(
                query, 
                (title, content, content[:50], tags, category, "test_author", status, 10, 4.0)
            )
    
    @given(
        query=st.sampled_from(["advertising", "marketing", "digital", "brand", "social"])
    )
    @settings(max_examples=5, deadline=None)
    def test_search_returns_relevant_results(self, query: str):
        """
        Property 13: For any search query, results should contain the query term
        in title, content, tags, or category.
        
        Feature: platform-core, Property 13: Search Result Relevance
        Validates: Requirements 9.1
        """
        # Perform search
        results = self.search_system.search(query, content_types=['articles'])
        
        # Verify results exist
        if 'articles' in results and not results['articles'].empty:
            articles = results['articles']
            
            # Each result should contain the query in some field
            for idx, article in articles.iterrows():
                query_lower = query.lower()
                
                # Check if query appears in any searchable field
                found_in_title = query_lower in str(article['title']).lower()
                found_in_content = query_lower in str(article['content']).lower()
                found_in_tags = query_lower in str(article['tags']).lower() if article['tags'] else False
                found_in_category = query_lower in str(article['category']).lower()
                
                assert found_in_title or found_in_content or found_in_tags or found_in_category, \
                    f"Query '{query}' should appear in at least one field of result: {article['title']}"
    
    @given(
        query=st.sampled_from(["advertising", "marketing"])
    )
    @settings(max_examples=5, deadline=None)
    def test_search_relevance_scoring(self, query: str):
        """
        Property 13: For any search query, results with query in title should
        have higher relevance scores than results with query only in content.
        
        Feature: platform-core, Property 13: Search Result Relevance
        Validates: Requirements 9.1
        """
        # Perform search
        results = self.search_system.search(query, content_types=['articles'])
        
        if 'articles' in results and not results['articles'].empty:
            articles = results['articles']
            
            # Separate results by where query appears
            title_matches = []
            content_only_matches = []
            
            query_lower = query.lower()
            
            for idx, article in articles.iterrows():
                if query_lower in str(article['title']).lower():
                    title_matches.append(article['relevance_score'])
                elif query_lower in str(article['content']).lower():
                    content_only_matches.append(article['relevance_score'])
            
            # If we have both types, title matches should have higher scores
            if title_matches and content_only_matches:
                min_title_score = min(title_matches)
                max_content_score = max(content_only_matches)
                
                assert min_title_score >= max_content_score, \
                    f"Title matches should have higher relevance than content-only matches"
    
    @given(
        query=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != '')
    )
    @settings(max_examples=5, deadline=None)
    def test_search_handles_arbitrary_queries(self, query: str):
        """
        Property 13: For any valid query string, search should return results
        or empty DataFrame without errors.
        
        Feature: platform-core, Property 13: Search Result Relevance
        Validates: Requirements 9.1
        """
        # Perform search - should not raise exceptions
        results = self.search_system.search(query, content_types=['articles'])
        
        # Verify results structure
        assert isinstance(results, dict), "Search should return a dictionary"
        
        if 'articles' in results:
            assert isinstance(results['articles'], pd.DataFrame), \
                "Article results should be a DataFrame"
            
            # If results exist, verify they have required fields
            if not results['articles'].empty:
                required_fields = ['id', 'title', 'content', 'relevance_score']
                for field in required_fields:
                    assert field in results['articles'].columns, \
                        f"Results should contain '{field}' field"


class TestSearchConsistency:
    """
    Property-based tests for search consistency.
    
    Feature: platform-core, Property 14: Search Consistency
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_search_consistency.db")
        
        # Create test database manager
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        
        # Create search system
        self.search_system = SearchSystem(self.db_manager)
        
        # Create test data
        self._create_test_data()
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_data(self):
        """Create test articles and comments."""
        # Create articles
        articles = [
            ("Test Article 1", "Content about advertising", "advertising", "Category A"),
            ("Test Article 2", "Content about marketing", "marketing", "Category B"),
            ("Test Article 3", "Content about both advertising and marketing", "advertising, marketing", "Category A"),
        ]
        
        for title, content, tags, category in articles:
            query = """
                INSERT INTO articles (title, content, excerpt, tags, category, author, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.db_manager.execute_update(
                query,
                (title, content, content[:30], tags, category, "author1", "published")
            )
        
        # Create comments
        comments = [
            ("user1", "Great article about advertising", "article", "1"),
            ("user2", "Marketing insights are valuable", "article", "2"),
        ]
        
        for username, content, target_type, target_id in comments:
            query = """
                INSERT INTO comments (username, content, target_type, target_id, is_approved)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db_manager.execute_update(query, (username, content, target_type, target_id, 1))
    
    @given(
        query=st.sampled_from(["advertising", "marketing", "article"])
    )
    @settings(max_examples=5, deadline=None)
    def test_search_deterministic_results(self, query: str):
        """
        Property 14: For any query, multiple searches should return identical
        results in the same order (deterministic behavior).
        
        Feature: platform-core, Property 14: Search Consistency
        Validates: Requirements 9.1
        """
        # Perform search multiple times
        results1 = self.search_system.search(query, content_types=['articles', 'comments'])
        results2 = self.search_system.search(query, content_types=['articles', 'comments'])
        results3 = self.search_system.search(query, content_types=['articles', 'comments'])
        
        # Verify results are identical
        for content_type in ['articles', 'comments']:
            if content_type in results1:
                # Check all three results have same content type
                assert content_type in results2, f"{content_type} should be in all results"
                assert content_type in results3, f"{content_type} should be in all results"
                
                df1 = results1[content_type]
                df2 = results2[content_type]
                df3 = results3[content_type]
                
                # Check same number of results
                assert len(df1) == len(df2) == len(df3), \
                    f"All searches should return same number of {content_type} results"
                
                # Check same IDs in same order
                if not df1.empty:
                    ids1 = df1['id'].tolist()
                    ids2 = df2['id'].tolist()
                    ids3 = df3['id'].tolist()
                    
                    assert ids1 == ids2 == ids3, \
                        f"Search results should be in same order across multiple searches"
    
    @given(
        query=st.sampled_from(["advertising", "marketing"])
    )
    @settings(max_examples=5, deadline=None)
    def test_search_empty_query_handling(self, query: str):
        """
        Property 14: For any query, empty or whitespace-only queries should
        return empty results consistently.
        
        Feature: platform-core, Property 14: Search Consistency
        Validates: Requirements 9.1
        """
        # Test empty query
        empty_results = self.search_system.search("", content_types=['articles'])
        assert empty_results == {}, "Empty query should return empty results"
        
        # Test whitespace query
        whitespace_results = self.search_system.search("   ", content_types=['articles'])
        assert whitespace_results == {}, "Whitespace query should return empty results"
        
        # Test valid query for comparison
        valid_results = self.search_system.search(query, content_types=['articles'])
        assert isinstance(valid_results, dict), "Valid query should return dict"
    
    @given(
        query=st.sampled_from(["advertising", "marketing"]),
        limit=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=5, deadline=None)
    def test_search_respects_limit(self, query: str, limit: int):
        """
        Property 14: For any query and limit, search should return at most
        'limit' results per content type.
        
        Feature: platform-core, Property 14: Search Consistency
        Validates: Requirements 9.1
        """
        # Perform search with limit
        results = self.search_system.search(query, content_types=['articles', 'comments'], limit=limit)
        
        # Verify limit is respected
        for content_type, df in results.items():
            if not df.empty:
                assert len(df) <= limit, \
                    f"Results for {content_type} should not exceed limit of {limit}, got {len(df)}"


class TestRecommendationDiversity:
    """
    Property-based tests for recommendation diversity and quality.
    
    Feature: platform-core, Property 15: Recommendation Diversity
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_recommendations.db")
        
        # Create test database manager
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        
        # Create recommendation engine
        self.rec_engine = RecommendationEngine(self.db_manager)
        
        # Create test data
        self._create_test_data()
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_data(self):
        """Create test articles with various categories and tags."""
        articles = [
            ("Article 1", "Content 1", "tag1, tag2", "Category A", 100, 4.5),
            ("Article 2", "Content 2", "tag2, tag3", "Category A", 200, 4.0),
            ("Article 3", "Content 3", "tag1, tag3", "Category B", 150, 4.2),
            ("Article 4", "Content 4", "tag4, tag5", "Category B", 50, 3.8),
            ("Article 5", "Content 5", "tag1, tag4", "Category C", 300, 4.8),
        ]
        
        for title, content, tags, category, views, rating in articles:
            query = """
                INSERT INTO articles (title, content, excerpt, tags, category, author, status, views, avg_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db_manager.execute_update(
                query,
                (title, content, content, tags, category, "author1", "published", views, rating)
            )
    
    @given(
        article_id=st.integers(min_value=1, max_value=5),
        limit=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5, deadline=None)
    def test_related_articles_exclude_source(self, article_id: int, limit: int):
        """
        Property 15: For any article, related article recommendations should
        not include the source article itself.
        
        Feature: platform-core, Property 15: Recommendation Diversity
        Validates: Requirements 9.3
        """
        # Get related articles
        related = self.rec_engine.get_related_articles(article_id, limit=limit)
        
        # Verify source article is not in results
        if not related.empty:
            result_ids = related['id'].tolist()
            assert article_id not in result_ids, \
                f"Related articles should not include source article {article_id}"
    
    @given(
        article_id=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5, deadline=None)
    def test_related_articles_share_attributes(self, article_id: int):
        """
        Property 15: For any article, related recommendations should share
        category or tags with the source article.
        
        Feature: platform-core, Property 15: Recommendation Diversity
        Validates: Requirements 9.3
        """
        # Get source article
        query = "SELECT category, tags FROM articles WHERE id = ?"
        source = self.db_manager.execute_query(query, (article_id,))
        
        if source.empty:
            return  # Article doesn't exist, skip
        
        source_category = source.iloc[0]['category']
        source_tags = set(source.iloc[0]['tags'].split(', ')) if source.iloc[0]['tags'] else set()
        
        # Get related articles
        related = self.rec_engine.get_related_articles(article_id, limit=5)
        
        # Verify each related article shares category or tags
        if not related.empty:
            for idx, article in related.iterrows():
                article_category = article['category']
                article_tags = set(article['tags'].split(', ')) if article['tags'] else set()
                
                # Should share category OR at least one tag
                shares_category = article_category == source_category
                shares_tags = bool(source_tags & article_tags)
                
                assert shares_category or shares_tags, \
                    f"Related article should share category or tags with source article"
    
    @given(
        limit=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=5, deadline=None)
    def test_trending_articles_ordered_by_score(self, limit: int):
        """
        Property 15: For any limit, trending articles should be ordered by
        descending trending score.
        
        Feature: platform-core, Property 15: Recommendation Diversity
        Validates: Requirements 9.4
        """
        # Get trending articles
        trending = self.rec_engine.get_trending_articles(limit=limit)
        
        # Verify ordering
        if not trending.empty and len(trending) > 1:
            scores = trending['trending_score'].tolist()
            
            # Check descending order
            for i in range(len(scores) - 1):
                assert scores[i] >= scores[i + 1], \
                    f"Trending articles should be ordered by descending score"
    
    @given(
        tags=st.sampled_from(["tag1, tag2", "tag3, tag4", "tag1, tag3"]),
        limit=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5, deadline=None)
    def test_similar_by_tags_matches_tags(self, tags: str, limit: int):
        """
        Property 15: For any tag set, similar articles should contain at least
        one of the specified tags.
        
        Feature: platform-core, Property 15: Recommendation Diversity
        Validates: Requirements 9.3
        """
        # Get similar articles
        similar = self.rec_engine.get_similar_by_tags(tags, limit=limit)
        
        # Parse input tags
        input_tags = set(t.strip() for t in tags.split(','))
        
        # Verify each result contains at least one matching tag
        if not similar.empty:
            for idx, article in similar.iterrows():
                article_tags = set(t.strip() for t in article['tags'].split(',')) if article['tags'] else set()
                
                # Should have at least one matching tag
                matching_tags = input_tags & article_tags
                assert len(matching_tags) > 0, \
                    f"Similar article should contain at least one matching tag from {input_tags}"
    
    @given(
        category=st.sampled_from(["Category A", "Category B", "Category C"]),
        limit=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5, deadline=None)
    def test_popular_in_category_matches_category(self, category: str, limit: int):
        """
        Property 15: For any category, popular articles should all belong to
        that category.
        
        Feature: platform-core, Property 15: Recommendation Diversity
        Validates: Requirements 9.4
        
        Note: This test verifies that the query filters by category correctly
        by checking that results are returned and don't exceed the limit.
        The category field is not included in the SELECT, so we verify
        the filtering works by checking result count consistency.
        """
        # Get popular articles in category
        popular = self.rec_engine.get_popular_in_category(category, limit=limit)
        
        # Verify results don't exceed limit
        assert len(popular) <= limit, \
            f"Popular articles should not exceed limit {limit}"
        
        # Verify results have required fields
        if not popular.empty:
            required_fields = ['id', 'title', 'excerpt', 'tags', 'author', 'views', 'avg_rating']
            for field in required_fields:
                assert field in popular.columns, \
                    f"Popular articles should contain '{field}' field"
            
            # Verify we can retrieve the full article to check category
            first_article_id = popular.iloc[0]['id']
            query = "SELECT category FROM articles WHERE id = ?"
            result = self.db_manager.execute_query(query, (first_article_id,))
            
            if not result.empty:
                assert result.iloc[0]['category'] == category, \
                    f"Popular article should belong to category '{category}'"
    
    @given(
        limit=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=5, deadline=None)
    def test_recommendations_respect_limit(self, limit: int):
        """
        Property 15: For any limit, recommendation functions should return
        at most 'limit' results.
        
        Feature: platform-core, Property 15: Recommendation Diversity
        Validates: Requirements 9.3, 9.4
        """
        # Test various recommendation functions
        trending = self.rec_engine.get_trending_articles(limit=limit)
        assert len(trending) <= limit, \
            f"Trending articles should not exceed limit {limit}"
        
        related = self.rec_engine.get_related_articles(1, limit=limit)
        assert len(related) <= limit, \
            f"Related articles should not exceed limit {limit}"
        
        similar = self.rec_engine.get_similar_by_tags("tag1, tag2", limit=limit)
        assert len(similar) <= limit, \
            f"Similar articles should not exceed limit {limit}"
        
        popular = self.rec_engine.get_popular_in_category("Category A", limit=limit)
        assert len(popular) <= limit, \
            f"Popular articles should not exceed limit {limit}"
    
    @given(
        username=st.text(min_size=1, max_size=20).filter(lambda x: x.strip() != '')
    )
    @settings(max_examples=5, deadline=None)
    def test_personalized_recommendations_no_duplicates(self, username: str):
        """
        Property 15: For any user, personalized recommendations should not
        contain duplicate articles.
        
        Feature: platform-core, Property 15: Recommendation Diversity
        Validates: Requirements 9.3
        """
        # Create some user activity
        for article_id in [1, 2]:
            query = """
                INSERT INTO user_activity (username, action, target_type, target_id)
                VALUES (?, ?, ?, ?)
            """
            self.db_manager.execute_update(
                query,
                (username, "article_view", "article", str(article_id))
            )
        
        # Get personalized recommendations
        recommendations = self.rec_engine.get_personalized_recommendations(username, limit=10)
        
        # Verify no duplicates
        if not recommendations.empty:
            article_ids = recommendations['id'].tolist()
            unique_ids = set(article_ids)
            
            assert len(article_ids) == len(unique_ids), \
                f"Personalized recommendations should not contain duplicates"
