# Pydantic AI Integration Design Document

**Project**: 广告思想简史 (Advertising History Platform)  
**Date**: 2026-07-21  
**Status**: Draft  

---

## 1. Current State

### AI Chat Architecture

The platform's AI layer (`modules/ai_chat.py`) is a hand-rolled multi-backend abstraction:

```
modules/ai_chat.py  →  AIChat class
    ├── _init_gemini()       → google-generativeai
    ├── _init_ollama()       → chat_ollama.OllamaChat
    ├── _init_azure_openai() → openai.AzureOpenAI
    ├── _init_groq()         → openai.OpenAI (Groq endpoint)
    └── _init_openwebui()    → requests (OpenWebUI API)
```

**Pain points**:
- ~200 lines of per-backend init/error-handling code
- No structured outputs — all responses are raw strings
- Chat is simple Q&A with a static system prompt; no tool use or data access
- Adding a new backend requires modifying `AIChat` directly (open/closed violation)
- No conversation memory beyond in-session `st.session_state` list
- `langchain` and `llama-index` are already in `requirements.txt` but unused — suggests prior RAG experiments that were abandoned

### What Exists Today

| Component | File | AI-aware? |
|-----------|------|-----------|
| Chat | `modules/ai_chat.py`, `chat_openwebui.py` | Yes — multi-backend LLM |
| Search | `modules/search.py` | No — SQL LIKE queries |
| Recommendations | `modules/recommendations.py` | No — tag/category scoring |
| Articles | `modules/articles.py` | No — CRUD |
| Database | `modules/database.py` | No — SQLite wrapper |

---

## 2. Goals

1. **Unify backend management** — single interface for all LLM providers, no manual branching
2. **Structured outputs** — typed, validated responses for recommendations, summaries, and Q&A
3. **Tool-using agent** — the chat can query the database, search articles, and look up timeline events, turning it from a generic Q&A into an *advertising history research assistant*
4. **Incremental adoption** — the current `chat_interface()` keeps working; Pydantic AI is introduced as a new backend, not a rewrite
5. **China-hosted compatibility** — must work with Ollama (local) and Groq; no hard dependency on Google/OpenAI APIs

---

## 3. Why Pydantic AI (vs. Alternatives)

| Criterion | Pydantic AI | LangChain (already in deps) | llama-index (already in deps) | Raw code (current) |
|-----------|-------------|----------------------------|-------------------------------|-------------------|
| Multi-provider unification | ✅ Built-in (OpenAI, Gemini, Groq, Ollama, Bedrock, Mistral) | ✅ Via chat model abstractions | ⚠️ LLM-focused, not general | ❌ Manual |
| Structured outputs | ✅ First-class (`result_type=T`) | ⚠️ Via output parsers | ⚠️ Via output parsers | ❌ Manual JSON parsing |
| Tool/agent system | ✅ Native `@agent.tool` decorator | ✅ Tool + AgentExecutor | ✅ Tool + ReActAgent | ❌ None |
| Dependency footprint | ✅ Single lib, ~50KB | ❌ Heavy transitive deps | ❌ Heavy transitive deps | ✅ None |
| Learning curve | ✅ Low (Pydantic + FastAPI-like) | ⚠️ Steep (chains, memory, callbacks) | ⚠️ Moderate | ✅ None |
| Streaming | ✅ Native | ✅ Native | ✅ Native | ⚠️ Per-backend |

**Recommendation**: Adopt Pydantic AI as the primary agent framework. Consider removing `langchain` and `llama-index` from `requirements.txt` if confirmed unused — they add significant install time and dependency conflicts for zero value.

---

## 4. Architecture Design

### 4.1 New Module Layout

```
modules/
├── ai_chat.py              # Existing — kept for backward compat during migration
├── ai_agent.py             # NEW — Pydantic AI agent definition
├── ai_models.py            # NEW — Pydantic models for structured outputs
├── ai_tools.py             # NEW — Tool functions (db query, search, timeline lookup)
└── ...
```

### 4.2 Structured Output Models (`modules/ai_models.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ContentCategory(str, Enum):
    TIMELINE = "timeline"
    FIGURE = "figure"
    CAMPAIGN = "campaign"
    THEORY = "theory"
    GENERAL = "general"

class ArticleSummary(BaseModel):
    """Structured summary of an article or topic."""
    title: str = Field(description="Title or topic being summarized")
    summary: str = Field(description="2-3 sentence summary in Chinese")
    key_figures: list[str] = Field(default_factory=list, description="Key people mentioned")
    key_campaigns: list[str] = Field(default_factory=list, description="Key campaigns mentioned")
    era: Optional[str] = Field(default=None, description="Historical period, e.g. '1950s', '明代'")
    related_topics: list[str] = Field(default_factory=list, description="Suggested follow-up topics")

class SearchIntent(BaseModel):
    """Parsed user search intent from natural language."""
    query: str = Field(description="Extracted search query")
    content_type: Optional[ContentCategory] = Field(default=None, description="Target content type")
    time_period: Optional[str] = Field(default=None, description="Historical period filter")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in intent parsing")

class RecommendationResult(BaseModel):
    """AI-enhanced recommendation with explanation."""
    article_id: int
    title: str
    reason: str = Field(description="Why this is recommended, in Chinese")
    relevance_score: float = Field(ge=0.0, le=1.0)

class ChatResponse(BaseModel):
    """Standardized chat response with optional structured data."""
    answer: str = Field(description="Natural language answer in Chinese")
    sources: list[str] = Field(default_factory=list, description="Article titles referenced")
    follow_up_questions: list[str] = Field(default_factory=list, description="Suggested follow-ups")
    summary: Optional[ArticleSummary] = Field(default=None, description="Structured summary if applicable")
```

### 4.3 Agent Tools (`modules/ai_tools.py`)

Tools wrap existing modules so the agent can access platform data:

```python
from modules.database import DatabaseManager
from modules.search import SearchSystem
from modules.recommendations import RecommendationEngine

def create_agent_tools(db_manager: DatabaseManager):
    """Factory that returns tool functions bound to live module instances."""

    search_system = SearchSystem(db_manager)
    rec_engine = RecommendationEngine(db_manager)

    async def search_articles(query: str, limit: int = 5) -> str:
        """Search articles by keyword. Returns titles, excerpts, and categories."""
        results = search_system.search(query, content_types=['articles'], limit=limit)
        # Format as readable string for the LLM
        ...

    async def get_timeline_events(era: str = "") -> str:
        """Look up historical timeline events, optionally filtered by era."""
        ...

    async def get_article_detail(article_id: int) -> str:
        """Fetch full article content by ID."""
        ...

    async def get_recommendations(topic: str, limit: int = 5) -> str:
        """Get article recommendations related to a topic."""
        ...

    return [search_articles, get_timeline_events, get_article_detail, get_recommendations]
```

### 4.4 Agent Definition (`modules/ai_agent.py`)

```python
from pydantic_ai import Agent
from modules.ai_models import ChatResponse, ArticleSummary

SYSTEM_PROMPT = """你是一位广告学领域的专家助手，服务于"广告思想简史"教学平台。

你的职责：
1. 回答关于广告历史、理论、经典案例的问题
2. 帮助学生理解广告思想的发展脉络
3. 推荐平台上的相关文章和内容
4. 引用具体的历史事件和人物

回答要求：
- 使用简体中文
- 准确、专业、有见地
- 当不确定时，明确说明
- 适当推荐平台上的相关学习资源
"""

def create_ad_history_agent(model, tools) -> Agent:
    """Create the advertising history tutor agent."""
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        result_type=ChatResponse,
        deps_type=dict,  # session context (username, role, etc.)
    )

    for tool in tools:
        agent.tool(tool)

    return agent
```

### 4.5 Integration with `ai_chat.py`

The existing `AIChat` class gains a new backend option:

```python
# In modules/ai_chat.py, AIChat class:

AVAILABLE_BACKENDS = ['gemini', 'ollama', 'azure_openai', 'groq', 'openwebui', 'pydantic_ai']

def _init_pydantic_ai(self):
    """Initialize Pydantic AI agent backend."""
    from modules.ai_agent import create_ad_history_agent
    from modules.ai_tools import create_agent_tools

    db_manager = get_database_manager()
    tools = create_agent_tools(db_manager)

    # Map env var to Pydantic AI model
    provider = os.getenv('PYDANTIC_AI_PROVIDER', 'groq')
    model_name = os.getenv('PYDANTIC_AI_MODEL', 'llama-3.3-70b-versatile')

    if provider == 'groq':
        from pydantic_ai.models.groq import GroqModel
        model = GroqModel(model_name, api_key=os.getenv('GROQ_API_KEY'))
    elif provider == 'ollama':
        from pydantic_ai.models.ollama import OllamaModel
        model = OllamaModel(model_name, base_url=os.getenv('OLLAMA_BASE_URL'))
    # ... other providers

    agent = create_ad_history_agent(model, tools)
    return {'type': 'pydantic_ai', 'agent': agent, 'model': model_name}
```

### 4.6 Streamlit Chat Integration

```python
# In chat_interface(), new branch for pydantic_ai backend:

if backend_info['backend'] == 'pydantic_ai':
    agent = ai_client.client['agent']
    with st.spinner(t('ai_thinking')):
        result = agent.run_sync(
            prompt,
            deps={'username': username, 'role': role}
        )
        response = result.data  # ChatResponse instance
    
    st.markdown(response.answer)
    if response.sources:
        st.caption(f"📚 参考: {', '.join(response.sources)}")
    if response.follow_up_questions:
        st.markdown("**你可能还想了解:**")
        for q in response.follow_up_questions:
            st.markdown(f"- {q}")
```

---

## 5. Data Flow

```
User Input (Streamlit chat)
        │
        ▼
┌──────────────────┐
│   AIChat class   │  ← existing entry point
│  backend switch  │
└──────┬───────────┘
       │ (pydantic_ai branch)
       ▼
┌──────────────────┐
│  Pydantic AI     │
│  Agent           │
│  ┌────────────┐  │
│  │ LLM call   │  │  ← Groq / Ollama / Gemini / etc.
│  │ + tools    │  │
│  └────────────┘  │
└──────┬───────────┘
       │ (tool calls)
       ▼
┌──────────────────────────────────┐
│  Agent Tools                     │
│  ├── search_articles()           │ → modules/search.py → SQLite
│  ├── get_timeline_events()       │ → modules/database.py → SQLite
│  ├── get_article_detail()        │ → modules/articles.py → SQLite
│  └── get_recommendations()       │ → modules/recommendations.py → SQLite
└──────────────────────────────────┘
       │
       ▼
  Structured ChatResponse (Pydantic validated)
       │
       ▼
  Streamlit UI rendering
```

---

## 6. Environment Configuration

Add to `.env`:

```bash
# Pydantic AI backend (new)
AI_BACKEND=pydantic_ai
PYDANTIC_AI_PROVIDER=groq          # groq | ollama | gemini | openai
PYDANTIC_AI_MODEL=llama-3.3-70b-versatile

# Reuses existing keys:
# GROQ_API_KEY=...
# OLLAMA_BASE_URL=...
# GEMINI_API_KEY=...
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1)
- Add `pydantic-ai` to `requirements.txt`
- Create `modules/ai_models.py` with Pydantic output models
- Create `modules/ai_tools.py` wrapping existing search/recommendations
- Create `modules/ai_agent.py` with agent definition
- **Deliverable**: Agent can be instantiated and run in isolation (unit test)

### Phase 2: Backend Integration (Week 2)
- Add `pydantic_ai` as a new backend in `modules/ai_chat.py`
- Wire up Streamlit chat interface for the new backend
- Add `.env` configuration
- **Deliverable**: Chat works end-to-end via Pydantic AI backend

### Phase 3: Enhanced Features (Week 3)
- Structured output rendering in Streamlit (source citations, follow-up questions)
- Conversation memory (persist to SQLite via `user_activity` table)
- Admin UI for switching Pydantic AI provider/model
- **Deliverable**: Rich chat experience with citations and suggestions

### Phase 4: Cleanup & Optimization (Week 4)
- Remove `langchain` and `llama-index` from `requirements.txt` (if confirmed unused)
- Add property-based tests for agent tools (following existing Hypothesis patterns)
- Performance: cache agent tool results in `st.cache_data`
- **Deliverable**: Clean dependency tree, tested, performant

---

## 8. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pydantic AI doesn't support a needed provider | Medium | Fallback to existing backends; agent is one of many |
| Tool calls add latency to chat | Medium | Set tool call timeout; cache frequent queries |
| Structured output parsing fails | Low | Pydantic validation with retry; fallback to raw string |
| Streamlit Cloud resource limits | Low | Ollama not viable on Cloud; use Groq/Gemini for production |
| Breaking existing chat during migration | Low | New backend is additive; old backends remain functional |
| China network restrictions | Medium | Default to Ollama (local) for dev; Groq for production |

---

## 9. Dependencies

### Add
```
pydantic-ai>=0.2.0
```

### Remove (after confirming unused)
```
langchain==1.3.14
llama-index==0.14.23
```

These two packages pull in hundreds of transitive dependencies. Removing them will significantly reduce install time and potential conflicts.

---

## 10. Success Criteria

- [ ] Chat works via Pydantic AI backend with at least Groq and Ollama
- [ ] Agent can search articles and return citations in responses
- [ ] Structured `ChatResponse` renders with sources and follow-up questions
- [ ] All existing backends continue to work unchanged
- [ ] `requirements.txt` is leaner (langchain/llama-index removed)
- [ ] Property-based tests cover agent tool functions
- [ ] No increase in Streamlit Cloud cold start time (>5s)
