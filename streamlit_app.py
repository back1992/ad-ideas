"""
广告思想简史 Platform - Main Application

This is the main entry point for the 广告思想简史 (Advertising History) platform.
It provides user authentication, role-based navigation, and integrates all platform features.
"""

import streamlit as st

from dotenv import load_dotenv
load_dotenv()  # Load .env before importing modules that use os.getenv()

from utils.i18n import t, render_language_selector

from modules.auth import get_auth_manager
from modules.database import get_database_manager
from modules.feedback import get_feedback_system
from modules.comments import get_comment_system
from modules.articles import get_article_manager
from modules.activity import get_activity_logger
from modules.analytics import get_analytics_dashboard
from modules.search import get_search_system
from modules.moderation import get_unified_moderation_dashboard

from modules.ai_chat import chat_interface
from homepage import intro
from pages import memorabilia, superstar, plotting_data
from classic_ad_100 import classic_ad
from utils.styles import inject_styles

# Page configuration
st.set_page_config(
    page_title="广告思想简史",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject global CSS theme
inject_styles()

# Initialize core systems
@st.cache_resource
def init_database_systems():
    """Initialize and cache database-dependent systems (excluding auth)."""
    db_manager = get_database_manager()
    feedback_system = get_feedback_system(db_manager)
    comment_system = get_comment_system(db_manager)
    activity_logger = get_activity_logger(db_manager)
    search_system = get_search_system(db_manager)
    
    return db_manager, feedback_system, comment_system, activity_logger, search_system


def init_auth_and_dependent_systems(db_manager, activity_logger):
    """Initialize auth manager and systems that depend on it (not cached due to widget usage)."""
    auth_manager = get_auth_manager(db_manager=db_manager)
    article_manager = get_article_manager(db_manager, auth_manager)
    analytics_dashboard = get_analytics_dashboard(db_manager, activity_logger)

    # Initialize moderation systems
    from modules.articles import ArticleReviewSystem
    article_review_system = ArticleReviewSystem(article_manager)
    moderation_dashboard = get_unified_moderation_dashboard(
        db_manager, auth_manager, comment_system, article_review_system
    )

    return auth_manager, article_manager, analytics_dashboard, moderation_dashboard


# Initialize database systems (cached)
db_manager, feedback_system, comment_system, activity_logger, search_system = init_database_systems()

# Initialize auth and dependent systems (not cached to avoid widget issues)
auth_manager, article_manager, analytics_dashboard, moderation_dashboard = init_auth_and_dependent_systems(db_manager, activity_logger)


def show_sidebar():
    """Show sidebar with auth info or login/register prompt."""
    is_authenticated = st.session_state.get('authentication_status')

    # Branded header
    st.sidebar.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 1rem;">
        <div style="font-size: 1.6rem; font-weight: 700; letter-spacing: 0.02em;">📚 广告思想简史</div>
        <div style="font-size: 0.85rem; opacity: 0.7; margin-top: 4px;">Advertising Thought History</div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Language selector
    render_language_selector()
    st.sidebar.markdown("---")

    if is_authenticated:
        user_info = auth_manager.get_current_user()
        role_emoji = {'admin': '👨‍💼', 'professor': '👨‍🏫', 'student': '👨‍🎓'}
        role_display = user_info.get('role', 'student')
        emoji = role_emoji.get(role_display, '👤')

        st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.08); border-radius: 10px; padding: 14px 16px; margin-bottom: 8px;">
            <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 4px;">{emoji} {user_info['name']}</div>
            <div style="font-size: 0.85rem; opacity: 0.7;">@{user_info['username']} · {role_display.title()}</div>
        </div>
        """, unsafe_allow_html=True)

        st.sidebar.markdown("")

        if st.sidebar.button(f"🚪 {t('logout')}", type="primary", use_container_width=True):
            auth_manager.force_logout()
            st.rerun()
    else:
        # Guest info banner — styled for high contrast
        st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15);
            border-radius: 10px; padding: 12px 14px; margin-bottom: 16px;">
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.92); line-height: 1.5;">
                💡 {t('guest_browsing_info')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Login section
        st.sidebar.markdown(
            '<div style="font-size: 1.05rem; font-weight: 600; color: #fff; '
            'margin-bottom: 10px;">🔐 Login</div>',
            unsafe_allow_html=True,
        )
        auth_manager.login(location="sidebar")

        st.sidebar.markdown(
            '<div style="height: 12px;"></div>',
            unsafe_allow_html=True,
        )
        st.sidebar.markdown(
            '<hr style="border-color: rgba(255,255,255,0.12); margin: 0 0 12px 0;">',
            unsafe_allow_html=True,
        )

        # Register section
        st.sidebar.markdown(
            '<div style="font-size: 1.05rem; font-weight: 600; color: #fff; '
            'margin-bottom: 10px;">📝 Register</div>',
            unsafe_allow_html=True,
        )
        auth_manager.register_user(location="sidebar", captcha=False)


def get_navigation_menu():
    """Get navigation menu based on user role. All users see the same base pages."""
    user_info = auth_manager.get_current_user()
    role = user_info.get('role', 'student')
    is_authenticated = user_info.get('authenticated', False)

    # Base menu available to everyone (guests + logged-in)
    menu = {
        f"🏠 {t('page_home')}": intro,
        f"🔍 {t('page_search')}": show_search_interface,
        f"📅 {t('page_timeline')}": memorabilia,
        f"⭐ {t('page_stars')}": superstar,
        f"🎬 {t('page_campaigns')}": classic_ad,
        f"📊 {t('page_data')}": plotting_data,
    }

    # Chat available to all (but will prompt for interaction)
    menu[f"💬 {t('page_chat')}"] = chat_interface

    # Add professor/admin features
    if is_authenticated and role in ['professor', 'admin']:
        menu[f"📝 {t('page_articles')}"] = show_my_articles
        menu[f"✍️ {t('page_create_article')}"] = show_article_editor

    # Add admin-only features
    if is_authenticated and role == 'admin':
        menu[f"🔧 {t('page_moderation')}"] = show_moderation_panel
        menu[f"📈 {t('page_analytics')}"] = show_analytics_dashboard

    return menu


    """Display search interface."""
    # Display search interface from search system
    search_system.display_search_interface()
    
    # Add content recommendations section
    st.markdown("---")
    st.markdown(f"## 📌 {t('page_recommendations')}")
    
    # Show popular content
    show_popular_content()


def show_search_interface():
    """Display search interface."""
    st.markdown("""
    <div class="page-header">
        <h1>🔍 搜索</h1>
        <p>Search — 搜索文章、时间线、人物和经典广告</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    search_system.display_search_interface()


def show_popular_content():
    """Display popular and trending content."""
    try:
        tab1, tab2 = st.tabs([f"🔥 {t('popular_articles_tab')}", f"💬 {t('active_discussions_tab')}"])
        
        with tab1:
            # Get popular articles
            popular_articles = feedback_system.get_popular_content(target_type='article', limit=5)
            
            if not popular_articles.empty:
                st.markdown(f"### {t('top_articles_by_engagement')}")
                
                for idx, row in popular_articles.iterrows():
                    # Get full article details
                    article = article_manager.get_article_by_id(int(row['target_id']))
                    
                    if article:
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.markdown(f"**📄 {article['title']}**")
                                st.caption(f"👤 {article['author']} | 📁 {article['category']}")
                                if article['excerpt']:
                                    st.markdown(f"> {article['excerpt'][:150]}...")
                            
                            with col2:
                                st.metric("👁️", article['views'])
                                st.metric("⭐", f"{article['avg_rating']:.1f}")
                            
                            if st.button(t('view'), key=f"popular_article_{article['id']}"):
                                st.session_state['view_article_id'] = article['id']
                                st.rerun()
                            
                            st.divider()
            else:
                st.info(t('no_popular_articles'))
        
        with tab2:
            # Get articles with most comments
            query = """
                SELECT target_id, COUNT(*) as comment_count
                FROM comments
                WHERE target_type = 'article' AND is_approved = 1
                GROUP BY target_id
                ORDER BY comment_count DESC
                LIMIT 5
            """
            active_discussions = db_manager.execute_query(query, ())
            
            if not active_discussions.empty:
                st.markdown(f"### {t('most_discussed_articles')}")
                
                for idx, row in active_discussions.iterrows():
                    article = article_manager.get_article_by_id(int(row['target_id']))
                    
                    if article:
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.markdown(f"**📄 {article['title']}**")
                                st.caption(f"👤 {article['author']}")
                            
                            with col2:
                                st.metric("💬", int(row['comment_count']))
                            
                            if st.button(t('join_discussion'), key=f"discuss_article_{article['id']}"):
                                st.session_state['view_article_id'] = article['id']
                                st.rerun()
                            
                            st.divider()
            else:
                st.info(t('no_discussions_yet'))
    
    except Exception as e:
        st.error(f"Unable to load recommendations: {str(e)}")


def show_my_articles():
    """Display user's articles."""
    st.title(f"📝 {t('page_articles')}")
    
    username = st.session_state.get('username')
    if not username:
        st.error(t('requires_login'))
        return
    
    # Show article list for current user
    article_manager.show_article_list(username=username)


def show_article_editor():
    """Display article editor."""
    st.title(f"✍️ {t('page_create_article')}")
    
    # Check permission
    if not auth_manager.is_professor_or_admin():
        st.error("访问被拒绝。此功能需要教授或管理员权限。")
        st.error("Access denied. This feature requires professor or admin role.")
        return
    
    username = st.session_state.get('username')
    article_manager.show_article_editor(username=username)


def show_moderation_panel():
    """Display content moderation panel."""
    st.title(f"🔧 {t('page_moderation')}")

    # Check admin permission
    username = st.session_state.get('username')
    if not auth_manager.is_admin(username):
        st.error("访问被拒绝。此功能需要管理员权限。")
        st.error("Access denied. This feature requires admin role.")
        return

    moderation_dashboard.show_dashboard(username)


def show_analytics_dashboard():
    """Display platform analytics dashboard."""
    st.title(f"📊 {t('page_analytics')}")
    
    # Check admin permission
    username = st.session_state.get('username')
    if not username or not auth_manager.is_admin(username):
        st.error("访问被拒绝。此功能需要管理员权限。")
        st.error("Access denied. This feature requires admin role.")
        return
    
    # Display comprehensive analytics dashboard
    analytics_dashboard.show_dashboard(username)


def main():
    """Main application entry point."""

    # Show sidebar with login/register for guests or user info for authenticated users
    show_sidebar()

    # Get navigation menu based on role (guests see base pages)
    menu = get_navigation_menu()

    # Sidebar navigation
    st.sidebar.markdown(f"#### 🧭 {t('navigation')}")
    selected_page = st.sidebar.radio(
        t('select_page'),
        list(menu.keys()),
        label_visibility="collapsed"
    )

    # Display selected page
    try:
        menu[selected_page]()
    except Exception as e:
        st.error(f"{t('error_loading_page')}: {str(e)}")
        st.exception(e)



if __name__ == "__main__":
    main()
