# Activity Tracking and Analytics System

## Overview

The platform now includes comprehensive activity tracking and analytics capabilities for monitoring user engagement, content performance, and platform growth.

## Components

### 1. Activity Logger (`modules/activity.py`)

The `ActivityLogger` class provides centralized activity tracking across all platform systems.

**Key Features:**
- Privacy-compliant data collection (no sensitive information stored)
- Automatic activity logging for all user actions
- Activity retrieval and filtering
- User engagement metrics
- Data anonymization and deletion for privacy compliance

**Common Activity Types:**
- `login` / `logout` - User authentication
- `feedback_submitted` - User feedback on content
- `comment_posted` / `comment_reply` - Comment activity
- `article_create` / `article_edit` / `article_publish` - Article management
- `content_viewed` - Content viewing
- `moderation_*` - Moderation actions

**Usage Example:**
```python
from modules.activity import get_activity_logger
from modules.database import get_database_manager

db_manager = get_database_manager()
activity_logger = get_activity_logger(db_manager)

# Log an activity
activity_logger.log_activity(
    username='user123',
    action='article_create',
    target_type='article',
    target_id='42',
    details='Created new article'
)

# Get user activity history
user_activity = activity_logger.get_user_activity('user123', limit=50)

# Get activity summary
summary = activity_logger.get_activity_summary(days=7)
```

### 2. Analytics Dashboard (`modules/analytics.py`)

The `AnalyticsDashboard` class provides comprehensive analytics and reporting for administrators.

**Key Features:**
- User engagement statistics
- Content performance metrics
- Platform growth reports
- Interactive visualizations using Plotly
- Customizable time periods (7, 30, 90 days, or all time)

**Dashboard Sections:**

1. **Platform Overview**
   - Active users count
   - Total activities
   - Published articles
   - User engagement metrics

2. **User Engagement Statistics**
   - Most active users
   - Activity distribution by type
   - Daily activity trends
   - Unique user engagement

3. **Content Performance Metrics**
   - Top articles by views
   - Top content by feedback
   - Feedback trends over time
   - Comment activity trends

4. **Platform Growth & Usage Reports**
   - User growth trends
   - Content growth (articles, comments)
   - Engagement rate trends

5. **Detailed Activity Breakdown**
   - Activity types breakdown
   - Detailed activity tables

**Access:**
- Available to administrators only
- Navigate to "📊 平台分析 / Platform Analytics" in the sidebar menu

## Integration

The activity tracking and analytics systems are automatically integrated into the main application:

1. **Activity Logging**: All existing modules (auth, feedback, comments, articles) can use the activity logger
2. **Analytics Dashboard**: Accessible from the main navigation menu for admin users
3. **Database**: Uses the existing `user_activity` table in the SQLite database

## Privacy Compliance

The system implements several privacy-compliant features:

1. **Data Sanitization**: Automatically removes sensitive information (emails, phone numbers) from activity details
2. **Data Truncation**: Limits stored details to 500 characters
3. **Anonymization**: Provides methods to anonymize user data while preserving activity patterns
4. **Data Deletion**: Supports selective or complete deletion of user activity data

**Privacy Methods:**
```python
# Anonymize user data
activity_logger.anonymize_user_data('username')

# Delete old activity data (keep last 90 days)
activity_logger.delete_user_activity('username', days_to_keep=90)

# Delete all activity data for a user
activity_logger.delete_user_activity('username', days_to_keep=0)
```

## Requirements

The analytics system requires the following additional dependency:
- `plotly==5.24.1` - For interactive data visualizations

This has been added to `requirements.txt`.

## Future Enhancements

Potential future improvements:
- Export analytics reports to PDF/Excel
- Email notifications for key metrics
- Custom dashboard widgets
- Real-time activity monitoring
- Advanced filtering and search
- Comparative analytics (period-over-period)
