"""
Simple i18n utility for language switching between Chinese and English.
"""

import streamlit as st
from typing import Optional

# Translations: key maps to (Chinese, English)
TRANSLATIONS: dict[str, tuple[str, str]] = {
    # UI elements
    "app_title": ("广告思想简史", "Advertising History"),
    "app_subtitle": ("广告思想简史平台", "Advertising Thought History Platform"),
    "navigation": ("导航", "Navigation"),
    "select_page": ("选择页面", "Select Page"),
    "login": ("登录", "Login"),
    "register": ("注册", "Register"),
    "confirm_password": ("确认密码", "Confirm Password"),
    "email_label": ("邮箱", "Email"),
    "logout": ("退出登录", "Logout"),
    "user_info": ("用户信息", "User Info"),
    "name_label": ("姓名", "Name"),
    "username_label": ("用户名", "Username"),
    "password_label": ("密码", "Password"),
    "role_label": ("角色", "Role"),
    "guest_browsing_info": ("浏览内容无需登录，登录后可以评论和参与互动", "Browsing is free. Log in to comment and interact."),

    # App download
    "download_app": ("下载App", "Download App"),
    "download_app_title": ("📱 下载Android应用", "📱 Download Android App"),
    "download_app_desc": ("在手机上体验广告思想简史，支持中英文切换", "Experience the app on your phone with bilingual support"),
    "download_button": ("下载 APK 文件", "Download APK File"),

    # Pages
    "page_home": ("首页", "Home"),
    "page_search": ("搜索", "Search"),
    "page_timeline": ("广告大事年表", "Advertising Timeline"),
    "page_stars": ("20世纪广告百位巨星榜", "Top 100 Advertising Stars"),
    "page_campaigns": ("20世纪最成功的广告TOP100", "Top 100 Campaigns"),
    "page_data": ("行业数据", "Industry Data"),
    "page_recommendations": ("推荐内容", "Recommended Content"),
    "page_chat": ("与大师对话", "Chat with Masters"),
    "page_articles": ("我的文章", "My Articles"),
    "page_create_article": ("创建文章", "Create Article"),
    "page_moderation": ("内容审核", "Content Moderation"),
    "page_analytics": ("平台分析", "Platform Analytics"),

    # Feedback & Comments
    "feedback_title": ("您的反馈", "Your Feedback"),
    "feedback_prompt": ("您的看法", "How do you find this content?"),
    "comments_title": ("评论互动", "Comments & Discussion"),
    "comments_subtitle": ("评论与互动", "Comments & Interaction"),
    "popular_articles_tab": ("热门文章", "Popular Articles"),
    "active_discussions_tab": ("活跃讨论", "Active Discussions"),
    "top_articles_by_engagement": ("热门内容排名", "Top Articles by Engagement"),
    "most_discussed_articles": ("热议文章", "Most Discussed Articles"),
    "no_popular_articles": ("还没有热门文章，快来探索内容吧！", "No popular articles yet. Start exploring content!"),
    "no_discussions_yet": ("还没有讨论，来做第一个评论的人吧！", "No discussions yet. Be the first to comment!"),
    "view": ("查看", "View"),
    "join_discussion": ("参与讨论", "Join Discussion"),
    "search_title": ("搜索", "Search"),
    "search_subtitle": ("搜索文章、评论和平台内容", "Search across articles, comments, and platform content"),
    "search_query_placeholder": ("输入关键词搜索", "Enter keywords to search"),
    "search_button": ("搜索", "Search"),
    "filter_by_type": ("按内容类型筛选", "Filter by content type"),
    "search_articles": ("文章", "Articles"),
    "search_comments": ("评论", "Comments"),
    "search_all": ("全部内容", "All Content"),
    "no_content_type_selected": ("请至少选择一种内容类型进行搜索", "Please select at least one content type to search."),
    "searching": ("正在搜索", "Searching"),
    "enter_search_query": ("输入搜索关键词开始搜索", "Enter a search query to begin."),
    "unable_to_search": ("无法进行搜索", "Unable to display search interface."),
    "no_results_found": ("未找到搜索结果，请尝试其他关键词", "No results found for '{query}'. Try different keywords."),
    "found_results": ("找到 {count} 条结果", "Found {count} result(s) for '{query}'"),
    "article_results": ("文章结果", "Articles"),
    "comment_results": ("评论结果", "Comments"),
    "unable_to_display_results": ("无法显示搜索结果", "Unable to display search results."),
    "view_article": ("查看文章", "View Article"),
    "unable_to_display_articles": ("无法显示文章结果", "Unable to display article results."),
    "unable_to_display_comments": ("无法显示评论结果", "Unable to display comment results."),
    "relevance_score": ("相关度", "Score"),
    "views": ("浏览", "views"),
    "add_comment": ("添加评论", "Add your comment"),
    "reply_to_comment": ("回复评论", "Reply to comment"),
    "your_comment": ("您的评论", "Your comment"),
    "excerpt_label": ("摘要", "Excerpt / Summary"),
    "excerpt_help": ("文章简要摘要（可选，留空则自动生成）", "Brief summary of the article (optional, auto-generated if empty)"),
    "login_to_comment": ("请先登录才能发表评论", "Please log in to join the discussion."),
    "feedback_text_optional": ("请分享您的想法（可选）", "Please share your thoughts (optional)"),
    "login_to_feedback": ("请先登录后才能提供反馈", "Please log in to provide feedback."),

    # AI Chat
    "ai_chat_title": ("AI专家对话", "AI Expert Chat"),
    "ai_backend": ("当前AI后端", "Current AI Backend"),
    "ai_model": ("模型", "Model"),
    "ai_placeholder": ("请输入您关于广告学的问题", "Please enter your question about advertising"),
    "ai_thinking": ("AI正在思考中", "AI is thinking"),
    "ai_settings": ("AI 设置", "AI Settings"),
    "ai_clear_chat": ("清空对话", "Clear Chat"),
    "ai_switch_backend": ("切换后端", "Switch Backend"),
    "ai_chat_stats": ("对话统计", "Chat Statistics"),
    "ai_message_count": ("消息数量", "Messages"),
    "ai_last_message": ("最后消息", "Last Message"),

    # Language selector
    "language_label": ("语言 / Language", "Language"),

    # Common
    "error_loading_page": ("加载页面时出错", "Error loading page"),
    "login_failed": ("用户名或密码错误", "Username/password is incorrect"),
    "fill_username_password": ("请填写用户名和密码", "Please enter username and password"),
    "username_not_found": ("用户名不存在", "Username not found"),
    "access_denied": ("访问被拒绝", "Access denied"),
    "requires_login": ("请先登录", "Please log in first"),
}


def get_language() -> str:
    """Get current language code ('zh' or 'en'). Defaults to 'zh'."""
    if "app_language" not in st.session_state:
        st.session_state.app_language = "zh"
    return st.session_state.app_language


def t(key: str) -> str:
    """Translate a key to the current language."""
    lang = get_language()
    if key not in TRANSLATIONS:
        return key
    return TRANSLATIONS[key][0] if lang == "zh" else TRANSLATIONS[key][1]


def render_language_selector() -> None:
    """Render a language toggle in the sidebar."""
    current = get_language()
    with st.sidebar:
        st.markdown("#### 🌐 Language")
        lang_col1, lang_col2 = st.columns(2)
        with lang_col1:
            if st.button(
                "中文" if current != "zh" else "● 中文",
                use_container_width=True,
                type="primary" if current == "zh" else "secondary",
                key="lang_zh_btn",
            ):
                st.session_state.app_language = "zh"
                st.rerun()
        with lang_col2:
            if st.button(
                "EN" if current != "en" else "● English",
                use_container_width=True,
                type="primary" if current == "en" else "secondary",
                key="lang_en_btn",
            ):
                st.session_state.app_language = "en"
                st.rerun()
