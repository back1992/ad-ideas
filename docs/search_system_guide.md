# Search System Guide

## Overview

The 广告思想简史 platform includes a comprehensive search and recommendation system that helps users discover content across articles, comments, and other platform content.

## Features

### 1. Full-Text Search

**Location:** Navigate to "🔍 搜索 / Search" in the main menu

**Capabilities:**
- Search across article titles, content, excerpts, tags, and categories
- Search through comments and discussions
- Relevance-based ranking
- Result highlighting showing matched content
- Filter by content type (articles, comments, or all)

**How It Works:**
- Enter keywords in the search box
- Select content types to search
- Click "Search" or press Enter
- Results are ranked by relevance score
- Matched text is highlighted in results

### 2. Content Recommendations

**Popular Content:**
- Trending articles based on views, ratings, and recent activity
- Most discussed articles with active comment threads
- Engagement metrics displayed for each item

**Related Content:**
- Articles in the same category
- Articles with similar tags
- Other articles by the same author
- Popular articles in the same category

**Personalized Recommendations:**
- Based on your viewing history
- Considers your preferred categories
- Adapts to your interaction patterns

## Search Tips

### Effective Search Queries

**Good Examples:**
- `digital marketing` - Finds articles about digital marketing
- `Nike campaigns` - Finds content mentioning Nike campaigns
- `consumer behavior` - Finds articles about consumer psychology

**Search Operators:**
- Multiple words: Searches for content containing any of the words
- Exact phrases: Use quotes for exact matches (future enhancement)

### Content Type Filters

- **Articles Only:** Best for finding in-depth content
- **Comments Only:** Find discussions and user opinions
- **All Content:** Comprehensive search across everything

## Recommendation Algorithm

### Relevance Scoring

Articles are scored based on:
- **Title Match:** 10 points
- **Tags Match:** 7 points  
- **Excerpt Match:** 5 points
- **Category Match:** 4 points
- **Content Match:** 3 points

### Trending Score

Trending articles are calculated using:
- Views (30% weight)
- Average rating (weighted by 10)
- Total feedback (weighted by 5)
- Recent activity (weighted by 2)

### Personalization

Recommendations consider:
- Your recently viewed articles
- Your preferred categories (top 3)
- Your frequently viewed tags (top 5)
- Article quality metrics (rating, views)

## API Reference

### SearchSystem Class

```python
from modules.search import get_search_system

# Initialize
search_system = get_search_system(db_manager)

# Perform search
results = search_system.search(
    query="marketing",
    content_types=['articles', 'comments'],
    limit=50
)

# Display search interface (Streamlit)
search_system.display_search_interface()
```

### RecommendationEngine Class

```python
from modules.recommendations import get_recommendation_engine

# Initialize
rec_engine = get_recommendation_engine(db_manager)

# Get related articles
related = rec_engine.get_related_articles(article_id=1, limit=5)

# Get personalized recommendations
personalized = rec_engine.get_personalized_recommendations(
    username="student",
    limit=10
)

# Get trending articles
trending = rec_engine.get_trending_articles(limit=10, days=7)
```

## Testing

### Manual Testing

1. **Create Test Data:**
   ```bash
   python create_test_data.py
   ```

2. **Run Search Tests:**
   ```bash
   python test_search_manual.py
   ```

3. **Test in UI:**
   ```bash
   streamlit run streamlit_app.py
   ```
   - Login with any account
   - Navigate to "🔍 搜索 / Search"
   - Try various search queries

### Expected Behavior

- Empty searches show info message
- No results show helpful message
- Results display with relevance scores
- Recommendations update based on content
- Popular content shows engagement metrics

## Performance Considerations

### Database Queries

- Search uses LIKE queries with relevance scoring
- Indexes recommended for large datasets:
  - `CREATE INDEX idx_articles_title ON articles(title)`
  - `CREATE INDEX idx_articles_tags ON articles(tags)`
  - `CREATE INDEX idx_comments_content ON comments(content)`

### Caching

- Search results are not cached (always fresh)
- Recommendation engine queries are optimized
- Consider caching trending articles for high-traffic sites

### Scalability

For large datasets (>10,000 articles):
- Consider full-text search engine (Elasticsearch, Meilisearch)
- Implement pagination for search results
- Add search result caching
- Use database indexes

## Future Enhancements

Potential improvements:
- [ ] Advanced search operators (AND, OR, NOT)
- [ ] Exact phrase matching with quotes
- [ ] Search filters (date range, author, category)
- [ ] Search history and saved searches
- [ ] Auto-complete suggestions
- [ ] Search analytics and popular queries
- [ ] Fuzzy matching for typos
- [ ] Multi-language search support

## Troubleshooting

### No Search Results

**Problem:** Search returns no results

**Solutions:**
1. Check if articles are published (status = 'published')
2. Verify database has content
3. Try broader search terms
4. Check content type filters

### Slow Search Performance

**Problem:** Search takes too long

**Solutions:**
1. Add database indexes
2. Reduce search limit
3. Optimize database queries
4. Consider search engine integration

### Recommendations Not Showing

**Problem:** No recommendations displayed

**Solutions:**
1. Ensure articles exist in database
2. Check article status (must be published)
3. Verify user has activity history
4. Check database connections

## Support

For issues or questions:
- Check the main README.md
- Review test scripts for examples
- Examine module source code
- Contact platform administrators
