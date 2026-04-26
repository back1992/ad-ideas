"""
Content Recommendation System for 广告思想简史 Platform

This module provides content recommendation functionality including
related articles, personalized suggestions, and trending content.
"""

import logging
from utils.logger import create_logger
import pandas as pd
from typing import Optional, List, Dict, Any
from modules.database import DatabaseManager


def _safe_like(tag: str) -> str:
    """Sanitize a tag for safe interpolation into a LIKE pattern."""
    return tag.replace("'", "''")


class RecommendationEngine:
    """
    Content recommendation engine for personalized content discovery.

    Provides related content suggestions, trending articles, and
    personalized recommendations based on user activity and preferences.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize RecommendationEngine with database manager.

        Args:
            db_manager: Database manager instance for data access
        """
        self.db_manager = db_manager
        self.logger = create_logger('RecommendationEngine')


    def get_related_articles(self, article_id: int, limit: int = 5) -> pd.DataFrame:
        """
        Get articles related to a specific article based on category and tags.

        Args:
            article_id: Article ID to find related content for
            limit: Maximum number of recommendations

        Returns:
            pd.DataFrame: Related articles with relevance scores
        """
        try:
            query = "SELECT category, tags FROM articles WHERE id = ?"
            source = self.db_manager.execute_query(query, (article_id,))

            if source.empty:
                return pd.DataFrame()

            category = source.iloc[0]['category']
            tags = source.iloc[0]['tags']

            if tags:
                tag_list = [t.strip() for t in tags.split(',')]
                tag_patterns = ' OR '.join(
                    [f"tags LIKE '%{_safe_like(tag)}%'" for tag in tag_list]
                )

                query = f"""
                    SELECT
                        id,
                        title,
                        excerpt,
                        category,
                        tags,
                        author,
                        views,
                        avg_rating,
                        (
                            CASE WHEN category = ? THEN 5 ELSE 0 END +
                            CASE WHEN ({tag_patterns}) THEN 3 ELSE 0 END
                        ) as relevance_score
                    FROM articles
                    WHERE
                        status = 'published' AND
                        id != ? AND
                        (category = ? OR ({tag_patterns}))
                    ORDER BY relevance_score DESC, avg_rating DESC, views DESC
                    LIMIT ?
                """
                params = (category, article_id, category, limit)
            else:
                query = """
                    SELECT
                        id,
                        title,
                        excerpt,
                        category,
                        tags,
                        author,
                        views,
                        avg_rating,
                        5 as relevance_score
                    FROM articles
                    WHERE
                        status = 'published' AND
                        id != ? AND
                        category = ?
                    ORDER BY avg_rating DESC, views DESC
                    LIMIT ?
                """
                params = (article_id, category, limit)

            return self.db_manager.execute_query(query, params)

        except Exception as e:
            self.logger.error(f"Error getting related articles: {e}")
            return pd.DataFrame()

    def get_personalized_recommendations(self, username: str, limit: int = 10) -> pd.DataFrame:
        """
        Get personalized article recommendations based on user activity.

        Args:
            username: Username to get recommendations for
            limit: Maximum number of recommendations

        Returns:
            pd.DataFrame: Recommended articles
        """
        try:
            query = """
                SELECT DISTINCT target_id
                FROM user_activity
                WHERE username = ? AND target_type = 'article'
                ORDER BY timestamp DESC
                LIMIT 5
            """
            history = self.db_manager.execute_query(query, (username,))

            if history.empty:
                return self.get_trending_articles(limit)

            viewed_ids = [int(id) for id in history['target_id']]
            placeholders = ','.join(['?'] * len(viewed_ids))

            query = f"SELECT category, tags FROM articles WHERE id IN ({placeholders})"
            viewed_articles = self.db_manager.execute_query(query, tuple(viewed_ids))

            if viewed_articles.empty:
                return self.get_trending_articles(limit)

            categories = viewed_articles['category'].value_counts().head(3).index.tolist()
            all_tags = []
            for tags in viewed_articles['tags'].dropna():
                all_tags.extend([t.strip() for t in tags.split(',')])

            preferred_tags = pd.Series(all_tags).value_counts().head(5).index.tolist() if all_tags else []

            # Fetch all published articles and score in Python to avoid SQL injection
            query = """
                SELECT id, title, excerpt, category, tags, author, views, avg_rating, total_feedback
                FROM articles
                WHERE status = 'published' AND id NOT IN ({})
            """.format(placeholders)

            params = tuple(viewed_ids)
            candidates = self.db_manager.execute_query(query, params)

            if candidates.empty:
                return pd.DataFrame()

            def score_article(row):
                score = 0.0
                if row['category'] in categories:
                    score += 5
                if preferred_tags and isinstance(row['tags'], str):
                    row_tags = {t.strip() for t in row['tags'].split(',')}
                    if any(pt in row_tags for pt in preferred_tags):
                        score += 3
                score += (row.get('avg_rating', 0) or 0) * 2
                score += (row.get('views', 0) or 0) / 100.0
                return score

            candidates['recommendation_score'] = candidates.apply(score_article, axis=1)
            return candidates.sort_values('recommendation_score', ascending=False).head(limit)

        except Exception as e:
            self.logger.error(f"Error getting personalized recommendations: {e}")
            return self.get_trending_articles(limit)

    def get_trending_articles(self, limit: int = 10, days: int = 7) -> pd.DataFrame:
        """
        Get trending articles based on recent activity.

        Args:
            limit: Maximum number of articles
            days: Number of days to consider for trending

        Returns:
            pd.DataFrame: Trending articles
        """
        try:
            query = """
                SELECT
                    a.id,
                    a.title,
                    a.excerpt,
                    a.category,
                    a.tags,
                    a.author,
                    a.views,
                    a.avg_rating,
                    a.total_feedback,
                    (
                        a.views * 0.3 +
                        a.avg_rating * 10 +
                        a.total_feedback * 5 +
                        COALESCE(recent_activity.activity_count, 0) * 2
                    ) as trending_score
                FROM articles a
                LEFT JOIN (
                    SELECT
                        target_id,
                        COUNT(*) as activity_count
                    FROM user_activity
                    WHERE
                        target_type = 'article' AND
                        timestamp >= datetime('now', '-' || ? || ' days')
                    GROUP BY target_id
                ) recent_activity ON a.id = CAST(recent_activity.target_id AS INTEGER)
                WHERE a.status = 'published'
                ORDER BY trending_score DESC
                LIMIT ?
            """

            return self.db_manager.execute_query(query, (days, limit))

        except Exception as e:
            self.logger.error(f"Error getting trending articles: {e}")
            return pd.DataFrame()

    def get_similar_by_tags(self, tags: str, exclude_id: Optional[int] = None,
                           limit: int = 5) -> pd.DataFrame:
        """
        Get articles with similar tags.

        Args:
            tags: Comma-separated tags to match
            exclude_id: Article ID to exclude from results
            limit: Maximum number of results

        Returns:
            pd.DataFrame: Articles with matching tags
        """
        try:
            if not tags:
                return pd.DataFrame()

            tag_list = [t.strip() for t in tags.split(',')]
            tag_patterns = ' OR '.join(
                [f"tags LIKE '%{_safe_like(tag)}%'" for tag in tag_list]
            )

            exclude_clause = "AND id != ?" if exclude_id else ""

            query = f"""
                SELECT
                    id,
                    title,
                    excerpt,
                    category,
                    tags,
                    author,
                    views,
                    avg_rating
                FROM articles
                WHERE
                    status = 'published' AND
                    ({tag_patterns})
                    {exclude_clause}
                ORDER BY avg_rating DESC, views DESC
                LIMIT ?
            """

            params = (exclude_id, limit) if exclude_id else (limit,)
            return self.db_manager.execute_query(query, params)

        except Exception as e:
            self.logger.error(f"Error getting similar articles by tags: {e}")
            return pd.DataFrame()

    def get_author_other_articles(self, author: str, exclude_id: Optional[int] = None,
                                  limit: int = 5) -> pd.DataFrame:
        """
        Get other articles by the same author.

        Args:
            author: Author username
            exclude_id: Article ID to exclude
            limit: Maximum number of results

        Returns:
            pd.DataFrame: Other articles by author
        """
        try:
            exclude_clause = "AND id != ?" if exclude_id else ""

            query = f"""
                SELECT
                    id,
                    title,
                    excerpt,
                    category,
                    tags,
                    views,
                    avg_rating,
                    published_at
                FROM articles
                WHERE
                    status = 'published' AND
                    author = ?
                    {exclude_clause}
                ORDER BY published_at DESC
                LIMIT ?
            """

            params = (author, exclude_id, limit) if exclude_id else (author, limit)
            return self.db_manager.execute_query(query, params)

        except Exception as e:
            self.logger.error(f"Error getting author's other articles: {e}")
            return pd.DataFrame()

    def get_popular_in_category(self, category: str, exclude_id: Optional[int] = None,
                                limit: int = 5) -> pd.DataFrame:
        """
        Get popular articles in a specific category.

        Args:
            category: Article category
            exclude_id: Article ID to exclude
            limit: Maximum number of results

        Returns:
            pd.DataFrame: Popular articles in category
        """
        try:
            exclude_clause = "AND id != ?" if exclude_id else ""

            query = f"""
                SELECT
                    id,
                    title,
                    excerpt,
                    tags,
                    author,
                    views,
                    avg_rating,
                    total_feedback
                FROM articles
                WHERE
                    status = 'published' AND
                    category = ?
                    {exclude_clause}
                ORDER BY
                    (views * 0.3 + avg_rating * 10 + total_feedback * 5) DESC
                LIMIT ?
            """

            params = (category, exclude_id, limit) if exclude_id else (category, limit)
            return self.db_manager.execute_query(query, params)

        except Exception as e:
            self.logger.error(f"Error getting popular articles in category: {e}")
            return pd.DataFrame()


# Global recommendation engine instance
_recommendation_engine = None

def get_recommendation_engine(db_manager: DatabaseManager) -> RecommendationEngine:
    """
    Get singleton recommendation engine instance.

    Args:
        db_manager: Database manager instance

    Returns:
        RecommendationEngine: Singleton recommendation engine instance
    """
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine(db_manager)
    return _recommendation_engine
