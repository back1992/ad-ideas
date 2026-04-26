# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**广告思想简史** (Advertising History Platform) — a Streamlit-based educational platform for teaching advertising history. China-hosted, SQLite-backed (no Google APIs).

## Deployment

Production: https://ad-ideas.streamlit.app/ (Streamlit Cloud)

## Key Commands

```bash
# Run the app
streamlit run streamlit_app.py

# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_database_properties.py

# Run tests with verbose output
pytest tests/ -v
```

## Architecture

### Entry Point
- `streamlit_app.py` — main app: login flow, sidebar navigation, page routing based on user role
- `homepage.py` — landing page content
- `pages.py` — timeline, superstar, and plotting data pages
- `classic_ad_100.py` — "Top 100 Campaigns" page

### Module System (`modules/`)
All modules follow a singleton pattern with `get_*()` factory functions and depend on `DatabaseManager`:

| Module | Purpose |
|--------|---------|
| `database.py` | `DatabaseManager` — SQLite wrapper with `execute_query`, `execute_update`, pandas integration |
| `auth.py` | `AuthManager` — streamlit-authenticator + role-based access (admin/professor/student) |
| `articles.py` | Article CRUD, moderation, and display |
| `comments.py` | Threaded comments with moderation |
| `feedback.py` | Thumbs up/down + star ratings via `streamlit-feedback` |
| `search.py` | Full-text search across articles, timeline, figures, campaigns |
| `analytics.py` | Admin dashboard with Plotly visualizations |
| `moderation.py` | Unified moderation for articles + comments |
| `activity.py` | User activity logging |
| `recommendations.py` | Content recommendation engine |
| `user_management.py` | Role management and user admin |
| `ai_chat.py` | AI chat backend abstraction (Gemini/Ollama/Azure) |

### Chat Integrations
- `chat_openwebui.py` — primary chat interface (OpenWebUI API, currently used in main app)
- `chat_ollama.py` — local Ollama integration
- `chat_gemini.py` — Google Gemini integration
- `chat_ad.py` — ad-specific chat

### Utilities (`utils/`)
- `db.py` — legacy Google Sheets compatibility layer (wraps `DatabaseManager`)
- `constances.py` — constants
- `chart.py` — charting utilities

### Database
SQLite at `platform.db`. Tables: `user_feedback`, `comments`, `articles`, `content_stats`, `user_activity`. Schema is auto-created by `DatabaseManager.init_database()` on first access.

### Testing
Tests use **Hypothesis** for property-based testing (`hypothesis.stateful.RuleBasedStateMachine` for workflow tests). Test files are per-module (e.g., `test_auth_properties.py` for `auth.py`).

### Configuration
- `config.yaml` — user credentials with bcrypt-hashed passwords and role assignments
- `.env` — environment variables (OpenWebUI URL, API keys, AI backend selection)

### Dependency Injection Pattern
Modules use global singletons initialized via `get_*()` functions. The main app (`streamlit_app.py`) initializes all systems at startup and passes them through. `init_database_systems()` is cached via `@st.cache_resource`; auth-dependent systems are NOT cached due to Streamlit widget state conflicts.