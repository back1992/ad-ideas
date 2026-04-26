# Moderation and User Management Guide

## Overview

This guide covers the unified moderation dashboard and user management system for administrators of the 广告思想简史 platform. These tools provide comprehensive control over content moderation, user accounts, and platform administration.

## Table of Contents

1. [Unified Moderation Dashboard](#unified-moderation-dashboard)
2. [User Management System](#user-management-system)
3. [Bulk Actions](#bulk-actions)
4. [Audit Logging](#audit-logging)
5. [Best Practices](#best-practices)

---

## Unified Moderation Dashboard

### Overview

The unified moderation dashboard (`modules/moderation.py`) combines article and comment moderation into a single, centralized interface. This allows administrators to efficiently manage all user-generated content from one location.

### Features

#### 1. Statistics Overview

The dashboard displays real-time statistics:
- **Articles Pending Review**: Number of articles awaiting approval
- **Comments Reported**: Number of comments flagged by users
- **Comments Unapproved**: Number of comments pending approval
- **Actions Today**: Number of moderation actions taken today

#### 2. Article Moderation Tab

Displays all articles pending review with options to:
- **Approve & Publish**: Immediately publish the article
- **Reject**: Send article back to draft with rejection reason
- **Request Changes**: Provide feedback to author for revisions

#### 3. Comment Moderation Tab

Provides three sub-tabs:
- **Reported Comments**: Comments flagged by users for review
- **Pending Approval**: Comments awaiting initial approval
- **All Comments**: Complete comment management interface

Actions available:
- **Approve**: Make comment visible to all users
- **Remove**: Delete comment permanently
- **Edit**: Modify comment content

#### 4. Audit Log Tab

Comprehensive logging of all moderation actions:
- Filter by action type (Article/Comment/User actions)
- Filter by time period (1-365 days)
- Filter by moderator username
- View detailed action history with timestamps

#### 5. Bulk Actions Tab

Perform actions on multiple items simultaneously:
- Select multiple comments or articles
- Approve/reject/remove in bulk
- Significant time savings for high-volume moderation

### Usage Example

```python
from modules.moderation import get_unified_moderation_dashboard
from modules.database import get_database_manager
from modules.auth import get_auth_manager
from modules.comments import get_comment_system, get_comment_moderation_system
from modules.articles import get_article_manager, get_article_review_system

# Initialize systems
db_manager = get_database_manager()
auth_manager = get_auth_manager()

# Get moderation systems
comment_system = get_comment_system(db_manager)
comment_mod_system = get_comment_moderation_system(comment_system)

article_manager = get_article_manager(db_manager, auth_manager)
article_review_system = get_article_review_system(article_manager)

# Create unified dashboard
mod_dashboard = get_unified_moderation_dashboard(
    db_manager,
    auth_manager,
    comment_mod_system,
    article_review_system
)

# Display dashboard (in Streamlit)
admin_username = st.session_state.get('username')
mod_dashboard.show_dashboard(admin_username)
```

---

## User Management System

### Overview

The user management system (`modules/user_management.py`) provides comprehensive tools for managing user accounts, roles, and monitoring user activity.

### Features

#### 1. User Accounts Tab

View and manage all user accounts:
- **Filter by Role**: Admin, Professor, Student
- **Filter by Status**: Active or Suspended
- **View User Details**: Name, email, role, activity stats
- **Account Actions**:
  - Suspend/Activate accounts
  - Change user roles
  - View detailed activity history

#### 2. Activity Monitoring Tab

Monitor user engagement across the platform:
- **Filter Options**:
  - By username
  - By action type (login, comment, feedback, etc.)
  - By time period (1-90 days)
- **Activity Summary**:
  - Actions by type
  - Most active users
  - Detailed activity log with timestamps

#### 3. Role Management Tab

Overview of platform roles and permissions:
- **User Counts by Role**: Admins, Professors, Students
- **Permissions Reference Table**: Clear breakdown of what each role can do
- **Quick Role Assignment**: Change user roles efficiently

### User Roles and Permissions

| Permission | Student | Professor | Admin |
|------------|---------|-----------|-------|
| View Content | ✅ | ✅ | ✅ |
| Submit Feedback | ✅ | ✅ | ✅ |
| Post Comments | ✅ | ✅ | ✅ |
| Create Articles | ❌ | ✅ | ✅ |
| Manage Own Articles | ❌ | ✅ | ✅ |
| Review Articles | ❌ | ❌ | ✅ |
| Moderate Comments | ❌ | ❌ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |
| View Analytics | ❌ | ✅ | ✅ |

### Account Suspension

When a user account is suspended:
1. The `is_active` field is set to `False` in the config
2. User cannot log in (blocked at authentication)
3. Existing sessions are terminated
4. Action is logged in the audit trail

To suspend a user:
```python
user_mgmt = get_user_management_system(db_manager, auth_manager)
success = user_mgmt.suspend_user('username', 'admin_username')
```

To activate a suspended user:
```python
success = user_mgmt.activate_user('username', 'admin_username')
```

### Role Management

Change a user's role:
```python
success = user_mgmt.change_user_role('username', 'professor', 'admin_username')
```

Valid roles:
- `student`: Basic access, can view and interact with content
- `professor`: Can create and manage articles
- `admin`: Full platform access including moderation and user management

---

## Bulk Actions

### Bulk Comment Moderation

1. Navigate to **Moderation Dashboard → Bulk Actions**
2. Select **Comments** as content type
3. Choose queue: Reported or Unapproved
4. Check boxes next to comments to moderate
5. Click action button:
   - **Approve All Selected**: Approve multiple comments
   - **Remove All Selected**: Delete multiple comments
   - **Clear Selection**: Reset checkboxes

### Bulk Article Moderation

1. Navigate to **Moderation Dashboard → Bulk Actions**
2. Select **Articles** as content type
3. Check boxes next to articles to moderate
4. Click action button:
   - **Approve & Publish All**: Publish multiple articles
   - **Reject All**: Reject multiple articles (requires reason)
   - **Clear Selection**: Reset checkboxes

### Performance Benefits

Bulk actions significantly improve moderation efficiency:
- Process 10+ items in seconds vs. minutes
- Reduce repetitive clicking
- Maintain consistent moderation standards
- Ideal for high-traffic periods

---

## Audit Logging

### What Gets Logged

All moderation and user management actions are logged:

**Article Actions:**
- `article_approved`: Article approved and published
- `article_rejected`: Article rejected with reason
- `article_changes_requested`: Feedback sent to author

**Comment Actions:**
- `comment_approved`: Comment approved for display
- `comment_rejected`: Comment rejected and removed
- `comment_removed`: Comment deleted by moderator
- `comment_edited`: Comment content modified

**User Actions:**
- `user_role_changed`: User role modified
- `user_suspended`: User account suspended
- `user_activated`: User account activated

### Audit Log Fields

Each log entry contains:
- **Username**: Moderator who performed the action
- **Action**: Type of action taken
- **Target Type**: Type of content (article, comment, user)
- **Target ID**: Specific item identifier
- **Details**: Additional context and information
- **Timestamp**: When the action occurred

### Viewing Audit Logs

Access audit logs through:
1. **Moderation Dashboard → Audit Log tab**
2. Apply filters to narrow results
3. View detailed information in expandable sections
4. Export data for compliance or reporting

---

## Best Practices

### Moderation Guidelines

1. **Review Regularly**: Check moderation queues daily
2. **Be Consistent**: Apply moderation standards uniformly
3. **Provide Feedback**: When rejecting content, explain why
4. **Use Bulk Actions**: For efficiency during high-volume periods
5. **Document Decisions**: Use the details field for complex cases

### User Management Guidelines

1. **Role Assignment**:
   - Start users as students
   - Promote to professor based on contribution quality
   - Limit admin role to trusted individuals

2. **Account Suspension**:
   - Use as last resort after warnings
   - Document reason in audit log
   - Set clear reinstatement criteria
   - Communicate with user when possible

3. **Activity Monitoring**:
   - Review activity patterns regularly
   - Identify and address unusual behavior
   - Recognize and reward active contributors
   - Use data to improve platform features

### Security Considerations

1. **Admin Access**:
   - Limit number of admin accounts
   - Use strong passwords
   - Review admin actions regularly
   - Rotate admin credentials periodically

2. **Data Privacy**:
   - Respect user privacy in activity monitoring
   - Only access user data when necessary
   - Follow data protection regulations
   - Anonymize data for analytics when possible

3. **Audit Trail**:
   - Never delete audit logs
   - Review logs for suspicious activity
   - Maintain logs for compliance
   - Use logs for dispute resolution

---

## Integration with Main Application

To integrate these features into your Streamlit app:

```python
import streamlit as st
from modules.database import get_database_manager
from modules.auth import get_auth_manager
from modules.moderation import get_unified_moderation_dashboard
from modules.user_management import get_user_management_system
from modules.comments import get_comment_system, get_comment_moderation_system
from modules.articles import get_article_manager, get_article_review_system

# Initialize systems
db_manager = get_database_manager()
auth_manager = get_auth_manager()

# Check if user is admin
if auth_manager.is_admin():
    # Create navigation
    admin_page = st.sidebar.selectbox(
        "Admin Tools",
        ["Moderation Dashboard", "User Management"]
    )
    
    if admin_page == "Moderation Dashboard":
        # Initialize moderation systems
        comment_system = get_comment_system(db_manager)
        comment_mod_system = get_comment_moderation_system(comment_system)
        article_manager = get_article_manager(db_manager, auth_manager)
        article_review_system = get_article_review_system(article_manager)
        
        # Show dashboard
        mod_dashboard = get_unified_moderation_dashboard(
            db_manager,
            auth_manager,
            comment_mod_system,
            article_review_system
        )
        mod_dashboard.show_dashboard(st.session_state['username'])
    
    elif admin_page == "User Management":
        # Show user management
        user_mgmt = get_user_management_system(db_manager, auth_manager)
        user_mgmt.show_user_management_dashboard(st.session_state['username'])
```

---

## Troubleshooting

### Common Issues

**Issue**: Bulk actions not working
- **Solution**: Ensure you've selected items with checkboxes before clicking action buttons

**Issue**: User suspension not preventing login
- **Solution**: Verify `is_active` field is set to `False` in config.yaml and config is reloaded

**Issue**: Audit log not showing recent actions
- **Solution**: Check time period filter, may need to expand date range

**Issue**: Role changes not taking effect
- **Solution**: User must log out and log back in for role changes to apply

### Getting Help

For additional support:
1. Check the audit log for error details
2. Review application logs for technical errors
3. Consult the requirements and design documents
4. Contact the development team

---

## Future Enhancements

Potential improvements for future versions:
- Email notifications for moderation actions
- Automated moderation rules based on keywords
- Advanced analytics and reporting
- Batch user import/export
- Custom role creation with granular permissions
- Integration with external authentication systems

---

## Conclusion

The unified moderation dashboard and user management system provide administrators with powerful tools to maintain platform quality, manage users effectively, and ensure a positive experience for all users. Regular use of these tools, combined with clear moderation policies, will help build a thriving academic community.
