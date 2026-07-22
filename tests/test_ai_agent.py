"""
Tests for Pydantic AI agent integration.

Validates:
- Agent instantiation with TestModel
- Tool registration and schema correctness
- Tool execution against an in-memory database
- Structured ChatResponse output
- AIChat pydantic_ai backend method
"""

import os
import shutil
import tempfile

import pytest

from modules.database import DatabaseManager
from modules.ai_models import ChatResponse, ArticleSummary, ContentCategory
from modules.ai_agent import create_ad_history_agent
from modules.ai_tools import register_tools


class TestAIModels:
    """Tests for Pydantic output models."""

    def test_chat_response_defaults(self):
        response = ChatResponse(answer="测试回答")
        assert response.answer == "测试回答"
        assert response.sources == []
        assert response.follow_up_questions == []
        assert response.summary is None

    def test_chat_response_full(self):
        summary = ArticleSummary(
            title="万宝路广告",
            summary="万宝路牛仔广告是20世纪最成功的广告活动之一。",
            key_figures=["Leo Burnett"],
            key_campaigns=["Marlboro Man"],
            era="1950s",
            related_topics=["品牌重塑", "烟草广告"],
        )
        response = ChatResponse(
            answer="详细介绍",
            sources=["万宝路广告史"],
            follow_up_questions=["万宝路如何从女性品牌转型？"],
            summary=summary,
        )
        assert response.summary.title == "万宝路广告"
        assert len(response.summary.key_figures) == 1
        assert response.summary.era == "1950s"

    def test_content_category_values(self):
        assert ContentCategory.ARTICLE.value == "article"
        assert ContentCategory.CAMPAIGN.value == "campaign"
        assert ContentCategory.TIMELINE.value == "timeline"


class TestAIAgentCreation:
    """Tests for agent instantiation."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_agent.db")
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_agent_with_test_model(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        assert agent is not None
        assert agent.name == "ad_history_tutor"

    def test_agent_has_tools_registered(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        tools = agent._function_toolset.tools
        tool_names = set(tools.keys())
        expected_tools = {
            'search_articles',
            'get_article_detail',
            'get_recommendations',
            'get_trending_articles',
            'get_articles_by_category',
        }
        assert expected_tools.issubset(tool_names), (
            f"Missing tools: {expected_tools - tool_names}"
        )

    def test_agent_run_produces_structured_output(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        result = agent.run_sync("你好")
        assert isinstance(result.output, ChatResponse)
        assert isinstance(result.output.answer, str)
        assert isinstance(result.output.sources, list)
        assert isinstance(result.output.follow_up_questions, list)


class TestAgentTools:
    """Tests for tool execution against a real database."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_tools.db")
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        self._seed_articles()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _seed_articles(self):
        """Insert test articles into the database."""
        articles = [
            {
                'title': '万宝路广告的品牌重塑',
                'content': '万宝路 originally targeted women, then Leo Burnett重新定位为男性品牌。',
                'excerpt': '从女性品牌到牛仔形象的品牌转型',
                'category': '经典案例',
                'tags': '万宝路,品牌重塑,Leo Burnett',
                'author': 'professor',
                'status': 'published',
            },
            {
                'title': '大众甲壳虫 Think Small',
                'content': 'DDB广告公司为大众甲壳虫创作的"Think Small"是广告史上的里程碑。',
                'excerpt': '反其道而行之的广告创意',
                'category': '经典案例',
                'tags': '大众,DDB,Think Small,创意',
                'author': 'professor',
                'status': 'published',
            },
            {
                'title': '广告理论发展概述',
                'content': '从USP理论到品牌个性理论，广告学经历了多次范式转变。',
                'excerpt': '广告理论的历史演变',
                'category': '广告理论',
                'tags': 'USP,品牌理论,广告史',
                'author': 'professor',
                'status': 'published',
            },
        ]
        for article in articles:
            self.db_manager.execute_update(
                """INSERT INTO articles 
                   (title, content, excerpt, category, tags, author, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    article['title'], article['content'], article['excerpt'],
                    article['category'], article['tags'], article['author'],
                    article['status'],
                ),
            )

    def _get_tool(self, agent, name):
        """Get a tool function from the agent's toolset."""
        return agent._function_toolset.tools[name].function

    def test_search_articles_finds_results(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        search_fn = self._get_tool(agent, 'search_articles')
        result = search_fn(query='万宝路', limit=5)
        assert '万宝路' in result
        assert '品牌重塑' in result

    def test_search_articles_no_results(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        search_fn = self._get_tool(agent, 'search_articles')
        result = search_fn(query='不存在的关键词xyz', limit=5)
        assert '未找到' in result

    def test_get_article_detail_by_id(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        detail_fn = self._get_tool(agent, 'get_article_detail')
        result = detail_fn(article_id=1)
        assert '万宝路' in result
        assert 'Leo Burnett' in result

    def test_get_article_detail_not_found(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        detail_fn = self._get_tool(agent, 'get_article_detail')
        result = detail_fn(article_id=9999)
        assert '未找到' in result

    def test_get_trending_articles(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        trending_fn = self._get_tool(agent, 'get_trending_articles')
        result = trending_fn(limit=3)
        assert isinstance(result, str)

    def test_get_articles_by_category(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        cat_fn = self._get_tool(agent, 'get_articles_by_category')
        result = cat_fn(category='经典案例', limit=5)
        assert '经典案例' in result

    def test_get_recommendations_by_tags(self):
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        rec_fn = self._get_tool(agent, 'get_recommendations')
        result = rec_fn(topic='DDB,创意', limit=3)
        assert isinstance(result, str)


class TestAIChatPydanticBackend:
    """Tests for pydantic_ai backend methods in AIChat."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_aichat.db")
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        self._seed_articles()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _seed_articles(self):
        """Insert test articles."""
        self.db_manager.execute_update(
            """INSERT INTO articles 
               (title, content, excerpt, category, tags, author, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ('测试文章', '测试内容', '测试摘要', '测试分类', '测试标签', 'professor', 'published'),
        )

    def test_pydantic_ai_init_method(self):
        """Test _init_pydantic_ai method directly."""
        from modules.ai_chat import AIChat
        from modules.ai_agent import create_ad_history_agent as real_create
        from unittest.mock import patch
        
        chat = AIChat.__new__(AIChat)
        chat.backend = 'pydantic_ai'
        
        with patch('modules.database.get_database_manager', return_value=self.db_manager):
            with patch('modules.ai_agent.create_ad_history_agent') as mock_create:
                mock_create.side_effect = lambda db, **kwargs: real_create(db, use_test_model=True)
                
                client = chat._init_pydantic_ai()
                
                assert client is not None
                assert client['type'] == 'pydantic_ai'
                assert 'agent' in client
                assert 'model' in client

    def test_pydantic_ai_generate_response(self):
        """Test _generate_pydantic_ai_response method."""
        from modules.ai_chat import AIChat
        
        chat = AIChat.__new__(AIChat)
        chat.backend = 'pydantic_ai'
        
        # Create a mock client with test agent
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        chat.client = {
            'type': 'pydantic_ai',
            'agent': agent,
            'model': 'test'
        }
        
        response = chat._generate_pydantic_ai_response("你好", [])
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert hasattr(chat, '_last_chat_response')
        assert chat._last_chat_response is not None
        assert isinstance(chat._last_chat_response, ChatResponse)

    def test_pydantic_ai_backend_info(self):
        """Test get_backend_info for pydantic_ai."""
        from modules.ai_chat import AIChat
        
        chat = AIChat.__new__(AIChat)
        chat.backend = 'pydantic_ai'
        chat.client = {
            'type': 'pydantic_ai',
            'agent': None,
            'model': 'groq:llama-3.3-70b-versatile'
        }
        
        info = chat.get_backend_info()
        
        assert info['backend'] == 'pydantic_ai'
        assert info['status'] == '已连接'
        assert info['model'] == 'groq:llama-3.3-70b-versatile'


class TestConversationMemory:
    """Tests for conversation memory system."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_memory.db")
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_retrieve_message(self):
        """Test saving and retrieving chat messages."""
        from modules.conversation_memory import ConversationMemory
        
        memory = ConversationMemory(self.db_manager)
        session_id = memory.create_session("test_user")
        
        # Save messages
        memory.save_message("test_user", session_id, "user", "Hello")
        memory.save_message("test_user", session_id, "assistant", "Hi there!", 
                           sources=["Article 1"], follow_up_questions=["Question 1?"])
        
        # Retrieve history
        history = memory.get_history("test_user", session_id)
        
        assert len(history) == 2
        assert history[0]['role'] == 'user'
        assert history[0]['content'] == 'Hello'
        assert history[1]['role'] == 'assistant'
        assert history[1]['content'] == 'Hi there!'
        assert history[1]['sources'] == ["Article 1"]
        assert history[1]['follow_up_questions'] == ["Question 1?"]

    def test_get_recent_messages(self):
        """Test getting recent messages with limit."""
        from modules.conversation_memory import ConversationMemory
        
        memory = ConversationMemory(self.db_manager)
        session_id = memory.create_session("test_user")
        
        # Save 15 messages
        for i in range(15):
            memory.save_message("test_user", session_id, "user", f"Message {i}")
        
        # Get last 10
        recent = memory.get_recent_messages("test_user", session_id, n=10)
        
        assert len(recent) == 10
        assert recent[0]['content'] == 'Message 5'  # Should start from message 5
        assert recent[-1]['content'] == 'Message 14'

    def test_get_user_sessions(self):
        """Test getting all sessions for a user."""
        from modules.conversation_memory import ConversationMemory
        
        memory = ConversationMemory(self.db_manager)
        
        # Create multiple sessions
        session1 = memory.create_session("test_user")
        session2 = memory.create_session("test_user")
        
        memory.save_message("test_user", session1, "user", "Session 1")
        memory.save_message("test_user", session2, "user", "Session 2")
        
        sessions = memory.get_sessions("test_user")
        
        assert len(sessions) == 2
        session_ids = [s[0] for s in sessions]
        assert session1 in session_ids
        assert session2 in session_ids

    def test_clear_session(self):
        """Test clearing a chat session."""
        from modules.conversation_memory import ConversationMemory
        
        memory = ConversationMemory(self.db_manager)
        session_id = memory.create_session("test_user")
        
        memory.save_message("test_user", session_id, "user", "Hello")
        assert len(memory.get_history("test_user", session_id)) == 1
        
        memory.clear_session("test_user", session_id)
        assert len(memory.get_history("test_user", session_id)) == 0

    def test_format_for_agent(self):
        """Test formatting messages for Pydantic AI agent."""
        from modules.conversation_memory import ConversationMemory
        
        memory = ConversationMemory(self.db_manager)
        session_id = memory.create_session("test_user")
        
        memory.save_message("test_user", session_id, "user", "Hello", 
                           sources=["src1"], follow_up_questions=["q1?"])
        memory.save_message("test_user", session_id, "assistant", "Hi!")
        
        history = memory.get_history("test_user", session_id)
        formatted = memory.format_for_agent(history)
        
        assert len(formatted) == 2
        assert formatted[0] == {'role': 'user', 'content': 'Hello'}
        assert formatted[1] == {'role': 'assistant', 'content': 'Hi!'}
        # Sources and follow-ups should not be in formatted output


class TestToolCaching:
    """Tests for tool result caching."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_cache.db")
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        self._seed_articles()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _seed_articles(self):
        """Insert test articles."""
        self.db_manager.execute_update(
            """INSERT INTO articles 
               (title, content, excerpt, category, tags, author, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ('Test Article', 'Content', 'Excerpt', 'Category', 'tags', 'author', 'published'),
        )

    def test_cache_hit(self):
        """Test that cached results are returned on subsequent calls."""
        from modules.ai_tools import _tool_cache
        
        # Clear cache
        _tool_cache.clear()
        
        agent = create_ad_history_agent(self.db_manager, use_test_model=True)
        
        search_fn = agent._function_toolset.tools['search_articles'].function
        
        # First call - should compute
        result1 = search_fn(query='Test', limit=5)
        
        # Check cache was populated
        assert len(_tool_cache) > 0
        
        # Second call - should use cache
        result2 = search_fn(query='Test', limit=5)
        
        assert result1 == result2

    def test_cache_ttl(self):
        """Test that cache expires after TTL."""
        import time
        from modules.ai_tools import register_tools, _tool_cache, _cache_ttl
        
        # Clear cache and set short TTL for testing
        _tool_cache.clear()
        original_ttl = _cache_ttl.get('search_articles', 300)
        _cache_ttl['search_articles'] = 1  # 1 second TTL
        
        try:
            agent = create_ad_history_agent(self.db_manager, use_test_model=True)
            search_fn = agent._function_toolset.tools['search_articles'].function
            
            # First call
            result1 = search_fn(query='Test', limit=5)
            cache_key = list(_tool_cache.keys())[0]
            
            # Wait for TTL to expire
            time.sleep(1.5)
            
            # Second call - should recompute (cache expired)
            result2 = search_fn(query='Test', limit=5)
            
            # Cache should have been refreshed
            assert cache_key in _tool_cache
            
        finally:
            _cache_ttl['search_articles'] = original_ttl
