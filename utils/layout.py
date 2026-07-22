"""Shared layout utilities for consistent page design across the app."""

import streamlit as st
from utils.i18n import t


# ---------------------------------------------------------------------------
# Icon constants
# ---------------------------------------------------------------------------

ICONS = {
    "home": "📚",
    "search": "🔍",
    "article_create": "✍️",
    "article_list": "📝",
    "article_view": "📄",
    "timeline": "📅",
    "stars": "⭐",
    "campaigns": "🏆",
    "data": "📈",
    "chat": "💬",
    "moderation": "🔧",
    "analytics": "📊",
    "feedback": "💭",
    "discussion": "💬",
    "settings": "⚙️",
    "user": "👤",
    "logout": "🚪",
    "login": "🔐",
    "info": "💡",
    "welcome": "👋",
    "ai": "🤖",
}


# ---------------------------------------------------------------------------
# Page layout helpers
# ---------------------------------------------------------------------------

def page_title(icon: str, zh: str, en: str) -> None:
    """Render a consistent page heading: `# {icon} 中文 / English`."""
    icon_char = ICONS.get(icon, "")
    if icon_char:
        st.title(f"{icon_char} {zh} / {en}")
    else:
        st.title(f"{zh} / {en}")


def section(zh: str, en: str) -> None:
    """Render a `##` section heading."""
    st.markdown(f"## {zh} / {en}")


def page_header(icon: str, zh: str, en: str, subtitle: str = "") -> None:
    """Render a styled page header banner."""
    icon_char = ICONS.get(icon, "")
    sub = f'<p>{subtitle}</p>' if subtitle else f'<p>{en}</p>'
    st.markdown(f"""
    <div class="page-header">
        <h1>{icon_char} {zh}</h1>
        {sub}
    </div>
    """, unsafe_allow_html=True)


def subsection(zh: str, en: str) -> None:
    """Render a `###` sub-section heading."""
    st.markdown(f"### {zh} / {en}")


def divider() -> None:
    """Render a horizontal rule."""
    st.divider()


def caption(text: str) -> None:
    """Render small metadata text."""
    st.markdown(f"<small style='color:#6b7280'>{text}</small>", unsafe_allow_html=True)


def info_box(text: str, icon: str = "💡") -> None:
    """Render an info message (replaces st.info for styled look)."""
    st.info(f"{icon} {text}")


def content_card(title: str, author: str = "", category: str = "",
                 excerpt: str = "", metrics: dict | None = None,
                 key: str = "") -> None:
    """Render a content card (article, campaign, etc.) in a container."""
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{title}**")
            parts = []
            if author:
                parts.append(f"👤 {author}")
            if category:
                parts.append(f"📁 {category}")
            if parts:
                caption(" | ".join(parts))
            if excerpt:
                st.markdown(f"> {excerpt[:200]}")
        with col2:
            if metrics:
                for label, value in metrics.items():
                    st.metric(label, value)


def timeline_entry(period: str, events: list[str]) -> None:
    """Render a timeline period with events in a structured card layout."""
    with st.container(border=True):
        st.markdown(f"### {period}")
        for event in events:
            # Split year from description if possible
            parts = event.split(" ", 1)
            if parts[0].replace(".", "").replace(",", "").isdigit() or \
               any(ch.isdigit() for ch in parts[0][:4]):
                st.markdown(f"**{parts[0]}** {parts[1] if len(parts) > 1 else ''}")
            else:
                st.markdown(f"- {event}")


# ---------------------------------------------------------------------------
# Reusable feedback + comment section
# ---------------------------------------------------------------------------

def render_feedback_and_comments(target_type: str, target_id: str,
                                 feedback_type: str = "thumbs",
                                 show_feedback: bool = True,
                                 show_comments: bool = True) -> None:
    """Unified feedback + comment section used across all content pages.

    This replaces the copy-paste pattern that existed in homepage.py,
    pages.py, and individual module display functions.
    """
    from modules.database import get_database_manager
    from modules.feedback import get_feedback_system
    from modules.comments import get_comment_system

    if not st.session_state.get("authentication_status"):
        info_box(t('login_to_feedback'))
        return

    db_manager = get_database_manager()
    feedback_system = get_feedback_system(db_manager)
    comment_system = get_comment_system(db_manager)

    if show_feedback:
        divider()
        subsection("您的反馈", "Your Feedback")
        feedback_system.collect_feedback(
            target_type=target_type,
            target_id=target_id,
            feedback_type=feedback_type,
            optional_text_label=t('feedback_text_optional'),
        )

    if show_comments:
        divider()
        subsection("讨论区", "Discussion")
        comment_system.display_comments_section(
            target_type=target_type,
            target_id=target_id,
        )
