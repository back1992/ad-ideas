# Feedback System Integration Guide

## Overview

The FeedbackSystem provides comprehensive feedback collection and management for the 广告思想简史 platform using the `streamlit-feedback` component with database integration.

## Features

- **Multiple Feedback Types**: Thumbs up/down, star ratings (1-5), and emoji faces
- **Database Integration**: Persistent storage with SQLite
- **Real-time Statistics**: Automatic aggregation and display of feedback metrics
- **User Management**: Prevents duplicate feedback and tracks user activity
- **Display Components**: Pre-built UI components for different use cases

## Quick Start

### 1. Basic Setup

```python
from modules.database import get_database_manager
from modules.feedback import get_feedback_system

# Initialize systems
db_manager = get_database_manager()
feedback_system = get_feedback_system(db_manager)
```

### 2. Collect Feedback

```python
# Simple thumbs up/down feedback
feedback = feedback_system.collect_feedback(
    target_type="timeline",
    target_id="content_123",
    feedback_type="thumbs"
)

# Star rating feedback
feedback = feedback_system.collect_feedback(
    target_type="article", 
    target_id="article_456",
    feedback_type="stars",
    optional_text_label="Please share your thoughts"
)
```

### 3. Display Statistics

```python
# Show feedback statistics
feedback_system.show_feedback_stats("timeline", "content_123")

# Get raw statistics data
stats = feedback_system.get_feedback_stats("timeline", "content_123")
print(f"Total feedback: {stats['total_feedback']}")
print(f"Average rating: {stats['avg_rating']}")
```

## Advanced Usage

### Display Components

```python
from modules.feedback import get_feedback_display_components

display_components = get_feedback_display_components(feedback_system)

# Compact stats for content lists
display_components.display_compact_stats("timeline", "content_123")

# Trending content
display_components.display_trending_content(limit=10)

# User feedback summary
display_components.display_user_feedback_summary("username")
```

### Content Types

The system supports different content types:

- `"timeline"` - Historical timeline content
- `"figures"` - Advertising industry figures
- `"campaigns"` - Famous advertising campaigns  
- `"articles"` - User-generated articles
- Custom types as needed

### Feedback Types

- `"thumbs"` - Binary like/dislike (values: 0 or 1) - Uses streamlit-feedback
- `"stars"` - 5-star rating (values: 0-4, displayed as 1-5 stars) - Uses Streamlit's built-in st.feedback
- `"faces"` - Emoji sentiment (values: 0-4, from sad to happy) - Uses streamlit-feedback

## Database Schema

### user_feedback Table

```sql
CREATE TABLE user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL,
    feedback_value INTEGER,
    feedback_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT
);
```

### content_stats Table

```sql
CREATE TABLE content_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    thumbs_up INTEGER DEFAULT 0,
    thumbs_down INTEGER DEFAULT 0,
    avg_stars REAL DEFAULT 0.0,
    total_ratings INTEGER DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(target_type, target_id)
);
```

## Integration Examples

### In Content Pages

```python
def show_content_with_feedback():
    st.title("Content Title")
    
    # Your content here
    st.markdown("Content goes here...")
    
    # Add feedback section
    st.markdown("---")
    st.markdown("### Your Feedback")
    
    feedback_system.collect_feedback(
        target_type="timeline",
        target_id="unique_content_id",
        feedback_type="thumbs"
    )
```

### In Content Lists

```python
def show_content_list():
    for content_item in content_list:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(content_item['title'])
        
        with col2:
            display_components.display_compact_stats(
                content_item['type'], 
                content_item['id']
            )
```

## Best Practices

1. **Unique Content IDs**: Use consistent, unique identifiers for content
2. **User Authentication**: Always check if user is logged in before collecting feedback
3. **Error Handling**: The system includes comprehensive error handling and logging
4. **Performance**: Statistics are cached in the content_stats table for fast retrieval
5. **User Experience**: Prevent duplicate feedback and provide clear feedback to users

## API Reference

### FeedbackSystem Methods

- `collect_feedback(target_type, target_id, feedback_type, optional_text_label)` - Collect user feedback
- `save_feedback(username, target_type, target_id, feedback_type, feedback_value, feedback_text)` - Save feedback to database
- `has_user_feedback(username, target_type, target_id)` - Check if user has provided feedback
- `get_feedback_stats(target_type, target_id)` - Get aggregated statistics
- `show_feedback_stats(target_type, target_id)` - Display statistics in UI
- `update_content_stats(target_type, target_id)` - Update cached statistics
- `get_user_feedback_history(username, limit)` - Get user's feedback history
- `get_popular_content(target_type, limit)` - Get popular content by feedback

### FeedbackDisplayComponents Methods

- `display_thumbs_feedback(target_type, target_id, show_collection)` - Thumbs feedback UI
- `display_stars_feedback(target_type, target_id, show_collection)` - Star rating UI
- `display_faces_feedback(target_type, target_id, show_collection)` - Emoji faces UI
- `display_compact_stats(target_type, target_id)` - Compact statistics display
- `display_trending_content(target_type, limit)` - Trending content display
- `display_user_feedback_summary(username)` - User feedback activity summary

## Troubleshooting

### Common Issues

1. **Module Import Error**: Ensure `streamlit-feedback==0.1.4` is installed
2. **Database Errors**: Check that database is initialized with `db_manager.init_database()`
3. **Authentication Issues**: Verify user is logged in before collecting feedback
4. **Duplicate Feedback**: System automatically prevents duplicate feedback per user

### Logging

The system includes comprehensive logging. Check logs for detailed error information:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Examples

See `examples/feedback_usage_example.py` for complete working examples of all feedback system features.