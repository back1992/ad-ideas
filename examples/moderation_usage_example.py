"""
Example usage of the Unified Moderation Dashboard and User Management System

This example demonstrates how to integrate and use the moderation and user
management features in a Streamlit application.
"""

import streamlit as st
from modules.database import get_database_manager
from modules.auth import get_auth_manager
from modules.moderation import get_unified_moderation_dashboard
from modules.user_management import get_user_management_system
from modules.comments import get_comment_system, get_comment_moderation_system
from modules.articles import get_article_manager, get_article_review_system


def show_admin_panel():
    """Display admin panel with moderation and user management tools."""
    
    # Initialize systems
    db_manager = get_database_manager()
    auth_manager = get_auth_manager()
    
    # Check if user is authenticated and is admin
    if not st.session_state.get('authentication_status'):
        st.warning("Please log in to access admin tools")
        return
    
    username = st.session_state.get('username')
    
    if not auth_manager.is_admin(username):
        st.error("Access denied. Admin privileges required.")
        return
    
    # Admin navigation
    st.sidebar.markdown("## 🛡️ Admin Tools")
    
    admin_page = st.sidebar.radio(
        "Select Tool",
        [
            "📊 Dashboard Overview",
            "🛡️ Moderation Dashboard",
            "👥 User Management",
            "📈 Platform Analytics"
        ]
    )
    
    if admin_page == "📊 Dashboard Overview":
        show_dashboard_overview(db_manager, auth_manager)
    
    elif admin_page == "🛡️ Moderation Dashboard":
        show_moderation_dashboard(db_manager, auth_manager, username)
    
    elif admin_page == "👥 User Management":
        show_user_management(db_manager, auth_manager, username)
    
    elif admin_page == "📈 Platform Analytics":
        show_platform_analytics(db_manager)


def show_dashboard_overview(db_manager, auth_manager):
    """Display overview dashboard with key metrics."""
    
    st.markdown("# 📊 Admin Dashboard Overview")
    st.markdown("Quick overview of platform status and pending actions")
    
    # Get statistics
    from modules.moderation import get_unified_moderation_dashboard
    from modules.comments import get_comment_system, get_comment_moderation_system
    from modules.articles import get_article_manager, get_article_review_system
    
    comment_system = get_comment_system(db_manager)
    comment_mod_system = get_comment_moderation_system(comment_system)
    article_manager = get_article_manager(db_manager, auth_manager)
    article_review_system = get_article_review_system(article_manager)
    
    mod_dashboard = get_unified_moderation_dashboard(
        db_manager,
        auth_manager,
        comment_mod_system,
        article_review_system
    )
    
    stats = mod_dashboard.get_moderation_statistics()
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📋 Articles Pending",
            stats['articles_pending'],
            help="Articles awaiting review"
        )
    
    with col2:
        st.metric(
            "🚩 Comments Reported",
            stats['comments_reported'],
            help="Comments flagged by users"
        )
    
    with col3:
        st.metric(
            "⚡ Actions Today",
            stats['moderation_actions_today'],
            help="Moderation actions taken today"
        )
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛡️ Go to Moderation", use_container_width=True):
            st.session_state['admin_page'] = "🛡️ Moderation Dashboard"
            st.rerun()
    
    with col2:
        if st.button("👥 Manage Users", use_container_width=True):
            st.session_state['admin_page'] = "👥 User Management"
            st.rerun()
    
    with col3:
        if st.button("📈 View Analytics", use_container_width=True):
            st.session_state['admin_page'] = "📈 Platform Analytics"
            st.rerun()
    
    # Recent activity
    st.markdown("---")
    st.markdown("### 📝 Recent Moderation Activity")
    
    recent_activity = mod_dashboard.get_audit_log(days_back=1)
    
    if recent_activity.empty:
        st.info("No moderation activity today")
    else:
        for _, activity in recent_activity.head(5).iterrows():
            st.caption(
                f"{activity['timestamp'][:16]} - {activity['username']}: "
                f"{activity['action']} - {activity['details'][:50] if activity['details'] else 'N/A'}"
            )


def show_moderation_dashboard(db_manager, auth_manager, username):
    """Display unified moderation dashboard."""
    
    # Initialize moderation systems
    comment_system = get_comment_system(db_manager)
    comment_mod_system = get_comment_moderation_system(comment_system)
    article_manager = get_article_manager(db_manager, auth_manager)
    article_review_system = get_article_review_system(article_manager)
    
    # Create and show dashboard
    mod_dashboard = get_unified_moderation_dashboard(
        db_manager,
        auth_manager,
        comment_mod_system,
        article_review_system
    )
    
    mod_dashboard.show_dashboard(username)


def show_user_management(db_manager, auth_manager, username):
    """Display user management dashboard."""
    
    # Create and show user management system
    user_mgmt = get_user_management_system(db_manager, auth_manager)
    user_mgmt.show_user_management_dashboard(username)


def show_platform_analytics(db_manager):
    """Display platform analytics and statistics."""
    
    st.markdown("# 📈 Platform Analytics")
    st.markdown("Comprehensive platform statistics and insights")
    
    # Get various statistics
    
    # User statistics
    st.markdown("### 👥 User Statistics")
    
    user_query = """
        SELECT 
            COUNT(DISTINCT username) as total_users,
            COUNT(DISTINCT CASE WHEN DATE(timestamp) = DATE('now') THEN username END) as active_today,
            COUNT(DISTINCT CASE WHEN DATE(timestamp) >= DATE('now', '-7 days') THEN username END) as active_week
        FROM user_activity
    """
    user_stats = db_manager.execute_query(user_query)
    
    if not user_stats.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", int(user_stats.iloc[0]['total_users']))
        
        with col2:
            st.metric("Active Today", int(user_stats.iloc[0]['active_today']))
        
        with col3:
            st.metric("Active This Week", int(user_stats.iloc[0]['active_week']))
    
    st.markdown("---")
    
    # Content statistics
    st.markdown("### 📚 Content Statistics")
    
    content_query = """
        SELECT 
            (SELECT COUNT(*) FROM articles WHERE status = 'published') as published_articles,
            (SELECT COUNT(*) FROM comments WHERE is_approved = 1) as approved_comments,
            (SELECT COUNT(*) FROM user_feedback) as total_feedback
    """
    content_stats = db_manager.execute_query(content_query)
    
    if not content_stats.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Published Articles", int(content_stats.iloc[0]['published_articles']))
        
        with col2:
            st.metric("Approved Comments", int(content_stats.iloc[0]['approved_comments']))
        
        with col3:
            st.metric("Total Feedback", int(content_stats.iloc[0]['total_feedback']))
    
    st.markdown("---")
    
    # Activity trends
    st.markdown("### 📊 Activity Trends (Last 7 Days)")
    
    activity_query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as actions
        FROM user_activity
        WHERE DATE(timestamp) >= DATE('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY date
    """
    activity_trends = db_manager.execute_query(activity_query)
    
    if not activity_trends.empty:
        st.line_chart(activity_trends.set_index('date'))
    else:
        st.info("No activity data available")


# Example of how to use in main app
def main():
    """Main application entry point."""
    
    st.set_page_config(
        page_title="Admin Panel Example",
        page_icon="🛡️",
        layout="wide"
    )
    
    # Initialize database
    db_manager = get_database_manager()
    auth_manager = get_auth_manager()
    
    # Login section
    if not st.session_state.get('authentication_status'):
        st.title("🛡️ Admin Panel Login")
        name, authentication_status, username = auth_manager.login()
        
        if authentication_status:
            st.success(f"Welcome {name}!")
            st.rerun()
        elif authentication_status is False:
            st.error("Username/password is incorrect")
        else:
            st.info("Please enter your credentials")
    else:
        # Show admin panel
        show_admin_panel()
        
        # Logout button in sidebar
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            auth_manager.force_logout()
            st.rerun()


if __name__ == "__main__":
    main()
