"""
Feedback System Test Page for 广告思想简史 Platform

This page allows you to test all feedback system functionality
in a live Streamlit environment.
"""

import streamlit as st
from modules.database import get_database_manager
from modules.auth import get_auth_manager
from modules.feedback import get_feedback_system, get_feedback_display_components


def feedback_test_page():
    """Test page for feedback system functionality."""
    
    st.title("🧪 Feedback System Test Page")
    st.markdown("Test all feedback system features in a live environment.")
    
    # Initialize systems
    db_manager = get_database_manager()
    auth_manager = get_auth_manager(db_manager=db_manager)
    feedback_system = get_feedback_system(db_manager)
    display_components = get_feedback_display_components(feedback_system)
    
    # Check authentication
    if not st.session_state.get('authentication_status'):
        st.warning("⚠️ Please log in first to test feedback features.")
        st.info("Go to '🔐 Authentication Demo' page to log in with test accounts.")
        
        with st.expander("🔑 Quick Login Reminder"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Admin**: admin / admin123")
            with col2:
                st.write("**Professor**: professor / prof123")
            with col3:
                st.write("**Student**: student / student123")
        
        return
    
    # Show current user
    user_info = auth_manager.get_current_user()
    st.success(f"✅ Logged in as: **{user_info['name']}** ({user_info['role']})")
    
    st.divider()
    
    # Test Section 1: Basic Feedback Collection
    st.header("1️⃣ Basic Feedback Collection")
    st.markdown("Test different types of feedback widgets:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👍 Thumbs Feedback")
        st.markdown("**Test Content: Ancient Advertising**")
        st.write("This is sample content about ancient advertising history...")
        
        display_components.display_thumbs_feedback(
            target_type="timeline",
            target_id="ancient_advertising_test",
            show_collection=True
        )
    
    with col2:
        st.subheader("⭐ Star Rating")
        st.markdown("**Test Content: Famous Campaign**")
        st.write("This is sample content about a famous advertising campaign...")
        
        display_components.display_stars_feedback(
            target_type="campaigns",
            target_id="famous_campaign_test",
            show_collection=True
        )
    
    with col3:
        st.subheader("😊 Emoji Faces")
        st.markdown("**Test Content: Industry Figure**")
        st.write("This is sample content about an advertising industry figure...")
        
        display_components.display_faces_feedback(
            target_type="figures",
            target_id="industry_figure_test",
            show_collection=True
        )
    
    st.divider()
    
    # Test Section 2: Statistics Display
    st.header("2️⃣ Feedback Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Detailed Statistics")
        st.markdown("**Ancient Advertising Content Stats:**")
        feedback_system.show_feedback_stats("timeline", "ancient_advertising_test")
        
        st.markdown("**Famous Campaign Content Stats:**")
        feedback_system.show_feedback_stats("campaigns", "famous_campaign_test")
    
    with col2:
        st.subheader("📈 Compact Statistics")
        st.markdown("**Compact stats for content lists:**")
        
        # Simulate content list items
        test_items = [
            {"type": "timeline", "id": "ancient_advertising_test", "title": "Ancient Advertising"},
            {"type": "campaigns", "id": "famous_campaign_test", "title": "Famous Campaign"},
            {"type": "figures", "id": "industry_figure_test", "title": "Industry Figure"},
        ]
        
        for item in test_items:
            with st.container():
                st.write(f"**{item['title']}**")
                st.write("Content preview goes here...")
                st.write("**Feedback:**")
                display_components.display_compact_stats(item["type"], item["id"])
                st.write("---")
    
    st.divider()
    
    # Test Section 3: Trending Content
    st.header("3️⃣ Trending Content")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 All Trending Content")
        display_components.display_trending_content(limit=10)
    
    with col2:
        st.subheader("🎯 Filtered Trending")
        content_type_filter = st.selectbox(
            "Filter by content type:",
            ["timeline", "campaigns", "figures", "articles"],
            key="trending_filter"
        )
        
        if content_type_filter:
            display_components.display_trending_content(content_type_filter, 5)
    
    st.divider()
    
    # Test Section 4: User Activity
    st.header("4️⃣ User Activity Summary")
    
    username = user_info['username']
    display_components.display_user_feedback_summary(username)
    
    st.divider()
    
    # Test Section 5: Raw Data Inspection
    st.header("5️⃣ Raw Data Inspection")
    st.markdown("Inspect the underlying data for debugging:")
    
    if st.checkbox("Show raw feedback data"):
        # Get user's feedback history
        history = feedback_system.get_user_feedback_history(username, 50)
        
        if not history.empty:
            st.subheader("Your Feedback History")
            st.dataframe(history)
        else:
            st.info("No feedback history found.")
        
        # Get popular content data
        popular = feedback_system.get_popular_content(limit=10)
        
        if not popular.empty:
            st.subheader("Popular Content Data")
            st.dataframe(popular)
        else:
            st.info("No popular content data found.")
    
    # Test Section 6: Manual Testing Tools
    st.divider()
    st.header("6️⃣ Manual Testing Tools")
    
    with st.expander("🛠️ Advanced Testing Tools"):
        st.subheader("Create Test Feedback")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            test_target_type = st.selectbox("Target Type", ["timeline", "campaigns", "figures", "articles"])
        
        with col2:
            test_target_id = st.text_input("Target ID", "test_content_123")
        
        with col3:
            test_feedback_type = st.selectbox("Feedback Type", ["thumbs", "stars", "faces"])
        
        test_feedback_value = st.slider("Feedback Value", 0, 4, 2)
        test_feedback_text = st.text_area("Optional Text", "This is test feedback")
        
        if st.button("Add Test Feedback"):
            success = feedback_system.save_feedback(
                username=username,
                target_type=test_target_type,
                target_id=test_target_id,
                feedback_type=test_feedback_type,
                feedback_value=test_feedback_value,
                feedback_text=test_feedback_text
            )
            
            if success:
                st.success("✅ Test feedback added!")
                feedback_system.update_content_stats(test_target_type, test_target_id)
                st.rerun()
            else:
                st.error("❌ Failed to add test feedback")
    
    # Instructions
    st.divider()
    st.header("📋 Testing Instructions")
    
    st.markdown("""
    ### How to Test:
    
    1. **Try Different Feedback Types**: Use the thumbs, stars, and faces widgets above
    2. **Check Duplicate Prevention**: Try submitting feedback twice for the same content
    3. **View Statistics**: See how statistics update in real-time
    4. **Test Different Users**: Log out and log in as different users to test multi-user functionality
    5. **Check Trending**: Add feedback to see content appear in trending sections
    
    ### Expected Behavior:
    
    - ✅ Feedback widgets should appear for logged-in users
    - ✅ Statistics should update immediately after feedback submission
    - ✅ Users should not be able to submit duplicate feedback
    - ✅ Compact stats should show in content lists
    - ✅ Trending content should rank by popularity
    - ✅ User activity should track all feedback submissions
    
    ### Test Accounts:
    
    - **admin** / admin123 (Full access)
    - **professor** / prof123 (Professor + student features)  
    - **student** / student123 (Basic access)
    """)


if __name__ == "__main__":
    feedback_test_page()