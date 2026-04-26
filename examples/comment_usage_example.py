"""
Comment System Usage Example

This example demonstrates how to use the CommentSystem and CommentModerationSystem
in a Streamlit application.
"""

import streamlit as st
from modules.database import get_database_manager
from modules.comments import get_comment_system, get_comment_moderation_system
from modules.auth import get_auth_manager

# Initialize systems
db_manager = get_database_manager("platform.db")
comment_system = get_comment_system(db_manager)
auth_manager = get_auth_manager("config.yaml", db_manager)

# Example 1: Display comments section on a content page
def display_content_with_comments():
    """Display content with comments section"""
    
    st.title("Example Content Page")
    
    # Your content here
    st.markdown("## Article Title")
    st.markdown("Article content goes here...")
    
    # Add comments section
    # This will show comment input (if logged in) and all existing comments
    comment_system.display_comments_section(
        target_type="article",
        target_id="example_article_1"
    )

# Example 2: Add a comment programmatically
def add_comment_example():
    """Example of adding a comment programmatically"""
    
    username = st.session_state.get('username')
    
    if username:
        success = comment_system.add_comment(
            username=username,
            target_type="timeline",
            target_id="1920s",
            content="Great historical overview!",
            parent_id=None  # None for top-level comment, or comment_id for reply
        )
        
        if success:
            st.success("Comment posted!")
        else:
            st.error("Failed to post comment")
    else:
        st.warning("Please log in to comment")

# Example 3: Display moderation interface (admin only)
def display_moderation_interface():
    """Display comment moderation interface for admins"""
    
    username = st.session_state.get('username')
    
    # Check if user is admin
    if auth_manager.is_admin(username):
        mod_system = get_comment_moderation_system(comment_system)
        mod_system.display_moderation_queue(username)
    else:
        st.error("Access denied. Admin privileges required.")

# Example 4: Get comments for display in a custom format
def custom_comment_display():
    """Example of custom comment display"""
    
    comments = comment_system.get_comments(
        target_type="figures",
        target_id="david_ogilvy",
        approved_only=True
    )
    
    if not comments.empty:
        st.markdown(f"### {len(comments)} Comments")
        
        for _, comment in comments.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 11])
                
                with col1:
                    avatar = comment_system.generate_user_avatar(comment['username'])
                    st.markdown(f"<div style='font-size: 2em;'>{avatar}</div>", 
                              unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{comment['username']}**")
                    st.markdown(comment['content'])
                    st.caption(f"👍 {comment['likes']} likes")
                
                st.markdown("---")
    else:
        st.info("No comments yet")

# Example 5: Like a comment
def like_comment_example(comment_id: int):
    """Example of liking a comment"""
    
    username = st.session_state.get('username')
    
    if username:
        success = comment_system.like_comment(comment_id, username)
        if success:
            st.success("Comment liked!")
            st.rerun()
    else:
        st.warning("Please log in to like comments")

# Example 6: Report a comment
def report_comment_example(comment_id: int):
    """Example of reporting a comment"""
    
    username = st.session_state.get('username')
    
    if username:
        success = comment_system.report_comment(
            comment_id,
            username,
            "Inappropriate content"
        )
        if success:
            st.success("Comment reported for moderation")
    else:
        st.warning("Please log in to report comments")

# Main app structure example
def main():
    """Main application structure"""
    
    st.set_page_config(page_title="Comment System Example", layout="wide")
    
    # Authentication
    name, authentication_status, username = auth_manager.login()
    
    if authentication_status:
        st.sidebar.success(f"Welcome {name}!")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Navigate",
            ["Content Page", "Custom Display", "Moderation (Admin)"]
        )
        
        if page == "Content Page":
            display_content_with_comments()
        elif page == "Custom Display":
            custom_comment_display()
        elif page == "Moderation (Admin)":
            display_moderation_interface()
        
        # Logout button
        if st.sidebar.button("Logout"):
            auth_manager.force_logout()
            st.rerun()
    
    elif authentication_status == False:
        st.error("Username/password is incorrect")
    else:
        st.warning("Please enter your username and password")

if __name__ == "__main__":
    main()
