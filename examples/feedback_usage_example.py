"""
Example usage of the FeedbackSystem for the 广告思想简史 Platform.

This example demonstrates how to integrate the feedback system
into Streamlit pages for content feedback collection.
"""

import streamlit as st
from modules.database import get_database_manager
from modules.feedback import get_feedback_system, get_feedback_display_components


def example_content_page():
    """Example content page with feedback integration."""
    
    # Initialize systems
    db_manager = get_database_manager()
    feedback_system = get_feedback_system(db_manager)
    display_components = get_feedback_display_components(feedback_system)
    
    st.title("📚 广告思想简史 - Content Example")
    
    # Example content
    st.markdown("""
    ## 广告的起源与发展
    
    广告作为一种商业传播形式，有着悠久的历史。从古代的叫卖声到现代的数字营销，
    广告始终在商业活动中扮演着重要角色...
    
    ### 古代广告
    - 古埃及的纸草广告
    - 古罗马的墙面广告
    - 中国古代的招牌文化
    
    ### 现代广告的兴起
    随着印刷技术的发展，现代广告开始兴起...
    """)
    
    # Add feedback section
    st.markdown("---")
    st.markdown("### 💭 您对这篇内容的看法")
    
    # Example 1: Thumbs feedback
    with st.expander("👍 快速评价", expanded=True):
        display_components.display_thumbs_feedback(
            target_type="timeline",
            target_id="ancient_advertising_history",
            show_collection=True
        )
    
    # Example 2: Star rating
    with st.expander("⭐ 详细评分"):
        display_components.display_stars_feedback(
            target_type="timeline", 
            target_id="ancient_advertising_history",
            show_collection=True
        )
    
    # Example 3: Emoji faces
    with st.expander("😊 情感反馈"):
        display_components.display_faces_feedback(
            target_type="timeline",
            target_id="ancient_advertising_history", 
            show_collection=True
        )


def example_content_list_page():
    """Example content list page with compact feedback stats."""
    
    # Initialize systems
    db_manager = get_database_manager()
    feedback_system = get_feedback_system(db_manager)
    display_components = get_feedback_display_components(feedback_system)
    
    st.title("📋 Content List with Feedback Stats")
    
    # Example content items
    content_items = [
        {"type": "timeline", "id": "ancient_advertising_history", "title": "古代广告的起源"},
        {"type": "figures", "id": "david_ogilvy", "title": "大卫·奥格威 - 广告教父"},
        {"type": "campaigns", "id": "coca_cola_happiness", "title": "可口可乐的快乐营销"},
    ]
    
    for item in content_items:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(item["title"])
                st.write("Content preview goes here...")
            
            with col2:
                st.markdown("**Feedback:**")
                display_components.display_compact_stats(item["type"], item["id"])
            
            st.divider()


def example_trending_page():
    """Example trending content page."""
    
    # Initialize systems
    db_manager = get_database_manager()
    feedback_system = get_feedback_system(db_manager)
    display_components = get_feedback_display_components(feedback_system)
    
    st.title("🔥 Trending Content")
    
    # Display trending content
    display_components.display_trending_content(limit=10)
    
    # Filter by content type
    st.markdown("---")
    content_type = st.selectbox(
        "Filter by content type:",
        ["All", "timeline", "figures", "campaigns", "articles"]
    )
    
    if content_type != "All":
        st.markdown(f"### Trending {content_type.title()} Content")
        display_components.display_trending_content(content_type, 5)


def example_user_profile_page():
    """Example user profile page with feedback summary."""
    
    # Initialize systems
    db_manager = get_database_manager()
    feedback_system = get_feedback_system(db_manager)
    display_components = get_feedback_display_components(feedback_system)
    
    st.title("👤 User Profile")
    
    # Check if user is logged in
    username = st.session_state.get('username')
    if not username:
        st.warning("Please log in to view your profile.")
        return
    
    st.markdown(f"## Welcome, {username}!")
    
    # Display user feedback summary
    display_components.display_user_feedback_summary(username)


def main():
    """Main function to run the example."""
    
    st.sidebar.title("Feedback System Examples")
    
    page = st.sidebar.selectbox(
        "Choose an example:",
        [
            "Content Page with Feedback",
            "Content List with Stats", 
            "Trending Content",
            "User Profile"
        ]
    )
    
    if page == "Content Page with Feedback":
        example_content_page()
    elif page == "Content List with Stats":
        example_content_list_page()
    elif page == "Trending Content":
        example_trending_page()
    elif page == "User Profile":
        example_user_profile_page()


if __name__ == "__main__":
    main()