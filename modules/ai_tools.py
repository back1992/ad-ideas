"""
Agent tools for the Pydantic AI advertising history tutor.

Each tool wraps an existing platform module (search, recommendations, database)
and returns a formatted string for the LLM to reason over.

Usage:
    from modules.ai_tools import register_tools
    register_tools(agent, db_manager)
"""

import pandas as pd
from typing import Callable
import time


# Simple in-memory cache with TTL
_tool_cache = {}
_cache_ttl = {
    'search_articles': 300,  # 5 minutes
    'get_article_detail': 600,  # 10 minutes
    'get_recommendations': 300,  # 5 minutes
    'get_trending_articles': 120,  # 2 minutes
    'get_articles_by_category': 300,  # 5 minutes
}


def _get_cached(tool_name, key, func, *args, **kwargs):
    """Get cached result or compute and cache it."""
    cache_key = f"{tool_name}:{key}"
    now = time.time()
    
    if cache_key in _tool_cache:
        result, timestamp = _tool_cache[cache_key]
        ttl = _cache_ttl.get(tool_name, 300)
        if now - timestamp < ttl:
            return result
    
    # Compute and cache
    result = func(*args, **kwargs)
    _tool_cache[cache_key] = (result, now)
    return result


def _format_article_row(row: pd.Series) -> str:
    """Format a single article row into a readable text block."""
    parts = [f"[ID:{row['id']}] {row['title']}"]
    if row.get('category'):
        parts.append(f"  分类: {row['category']}")
    if row.get('tags'):
        parts.append(f"  标签: {row['tags']}")
    if row.get('excerpt'):
        parts.append(f"  摘要: {row['excerpt'][:150]}")
    if row.get('author'):
        parts.append(f"  作者: {row['author']}")
    if row.get('views') is not None:
        parts.append(f"  浏览: {row['views']}  评分: {row.get('avg_rating', 0):.1f}")
    return "\n".join(parts)


def _format_articles_df(df: pd.DataFrame, header: str = "") -> str:
    """Format a DataFrame of articles into readable text."""
    if df.empty:
        return f"{header}\n（未找到相关文章）" if header else "（未找到相关文章）"
    lines = [header] if header else []
    for _, row in df.iterrows():
        lines.append(_format_article_row(row))
        lines.append("")
    return "\n".join(lines)


def register_tools(agent, db_manager) -> None:
    """Register platform tools on a Pydantic AI agent.

    Args:
        agent: A pydantic_ai.Agent instance.
        db_manager: A DatabaseManager instance for data access.
    """
    from modules.search import SearchSystem
    from modules.recommendations import RecommendationEngine

    search_system = SearchSystem(db_manager)
    rec_engine = RecommendationEngine(db_manager)

    @agent.tool_plain
    def search_articles(query: str, limit: int = 5) -> str:
        """搜索平台上的广告学文章。返回匹配的文章标题、摘要和分类。

        Args:
            query: 搜索关键词（中文或英文均可）
            limit: 返回结果数量上限
        """
        def _do_search():
            results = search_system.search(query, content_types=['articles'], limit=limit)
            articles = results.get('articles', pd.DataFrame())
            return _format_articles_df(articles, header=f"搜索结果（关键词: {query}）:")
        
        return _get_cached('search_articles', f"{query}:{limit}", _do_search)

    @agent.tool_plain
    def get_article_detail(article_id: int) -> str:
        """根据文章ID获取文章全文内容。

        Args:
            article_id: 文章ID
        """
        def _do_get():
            row = db_manager.execute_query(
                "SELECT id, title, content, excerpt, category, tags, author, views, avg_rating "
                "FROM articles WHERE id = ? AND status = 'published'",
                (article_id,)
            )
            if row.empty:
                return f"未找到ID为 {article_id} 的文章。"
            article = row.iloc[0]
            parts = [
                f"标题: {article['title']}",
                f"分类: {article.get('category', '未分类')}",
                f"标签: {article.get('tags', '无')}",
                f"作者: {article['author']}",
                f"浏览: {article['views']}  评分: {article.get('avg_rating', 0):.1f}",
                "",
                "--- 正文 ---",
                article['content'],
            ]
            return "\n".join(parts)
        
        return _get_cached('get_article_detail', str(article_id), _do_get)

    @agent.tool_plain
    def get_recommendations(topic: str, limit: int = 5) -> str:
        """根据主题或标签获取相关文章推荐。

        Args:
            topic: 主题关键词或逗号分隔的标签
            limit: 返回结果数量上限
        """
        def _do_rec():
            articles = rec_engine.get_similar_by_tags(topic, limit=limit)
            return _format_articles_df(articles, header=f"推荐文章（主题: {topic}）:")
        
        return _get_cached('get_recommendations', f"{topic}:{limit}", _do_rec)

    @agent.tool_plain
    def get_trending_articles(limit: int = 5) -> str:
        """获取当前最受欢迎的文章（按浏览量和评分排序）。

        Args:
            limit: 返回结果数量上限
        """
        def _do_trending():
            articles = rec_engine.get_trending_articles(limit=limit)
            return _format_articles_df(articles, header="热门文章:")
        
        return _get_cached('get_trending_articles', str(limit), _do_trending)

    @agent.tool_plain
    def get_articles_by_category(category: str, limit: int = 5) -> str:
        """按分类浏览文章。可用分类包括广告理论、广告历史、经典案例等。

        Args:
            category: 文章分类名称
            limit: 返回结果数量上限
        """
        def _do_cat():
            articles = rec_engine.get_popular_in_category(category, limit=limit)
            return _format_articles_df(articles, header=f"分类「{category}」下的文章:")
        
        return _get_cached('get_articles_by_category', f"{category}:{limit}", _do_cat)
