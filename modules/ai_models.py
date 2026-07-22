"""
Pydantic output models for the AI agent.

These models define structured outputs for the Pydantic AI agent,
ensuring typed, validated responses from the LLM.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ContentCategory(str, Enum):
    """Content categories available on the platform."""
    ARTICLE = "article"
    TIMELINE = "timeline"
    FIGURE = "figure"
    CAMPAIGN = "campaign"
    THEORY = "theory"
    GENERAL = "general"


class ArticleSummary(BaseModel):
    """Structured summary of an article or topic."""
    title: str = Field(description="Title or topic being summarized")
    summary: str = Field(description="2-3 sentence summary in Chinese")
    key_figures: list[str] = Field(
        default_factory=list, description="Key people mentioned"
    )
    key_campaigns: list[str] = Field(
        default_factory=list, description="Key campaigns mentioned"
    )
    era: Optional[str] = Field(
        default=None, description="Historical period, e.g. '1950s', '明代'"
    )
    related_topics: list[str] = Field(
        default_factory=list, description="Suggested follow-up topics"
    )


class SearchIntent(BaseModel):
    """Parsed user search intent from natural language."""
    query: str = Field(description="Extracted search query")
    content_type: Optional[ContentCategory] = Field(
        default=None, description="Target content type"
    )
    time_period: Optional[str] = Field(
        default=None, description="Historical period filter"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in intent parsing"
    )


class RecommendationItem(BaseModel):
    """A single AI-enhanced recommendation with explanation."""
    article_id: int
    title: str
    reason: str = Field(description="Why this is recommended, in Chinese")
    relevance_score: float = Field(ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Standardized chat response with optional structured data."""
    answer: str = Field(description="Natural language answer in Chinese")
    sources: list[str] = Field(
        default_factory=list, description="Article titles referenced"
    )
    follow_up_questions: list[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )
    summary: Optional[ArticleSummary] = Field(
        default=None, description="Structured summary if applicable"
    )
