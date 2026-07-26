"""
Global CSS styles for the 广告思想简史 platform.

Inject via `st.markdown(GLOBAL_CSS, unsafe_allow_html=True)` once at app startup.
"""

GLOBAL_CSS = """
<style>
/* ── Fonts ─────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* ── Reset & base ──────────────────────────────────────────── */
html, body, .stApp {
    font-family: 'Inter', 'Noto Serif SC', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #2D2D2D;
    background: #F8F6F1 !important;
}

/* ── Main content ─────────────────────────────────────────── */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1100px;
}

/* ── Typography ────────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: 'Noto Serif SC', 'Inter', serif !important;
    color: #1B3A5C !important;
    letter-spacing: -0.01em;
}
h1 { font-size: 2.2rem !important; font-weight: 700 !important; }
h2 { font-size: 1.6rem !important; font-weight: 600 !important; }
h3 { font-size: 1.25rem !important; font-weight: 600 !important; }

p, li, span, label {
    font-family: 'Inter', 'Noto Serif SC', sans-serif !important;
    line-height: 1.7;
}

/* ═══════════════════════════════════════════════════════════
   SIDEBAR — high-contrast dark theme
   ═══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B3A5C 0%, #1E4068 50%, #244B73 100%) !important;
}

/* BROAD: Force ALL text inside sidebar to be white */
section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Catch-all: ALL inputs/textareas inside sidebar — dark text on light bg */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    color: #1B3A5C !important;
    -webkit-text-fill-color: #1B3A5C !important;
    background: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] textarea:focus {
    border-color: #C9850A !important;
    outline: none;
}

/* Catch-all: ALL buttons inside sidebar — ensure visible text */
section[data-testid="stSidebar"] button {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    background: #C9850A !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 10px 20px !important;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
}
section[data-testid="stSidebar"] button:hover {
    background: #D99520 !important;
    transform: translateY(-1px);
}

/* Exception: keep placeholders dim */
section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder {
    color: #8B8B8B !important;
}

/* Exception: keep dividers subtle */
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
}

/* Sidebar info/alert boxes */
section[data-testid="stSidebar"] .stAlert {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
}

/* Sidebar text inputs (authenticator fields) */
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stPasswordInput input,
section[data-testid="stSidebar"] input[type="text"],
section[data-testid="stSidebar"] input[type="password"] {
    color: #1B3A5C !important;
    -webkit-text-fill-color: #1B3A5C !important;
    background: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 8px !important;
    font-size: 0.95rem;
    padding: 10px 12px !important;
    transition: border-color 0.2s, background 0.2s;
}
section[data-testid="stSidebar"] .stTextInput input:focus,
section[data-testid="stSidebar"] .stPasswordInput input:focus,
section[data-testid="stSidebar"] input[type="text"]:focus,
section[data-testid="stSidebar"] input[type="password"]:focus {
    border-color: #C9850A !important;
    background: #F5F5F5 !important;
    outline: none;
}

/* Sidebar buttons (including authenticator Login button) */
section[data-testid="stSidebar"] .stButton > button {
    background: #C9850A !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 10px 20px !important;
    width: 100% !important;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #D99520 !important;
    transform: translateY(-1px);
}
section[data-testid="stSidebar"] .stButton > button:active {
    transform: translateY(0);
}

/* Secondary sidebar buttons (language toggle, etc.) */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.5) !important;
}

/* Sidebar radio buttons (navigation) — rounded hover effect */
section[data-testid="stSidebar"] [data-testid="stRadio"] label,
section[data-testid="stSidebar"] .stRadio label {
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 4px;
    transition: background 0.2s;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover,
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.1);
}

/* ═══════════════════════════════════════════════════════════
   CARDS / CONTAINERS
   ═══════════════════════════════════════════════════════════ */
.stContainer[data-border="true"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #E5E1D8 !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    padding: 1.2rem !important;
    transition: box-shadow 0.2s, transform 0.15s;
}
.stContainer[data-border="true"]:hover,
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.06);
    transform: translateY(-1px);
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS (main content)
   ═══════════════════════════════════════════════════════════ */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    padding: 0.4rem 1.2rem;
    transition: all 0.2s;
}
.stButton > button[kind="primary"] {
    background: #1B3A5C;
    border-color: #1B3A5C;
}
.stButton > button[kind="primary"]:hover {
    background: #244B73;
    border-color: #244B73;
}

/* ═══════════════════════════════════════════════════════════
   METRICS
   ═══════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E5E1D8;
    border-radius: 10px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] {
    color: #1B3A5C !important;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════════════ */
.stTabs > div[data-baseweb="tab-list"] { gap: 8px; }
.stTabs > div[data-baseweb="tab-list"] button {
    border-radius: 8px 8px 0 0;
    font-weight: 500;
    color: #6B7280;
}
.stTabs > div[data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #1B3A5C;
    border-bottom: 2px solid #C9850A;
}

/* ══════════════════════════════════════════════════════════
   EXPANDERS
   ══════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    color: #1B3A5C !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    border: 1px solid #E5E1D8 !important;
    padding: 12px 16px !important;
}
.streamlit-expanderHeader:hover { background: #FDF8EE !important; }
.streamlit-expanderContent {
    border: 1px solid #E5E1D8;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 16px;
    background: #FFFFFF;
}

/* ═══════════════════════════════════════════════════════════
   ALERTS (main content)
   ═══════════════════════════════════════════════════════════ */
.stAlert { border-radius: 10px; border: none; }
.stAlert-info { background: #EBF2FA !important; color: #1B3A5C !important; }
.stAlert-success { background: #EEFBF1 !important; }

/* ═══════════════════════════════════════════════════════════
   DIVIDERS
   ═══════════════════════════════════════════════════════════ */
hr { border-color: #E5E1D8 !important; margin: 1.5rem 0; }

/* ═══════════════════════════════════════════════════════════
   DATAFRAMES
   ═══════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #E5E1D8;
}

/* ═══════════════════════════════════════════════════════════
   HERO SECTION
   ═══════════════════════════════════════════════════════════ */
.hero-section {
    background: linear-gradient(135deg, #1B3A5C 0%, #2D5F8A 60%, #C9850A 100%);
    border-radius: 16px;
    padding: 3rem 2.5rem;
    color: #FFFFFF;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 60%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-section h1 {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-size: 2.6rem !important;
    margin-bottom: 0.5rem;
}
.hero-section p, .hero-section span {
    color: rgba(255,255,255,0.92) !important;
    font-size: 1.1rem;
}

/* ═══════════════════════════════════════════════════════════
   PAGE HEADER BANNER
   ═══════════════════════════════════════════════════════════ */
.page-header {
    background: linear-gradient(135deg, #1B3A5C 0%, #2D5F8A 100%);
    border-radius: 14px;
    padding: 2rem 2.5rem;
    color: #FFFFFF;
    margin-bottom: 1.5rem;
}
.page-header h1 { color: #FFFFFF !important; margin-bottom: 0.3rem; }
.page-header p { color: rgba(255,255,255,0.8) !important; margin: 0; }

/* ═══════════════════════════════════════════════════════════
   TIMELINE
   ═══════════════════════════════════════════════════════════ */
.timeline-period {
    position: relative;
    padding-left: 2rem;
    margin-bottom: 1.5rem;
    border-left: 3px solid #C9850A;
}
.timeline-period h3 { color: #1B3A5C; margin-bottom: 0.8rem; }

/* ═══════════════════════════════════════════════════════════
   QUOTE CARDS
   ═══════════════════════════════════════════════════════════ */
.quote-card {
    background: #FDF8EE;
    border-left: 4px solid #C9850A;
    border-radius: 0 10px 10px 0;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-style: italic;
}
.quote-card .attribution {
    font-style: normal;
    font-weight: 600;
    color: #1B3A5C;
    margin-top: 0.5rem;
    font-size: 0.9rem;
}

/* ═══════════════════════════════════════════════════════════
   CHAPTER LIST
   ═══════════════════════════════════════════════════════════ */
.chapter-item {
    padding: 10px 16px;
    border-radius: 8px;
    margin: 4px 0;
    background: #FFFFFF;
    border: 1px solid #E5E1D8;
    transition: all 0.15s;
}
.chapter-item:hover {
    background: #FDF8EE;
    border-color: #C9850A;
}

/* ═══════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #F0EDE6; }
::-webkit-scrollbar-thumb { background: #C4BFB4; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #A39E93; }

/* ═══════════════════════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .hero-section { padding: 2rem 1.5rem; }
    .hero-section h1 { font-size: 1.8rem !important; }
    .main .block-container { padding-top: 1rem; }
}
</style>
"""


def inject_styles():
    """Inject the global CSS into the Streamlit app. Call once at startup."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
