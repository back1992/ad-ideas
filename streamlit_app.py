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

import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth


# Page configuration
st.set_page_config(
    page_title="广告思想简史",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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


def show_login_dialog():
    """Show login dialog (used from sidebar for guests)."""
    username_input = st.text_input(t('username_label'), key="login_user")
    password_input = st.text_input(t('password_label'), type="password", key="login_pass")

    if st.button(t('login'), type="primary", use_container_width=True):
        if not username_input or not password_input:
            st.warning(f"⚠️ {t('fill_username_password')}")
            return
        try:
            with open("config.yaml", 'r', encoding='utf-8') as file:
                config = yaml.load(file, Loader=SafeLoader)
            users = config['credentials']['usernames']
            if username_input not in users:
                st.error(f"❌ {t('username_not_found')}")
                return
            stored_password = users[username_input]['password']
            # Try hashed comparison first, then plain text fallback
            pw_match = False
            try:
                if stauth.Hasher([password_input]).generate()[0] == stored_password:
                    pw_match = True
            except Exception:
                pass
            if not pw_match and password_input == stored_password:
                pw_match = True
            if pw_match:
                st.session_state['authentication_status'] = True
                st.session_state['username'] = username_input
                st.session_state['name'] = users[username_input]['name']
                st.session_state['user_role'] = users[username_input].get('role', 'student')
                activity_logger.log_login(username_input, success=True)
                st.rerun()
            else:
                st.error(t('login_failed'))
                activity_logger.log_login(username_input, success=False)
        except Exception as e:
            st.error(f"Authentication system error: {e}")


def show_register_dialog():
    """Show self-registration dialog."""
    st.markdown(f"### 📝 {t('register')}")

    with st.form("register_form"):
        reg_name = st.text_input(t('name_label'))
        reg_username = st.text_input(t('username_label'))
        reg_email = st.text_input(t('email_label'))
        reg_password = st.text_input(t('password_label'), type="password")
        reg_confirm = st.text_input(t('confirm_password'), type="password")
        reg_submit = st.form_submit_button(t('register'), type="primary")

        if reg_submit:
            if not all([reg_name, reg_username, reg_email, reg_password, reg_confirm]):
                st.error("⚠️ Please fill in all fields")
            elif reg_password != reg_confirm:
                st.error("⚠️ Passwords do not match")
            elif not reg_username.replace('.', '').replace('_', '').isalnum():
                st.error("⚠️ Username can only contain letters, numbers, dots, and underscores")
            else:
                with open("config.yaml", 'r', encoding='utf-8') as file:
                    config = yaml.load(file, Loader=SafeLoader)

                users = config['credentials']['usernames']
                if reg_username in users:
                    st.error("⚠️ Username already exists")
                else:
                    hashed = stauth.Hasher([reg_password]).generate()[0]
                    users[reg_username] = {
                        'name': reg_name,
                        'email': reg_email,
                        'password': hashed,
                        'role': 'student',
                    }
                    with open("config.yaml", 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)

                    activity_logger.log_login(reg_username, success=True)
                    st.success("✅ Registration successful! You can now login.")
                    st.rerun()


def show_sidebar():
    """Show sidebar with auth info or login/register prompt."""
    is_authenticated = st.session_state.get('authentication_status')

    # Language selector
    render_language_selector()
    st.sidebar.markdown("---")

    if is_authenticated:
        # Show user info and logout
        user_info = auth_manager.get_current_user()
        st.sidebar.markdown(f"### 👤 {t('user_info')}")
        st.sidebar.write(f"**{t('name_label')}:** {user_info['name']}")
        st.sidebar.write(f"**{t('username_label')}:** {user_info['username']}")

        role_emoji = {
            'admin': '👨‍💼',
            'professor': '👨‍🏫',
            'student': '👨‍🎓'
        }
        role_display = user_info.get('role', 'student')
        emoji = role_emoji.get(role_display, '👤')
        st.sidebar.write(f"**{t('role_label')}:** {emoji} {role_display.title()}")

        st.sidebar.markdown("---")

        if st.sidebar.button(f"🚪 {t('logout')}", type="primary", use_container_width=True):
            auth_manager.force_logout()
            st.rerun()
    else:
        # Show login/register for guests
        st.sidebar.markdown(f"### 📚 {t('app_title')}")
        st.sidebar.info(t('guest_browsing_info'))

        auth_tabs = st.sidebar.tabs([t('login'), t('register')])
        with auth_tabs[0]:
            show_login_dialog()
        with auth_tabs[1]:
            show_register_dialog()


def get_navigation_menu():
    """Get navigation menu based on user role. All users see the same base pages."""
    user_info = auth_manager.get_current_user()
    role = user_info.get('role', 'student')
    is_authenticated = user_info.get('authenticated', False)

    # Base menu available to everyone (guests + logged-in)
    menu = {
        f"🏠 {t('page_home')}": intro,
        f"📱 {t('download_app')}": show_download_page,
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


def show_download_page():
    """Display app download page."""
    st.markdown(f"# {t('download_app_title')}")
    st.info(t('download_app_desc'))

    st.markdown("""
    ### How to install

    1. Click the button below to download the APK file
    2. Transfer to your Android phone (USB, cloud, etc.)
    3. Open the file on your phone and tap "Install"
    4. If prompted, enable "Install from unknown sources" in Settings

    > The app loads this website in a native WebView, so all content is up-to-date.
    """)

    apk_url = "https://github.com/back1992/ad-ideas/releases/download/v0.1.0-apk/app-debug.apk"
    
    # Plain <a> tag without target="_blank" — most reliable for mobile download
    # On Android, target="_blank" inside iframes often blocks downloads entirely
    # Without target, the browser navigates the iframe to the APK URL and triggers download
    st.markdown(
        f'<a href="{apk_url}" '
        f'style="display:inline-block;padding:0.75rem 1.5rem;background:#FF4B4B;color:#fff;'
        f'border-radius:0.5rem;text-decoration:none;font-weight:600;font-size:1rem;">'
        f'📱 {t("download_button")}</a>',
        unsafe_allow_html=True,
    )


def show_search_interface():
    """Display search interface."""
    # Display search interface from search system
    search_system.display_search_interface()
    
    # Add content recommendations section
    st.markdown("---")
    st.markdown(f"## 📌 {t('page_recommendations')}")
    
    # Show popular content
    show_popular_content()


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
    st.sidebar.title(f"📚 {t('navigation')}")
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

    # App download link in sidebar
    st.sidebar.markdown("---")
    download_url = "https://github.com/back1992/ad-ideas/releases/download/v0.1.0-apk/app-debug.apk"
    st.sidebar.markdown(
        f'<a href="{download_url}" '
        f'style="display:block;padding:0.5rem 1rem;background:#FF4B4B;color:#fff;'
        f'border-radius:0.5rem;text-decoration:none;font-weight:600;text-align:center;">'
        f'📱 {t("download_button")}</a>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
