"""
Pydantic AI agent for the advertising history tutoring system.

This module creates and configures the AI agent that serves as a
research assistant for the 广告思想简史 platform.

Usage:
    from modules.ai_agent import create_ad_history_agent
    agent = create_ad_history_agent(db_manager)
    result = agent.run_sync("介绍万宝路牛仔广告的历史意义")
    print(result.output.answer)
"""

import os
import logging
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from modules.ai_models import ChatResponse
from modules.ai_tools import register_tools
from utils.logger import create_logger

logger = create_logger('AIAgent')

SYSTEM_PROMPT = """\
你是一位广告学领域的专家助手，服务于"广告思想简史"教学平台。

你的职责：
1. 回答关于广告历史、理论、经典案例的问题
2. 帮助学生理解广告思想的发展脉络
3. 推荐平台上的相关文章和内容
4. 引用具体的历史事件和人物

使用工具的指引：
- 当用户的问题涉及平台内容时，先用 search_articles 搜索相关文章
- 当用户想了解某个话题的深入内容时，用 get_article_detail 获取全文
- 当用户想要推荐时，用 get_recommendations 或 get_trending_articles
- 当用户按分类浏览时，用 get_articles_by_category

回答要求：
- 使用简体中文
- 准确、专业、有见地
- 当引用平台文章时，在 sources 字段列出文章标题
- 在 follow_up_questions 中提供 2-3 个延伸问题
- 当不确定时，明确说明
"""

# Mapping from provider name to pydantic-ai model string prefix
_PROVIDER_MODEL_PREFIXES = {
    'openai': 'openai',
    'groq': 'groq',
    'gemini': 'gemini',
    'ollama': 'ollama',
    'bedrock': 'bedrock',
    'mistral': 'mistral',
}


def _resolve_model_string() -> str:
    """Build the pydantic-ai model string from environment variables.

    Returns a string like 'groq:llama-3.3-70b-versatile' that pydantic-ai
    can resolve via infer_model().
    """
    provider = os.getenv('PYDANTIC_AI_PROVIDER', 'groq').lower()
    model_name = os.getenv('PYDANTIC_AI_MODEL', '')

    prefix = _PROVIDER_MODEL_PREFIXES.get(provider)
    if not prefix:
        raise ValueError(
            f"Unknown PYDANTIC_AI_PROVIDER '{provider}'. "
            f"Supported: {', '.join(_PROVIDER_MODEL_PREFIXES)}"
        )

    if not model_name:
        defaults = {
            'openai': 'gpt-4o',
            'groq': 'llama-3.3-70b-versatile',
            'gemini': 'gemini-1.5-flash',
            'ollama': 'llama3.2:latest',
            'bedrock': 'us.anthropic.claude-3-sonnet-20240229-v1:0',
            'mistral': 'mistral-large-latest',
        }
        model_name = defaults.get(provider, 'gpt-4o')

    return f"{prefix}:{model_name}"


def create_ad_history_agent(
    db_manager,
    model: Optional[str] = None,
    use_test_model: bool = False,
) -> Agent:
    """Create the advertising history tutor agent.

    Args:
        db_manager: DatabaseManager instance for tool data access.
        model: Optional model string (e.g. 'groq:llama-3.3-70b-versatile').
               If None, reads from PYDANTIC_AI_PROVIDER / PYDANTIC_AI_MODEL env vars.
        use_test_model: If True, use pydantic-ai's TestModel (for unit tests).

    Returns:
        A configured pydantic_ai.Agent with platform tools registered.
    """
    if use_test_model:
        resolved_model = TestModel()
    elif model:
        resolved_model = model
    else:
        resolved_model = _resolve_model_string()

    agent = Agent(
        model=resolved_model,
        output_type=ChatResponse,
        system_prompt=SYSTEM_PROMPT,
        name="ad_history_tutor",
    )

    register_tools(agent, db_manager)

    logger.info(
        f"Created ad_history_tutor agent with model: "
        f"{'test' if use_test_model else resolved_model}"
    )

    return agent
