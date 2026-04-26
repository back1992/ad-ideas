# Comment System Guide

## Overview

The Comment System provides comprehensive discussion and interaction functionality for the 广告思想简史 platform. It includes comment submission, threading, likes, reporting, and full moderation capabilities.

## Features

### Core Features
- ✅ Comment submission with user attribution
- ✅ Threaded replies (up to 3 levels deep)
- ✅ Like/dislike functionality
- ✅ Comment reporting for moderation
- ✅ User avatar generation
- ✅ Timestamp formatting (relative and absolute)

### Moderation Features
- ✅ Moderation queue for reported comments
- ✅ Approve/reject comment functionality
- ✅ Comment editing by administrators
- ✅ Comment removal
- ✅ Comprehensive activity logging
- ✅ Multiple moderation views (reported, pending, all)

## Architecture

### Components

1. **CommentSystem**: Main class for comment functionality
   - Comment submission and display
   - Threading and replies
   - User interactions (likes, reports)
   - Avatar generation

2. **CommentModerationSystem**: Administrative moderation tools
   - Moderation queue management
   - Comment approval/rejection
   - Content editing and removal
   - Activity logging

## Usage

### Basic Comment Display

```python
from modules.database import get_database_manager
from modules.comments import get_comment_system

# Initialize
db_manager = get_database_manager("platform.db")
comment_system = get_comment_system(db_manager)

# Display comments section (includes input and existing comments)
comment_system.display_comments_section(
    target_type="article",
    target_id="article_123"
)
```

### Adding Comments Programmatically

```python
# Add a top-level comment
success = comment_system.add_comment(
    username="john_doe",
    target_type="timeline",
    target_id="1920s",
    content="Great historical overview!",
    parent_id=None  # None for top-level
)

# Add a reply to a comment
success = comment_system.add_comment(
    username="jane_smith",
    target_type="timeline",
    target_id="1920s",
    content="I agree!",
    parent_id=5  # ID of parent comment
)
```

### Retrieving Comments

```python
# Get all approved comments
comments = comment_system.get_comments(
    target_type="figures",
    target_id="david_ogilvy",
    approved_only=True
)

# Get all comments (including unapproved)
all_comments = comment_system.get_comments(
    target_type="figures",
    target_id="david_ogilvy",
    approved_only=False
)
```

### User Interactions

```python
# Like a comment
success = comment_system.like_comment(
    comment_id=42,
    username="user123"
)

# Report a comment
success = comment_system.report_comment(
    comment_id=42,
    reporter_username="user456",
    reason="Inappropriate content"
)

# Generate user avatar
avatar = comment_system.generate_user_avatar("john_doe")
# Returns: "👨‍💼" (consistent emoji based on username)
```

### Moderation Interface

```python
from modules.comments import get_comment_moderation_system

# Initialize moderation system
mod_system = get_comment_moderation_system(comment_system)

# Display full moderation interface
mod_system.display_moderation_queue(admin_username="admin")

# Get reported comments
reported = mod_system.get_reported_comments()

# Approve a comment
success = mod_system.approve_comment(
    comment_id=42,
    admin_username="admin"
)

# Reject and remove a comment
success = mod_system.reject_comment(
    comment_id=43,
    admin_username="admin"
)

# Edit a comment
success = mod_system.edit_comment(
    comment_id=44,
    new_content="Edited content",
    admin_username="admin"
)

# Remove a comment
success = mod_system.remove_comment(
    comment_id=45,
    admin_username="admin"
)
```

## Database Schema

### Comments Table

```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    likes INTEGER DEFAULT 0,
    parent_id INTEGER,
    is_approved BOOLEAN DEFAULT 1,
    FOREIGN KEY (parent_id) REFERENCES comments (id)
);
```

### Fields

- **id**: Unique comment identifier
- **username**: User who posted the comment
- **target_type**: Type of content (timeline, figures, campaigns, article)
- **target_id**: Specific content identifier
- **content**: Comment text (max 2000 characters)
- **timestamp**: When comment was posted
- **likes**: Number of likes received
- **parent_id**: ID of parent comment (NULL for top-level)
- **is_approved**: Approval status (1=approved, 0=pending)

## Integration with Streamlit

### Page Integration

```python
import streamlit as st
from modules.comments import get_comment_system
from modules.database import get_database_manager

def article_page():
    st.title("Article Title")
    
    # Article content
    st.markdown("Article content here...")
    
    # Comments section
    db_manager = get_database_manager()
    comment_system = get_comment_system(db_manager)
    
    comment_system.display_comments_section(
        target_type="article",
        target_id="article_123"
    )
```

### Admin Moderation Page

```python
import streamlit as st
from modules.auth import get_auth_manager
from modules.comments import get_comment_system, get_comment_moderation_system
from modules.database import get_database_manager

def moderation_page():
    auth_manager = get_auth_manager()
    username = st.session_state.get('username')
    
    # Check admin privileges
    if not auth_manager.is_admin(username):
        st.error("Access denied. Admin privileges required.")
        return
    
    # Display moderation interface
    db_manager = get_database_manager()
    comment_system = get_comment_system(db_manager)
    mod_system = get_comment_moderation_system(comment_system)
    
    mod_system.display_moderation_queue(username)
```

## Best Practices

### 1. Always Check Authentication

```python
username = st.session_state.get('username')
if not username:
    st.warning("Please log in to comment")
    return
```

### 2. Handle Errors Gracefully

```python
try:
    success = comment_system.add_comment(...)
    if success:
        st.success("Comment posted!")
    else:
        st.error("Failed to post comment")
except Exception as e:
    st.error(f"An error occurred: {e}")
```

### 3. Use Rerun After State Changes

```python
if st.button("Like"):
    comment_system.like_comment(comment_id, username)
    st.rerun()  # Refresh to show updated like count
```

### 4. Limit Threading Depth

The system automatically limits threading to 3 levels to maintain readability:
- Level 0: Top-level comments
- Level 1: Direct replies
- Level 2: Replies to replies
- Level 3: Maximum depth (no further nesting)

### 5. Validate User Permissions

```python
# Only allow comment author or admin to edit
if username == comment['username'] or auth_manager.is_admin(username):
    # Allow edit
    pass
else:
    st.error("You don't have permission to edit this comment")
```

## Customization

### Custom Avatar System

You can customize the avatar generation by modifying the `generate_user_avatar` method:

```python
def generate_user_avatar(self, username: str) -> str:
    # Custom implementation
    # Could use: initials, profile pictures, custom emojis, etc.
    initials = ''.join([c[0].upper() for c in username.split('_')])
    return f"[{initials}]"
```

### Custom Comment Display

```python
def custom_comment_card(comment):
    """Custom comment display format"""
    with st.container():
        st.markdown(f"**{comment['username']}** · {comment['timestamp']}")
        st.markdown(comment['content'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"👍 {comment['likes']}")
        with col2:
            st.button("Reply", key=f"reply_{comment['id']}")
        with col3:
            st.button("Report", key=f"report_{comment['id']}")
```

## Performance Considerations

### 1. Pagination for Large Comment Threads

For content with many comments, consider implementing pagination:

```python
def get_comments_paginated(target_type, target_id, page=1, per_page=20):
    offset = (page - 1) * per_page
    query = """
        SELECT * FROM comments 
        WHERE target_type = ? AND target_id = ? AND is_approved = 1
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    """
    return db_manager.execute_query(query, (target_type, target_id, per_page, offset))
```

### 2. Caching Comment Counts

```python
@st.cache_data(ttl=60)
def get_comment_count(target_type, target_id):
    query = """
        SELECT COUNT(*) as count FROM comments 
        WHERE target_type = ? AND target_id = ? AND is_approved = 1
    """
    result = db_manager.execute_query(query, (target_type, target_id))
    return result.iloc[0]['count']
```

### 3. Batch Operations

For moderation of multiple comments:

```python
def approve_multiple_comments(comment_ids, admin_username):
    query = "UPDATE comments SET is_approved = 1 WHERE id IN ({})".format(
        ','.join('?' * len(comment_ids))
    )
    return db_manager.execute_update(query, tuple(comment_ids))
```

## Troubleshooting

### Issue: Foreign Key Constraint Failed

**Problem**: Error when adding replies to comments.

**Solution**: Ensure parent comment exists and foreign keys are enabled:

```python
# Check if parent exists
parent_comment = comment_system.get_comments(...)
if parent_comment.empty:
    st.error("Parent comment not found")
    return
```

### Issue: Comments Not Displaying

**Problem**: Comments added but not showing up.

**Solution**: Check approval status:

```python
# Get all comments including unapproved
comments = comment_system.get_comments(
    target_type="article",
    target_id="123",
    approved_only=False  # Set to False to see all
)
```

### Issue: Session State Issues with Replies

**Problem**: Reply input not showing or persisting.

**Solution**: Use unique keys and clear state properly:

```python
# Clear reply state after posting
if st.button("Post Reply"):
    # Post comment
    st.session_state[f'replying_to_{comment_id}'] = False
    st.rerun()
```

## Security Considerations

1. **Input Validation**: All comment content is validated (max 2000 chars)
2. **SQL Injection Prevention**: Parameterized queries used throughout
3. **XSS Protection**: Content should be escaped when displayed (Streamlit handles this)
4. **Permission Checks**: Always verify user permissions before moderation actions
5. **Activity Logging**: All moderation actions are logged for audit purposes

## Future Enhancements

Potential improvements for future versions:

- [ ] Comment editing by original author (with edit history)
- [ ] Comment voting (upvote/downvote instead of just likes)
- [ ] Nested reply notifications
- [ ] Comment search functionality
- [ ] Rich text formatting (markdown support)
- [ ] File attachments
- [ ] Comment reactions (beyond likes)
- [ ] User mention system (@username)
- [ ] Comment sorting options (newest, oldest, most liked)
- [ ] Comment pinning by moderators

## Support

For issues or questions about the comment system:

1. Check this documentation
2. Review the example code in `examples/comment_usage_example.py`
3. Check the requirements in `.kiro/specs/platform-core/requirements.md`
4. Review the design document in `.kiro/specs/platform-core/design.md`
