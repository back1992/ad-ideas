"""
Mobile API for 广告思想简史 Platform

FastAPI backend that serves the same data as the Streamlit app,
optimized for mobile clients (Capacitor wrapper).
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path so we can import modules
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.database import get_database_manager
from modules.auth import AuthManager, get_auth_manager
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="广告思想简史 API",
    description="Mobile API for the Advertising History Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

_db_manager = None
_auth_manager = None


def get_db():
    global _db_manager
    if _db_manager is None:
        _db_manager = get_database_manager()
    return _db_manager


def get_auth():
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = get_auth_manager(db_manager=get_db())
    return _auth_manager


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def get_current_user(x_token: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Validate a bearer token and return user info."""
    if not x_token:
        return None
    try:
        # Token is the username (simple approach for now)
        auth = get_auth()
        config_path = PROJECT_ROOT / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=SafeLoader)
        username = x_token
        users = config['credentials']['usernames']
        if username not in users:
            return None
        return {
            "username": username,
            "name": users[username]['name'],
            "role": users[username].get('role', 'student'),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    name: str
    role: str


class CommentRequest(BaseModel):
    target_type: str
    target_id: str
    content: str
    parent_id: Optional[int] = None


class FeedbackRequest(BaseModel):
    target_type: str
    target_id: str
    feedback_type: str
    feedback_value: int
    feedback_text: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ad-ideas-api"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """Authenticate user and return a token."""
    auth = get_auth()
    config_path = PROJECT_ROOT / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=SafeLoader)

    users = config['credentials']['usernames']
    if req.username not in users:
        raise HTTPException(status_code=401, detail="Username not found")

    stored_password = users[req.username]['password']
    pw_match = False
    try:
        if stauth.Hasher([req.password]).generate()[0] == stored_password:
            pw_match = True
    except Exception:
        pass
    if not pw_match and req.password == stored_password:
        pw_match = True

    if not pw_match:
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Use username as simple token
    return LoginResponse(
        token=req.username,
        name=users[req.username]['name'],
        role=users[req.username].get('role', 'student'),
    )


@app.get("/api/timeline")
def get_timeline():
    """Get advertising timeline events."""
    db = get_db()
    query = "SELECT * FROM timeline_events ORDER BY year ASC"
    df = db.execute_query(query, ())
    if df.empty:
        return []
    records = df.to_dict(orient='records')
    # Convert timestamps to ISO strings
    for r in records:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])
    return records


@app.get("/api/stars")
def get_stars():
    """Get top 100 advertising stars."""
    db = get_db()
    query = "SELECT * FROM advertising_stars ORDER BY ranking ASC LIMIT 100"
    df = db.execute_query(query, ())
    if df.empty:
        return []
    records = df.to_dict(orient='records')
    for r in records:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])
    return records


@app.get("/api/campaigns")
def get_campaigns():
    """Get top 100 advertising campaigns."""
    db = get_db()
    query = "SELECT * FROM classic_ads ORDER BY ranking ASC LIMIT 100"
    df = db.execute_query(query, ())
    if df.empty:
        return []
    records = df.to_dict(orient='records')
    for r in records:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])
    return records


@app.get("/api/campaigns/{campaign_id}")
def get_campaign(campaign_id: int):
    """Get a single campaign detail."""
    db = get_db()
    query = "SELECT * FROM classic_ads WHERE id = ?"
    df = db.execute_query(query, (campaign_id,))
    if df.empty:
        raise HTTPException(status_code=404, detail="Campaign not found")
    record = df.iloc[0].to_dict()
    if record.get('created_at'):
        record['created_at'] = str(record['created_at'])
    return record


@app.get("/api/articles")
def get_articles(status: str = "published"):
    """Get published articles."""
    db = get_db()
    query = "SELECT * FROM articles WHERE status = ? ORDER BY created_at DESC"
    df = db.execute_query(query, (status,))
    if df.empty:
        return []
    records = df.to_dict(orient='records')
    for r in records:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])
        if r.get('published_at'):
            r['published_at'] = str(r['published_at'])
    return records


@app.get("/api/articles/{article_id}")
def get_article(article_id: int):
    """Get a single article."""
    db = get_db()
    query = "SELECT * FROM articles WHERE id = ?"
    df = db.execute_query(query, (article_id,))
    if df.empty:
        raise HTTPException(status_code=404, detail="Article not found")
    record = df.iloc[0].to_dict()
    if record.get('created_at'):
        record['created_at'] = str(record['created_at'])
    if record.get('published_at'):
        record['published_at'] = str(record['published_at'])
    return record


@app.get("/api/search")
def search(q: str, target: str = "all"):
    """Search across platform content."""
    db = get_db()
    results = {"articles": [], "timeline": [], "stars": [], "campaigns": []}

    if target in ("all", "articles"):
        query = "SELECT * FROM articles WHERE status = 'published' AND (title LIKE ? OR content LIKE ? OR excerpt LIKE ?)"
        pattern = f"%{q}%"
        df = db.execute_query(query, (pattern, pattern, pattern))
        if not df.empty:
            records = df.to_dict(orient='records')
            for r in records:
                if r.get('created_at'):
                    r['created_at'] = str(r['created_at'])
            results["articles"] = records

    if target in ("all", "timeline"):
        query = "SELECT * FROM timeline_events WHERE event LIKE ? OR description LIKE ?"
        pattern = f"%{q}%"
        df = db.execute_query(query, (pattern, pattern))
        if not df.empty:
            records = df.to_dict(orient='records')
            for r in records:
                if r.get('created_at'):
                    r['created_at'] = str(r['created_at'])
            results["timeline"] = records

    return results


@app.get("/api/comments")
def get_comments(target_type: str, target_id: str):
    """Get comments for a target."""
    db = get_db()
    query = """
        SELECT * FROM comments
        WHERE target_type = ? AND target_id = ? AND is_approved = 1
        ORDER BY created_at ASC
    """
    df = db.execute_query(query, (target_type, target_id))
    if df.empty:
        return []
    records = df.to_dict(orient='records')
    for r in records:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])
    return records


@app.post("/api/comments")
def add_comment(req: CommentRequest, user: Optional[Dict] = Depends(get_current_user)):
    """Add a comment (requires authentication)."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    db = get_db()
    query = """
        INSERT INTO comments (username, target_type, target_id, content, parent_id, is_approved, created_at)
        VALUES (?, ?, ?, ?, ?, 0, ?)
    """
    now = datetime.now().isoformat()
    db.execute_update(query, (
        user['username'],
        req.target_type,
        req.target_id,
        req.content,
        req.parent_id,
        now,
    ))

    return {"status": "pending_approval", "message": "Comment submitted for review"}


@app.get("/api/feedback")
def get_feedback(target_type: str, target_id: str):
    """Get feedback stats for a target."""
    db = get_db()
    query = """
        SELECT feedback_type, feedback_value, COUNT(*) as count
        FROM user_feedback
        WHERE target_type = ? AND target_id = ?
        GROUP BY feedback_type, feedback_value
    """
    df = db.execute_query(query, (target_type, target_id))
    if df.empty:
        return {"thumbs_up": 0, "thumbs_down": 0, "ratings": []}

    result = {"thumbs_up": 0, "thumbs_down": 0, "ratings": []}
    for _, row in df.iterrows():
        if row['feedback_type'] == 'thumbs':
            if row['feedback_value'] == 1:
                result["thumbs_up"] = int(row['count'])
            else:
                result["thumbs_down"] = int(row['count'])
        elif row['feedback_type'] == 'rating':
            result["ratings"].append({
                "value": int(row['feedback_value']),
                "count": int(row['count']),
            })
    return result


@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest, user: Optional[Dict] = Depends(get_current_user)):
    """Submit feedback (requires authentication)."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    db = get_db()
    # Check for duplicate
    check_query = """
        SELECT id FROM user_feedback
        WHERE username = ? AND target_type = ? AND target_id = ? AND feedback_type = ?
    """
    existing = db.execute_query(check_query, (
        user['username'], req.target_type, req.target_id, req.feedback_type
    ))
    if not existing.empty:
        raise HTTPException(status_code=409, detail="Feedback already submitted")

    query = """
        INSERT INTO user_feedback (username, target_type, target_id, feedback_type, feedback_value, feedback_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    now = datetime.now().isoformat()
    db.execute_update(query, (
        user['username'],
        req.target_type,
        req.target_id,
        req.feedback_type,
        req.feedback_value,
        req.feedback_text,
        now,
    ))

    return {"status": "ok", "message": "Feedback submitted"}


# ---------------------------------------------------------------------------
# Industry data (for charts)
# ---------------------------------------------------------------------------

@app.get("/api/industry-data")
def get_industry_data():
    """Get industry data for charts."""
    db = get_db()
    query = "SELECT * FROM industry_data ORDER BY year ASC"
    df = db.execute_query(query, ())
    if df.empty:
        return []
    records = df.to_dict(orient='records')
    for r in records:
        if r.get('year'):
            r['year'] = int(r['year']) if str(r['year']).isdigit() else str(r['year'])
    return records
