import streamlit as st
import os
from typing import List, Dict, Optional
from datetime import datetime
import importlib

from utils.i18n import t

# AI后端配置
AI_BACKEND = os.getenv('AI_BACKEND', 'ollama')  # 默认使用ollama
AVAILABLE_BACKENDS = ['gemini', 'ollama', 'azure_openai', 'groq']

class AIChat:
    """统一的AI聊天管理器"""
    
    def __init__(self):
        self.backend = AI_BACKEND.lower()
        self.client = None
        self.initialize_backend()
    
    def initialize_backend(self):
        """初始化AI后端"""
        try:
            if self.backend == 'gemini':
                self.client = self._init_gemini()
            elif self.backend == 'ollama':
                self.client = self._init_ollama()
            elif self.backend == 'azure_openai':
                self.client = self._init_azure_openai()
            elif self.backend == 'groq':
                self.client = self._init_groq()
            else:
                st.error(f"不支持的AI后端: {self.backend}")
                self.client = None
        except Exception as e:
            st.error(f"初始化AI后端失败: {e}")
            self.client = None
    
    def _init_gemini(self):
        """初始化Gemini客户端"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY 环境变量未设置")
            
            genai.configure(api_key=api_key)
            model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            model = genai.GenerativeModel(model_name)
            
            return {
                'type': 'gemini',
                'model': model,
                'chat': model.start_chat(history=[])
            }
        except ImportError:
            raise ImportError("请安装 google-generativeai: pip install google-generativeai")
    
    def _init_ollama(self):
        """初始化Ollama客户端"""
        from chat_ollama import OllamaChat
        
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model = os.getenv('OLLAMA_MODEL', 'llama2')
        
        ollama_client = OllamaChat(base_url, model)
        
        # 检查连接
        if not ollama_client.check_connection():
            raise ConnectionError("无法连接到Ollama服务")
        
        return {
            'type': 'ollama',
            'client': ollama_client
        }
    
    def _init_azure_openai(self):
        """初始化Azure OpenAI客户端"""
        try:
            from openai import AzureOpenAI
            import httpx

            proxy_url = os.getenv('https_proxy') or os.getenv('http_proxy')
            if proxy_url:
                http_client = httpx.Client(proxy=proxy_url)
            else:
                http_client = httpx.Client()

            client = AzureOpenAI(
                api_key=os.getenv('AZURE_OPENAI_KEY'),
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-06-01'),
                azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                http_client=http_client,
            )
            
            return {
                'type': 'azure_openai',
                'client': client,
                'deployment': os.getenv('AZURE_OPENAI_CHATGPT_DEPLOYMENT', 'gpt-4o')
            }
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

    def _init_groq(self):
        """初始化Groq客户端（OpenAI兼容API）"""
        try:
            from openai import OpenAI
            import httpx

            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY 环境变量未设置")

            # Explicit http_client with proxy to bypass broken auto-detection
            # in openai 1.42.0 + httpx with proxy env vars
            proxy_url = os.getenv('https_proxy') or os.getenv('http_proxy')
            if proxy_url:
                http_client = httpx.Client(proxy=proxy_url)
            else:
                http_client = httpx.Client()

            client = OpenAI(
                api_key=api_key,
                base_url=os.getenv('GROQ_BASE_URL', 'https://api.groq.com/openai/v1'),
                http_client=http_client,
            )

            return {
                'type': 'groq',
                'client': client,
                'model': os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
            }
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

    def generate_response(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """生成AI回复"""
        if not self.client:
            return "AI服务未正确初始化，请检查配置。"

        try:
            if self.client['type'] == 'gemini':
                return self._generate_gemini_response(prompt, conversation_history)
            elif self.client['type'] == 'ollama':
                return self._generate_ollama_response(prompt, conversation_history)
            elif self.client['type'] == 'azure_openai':
                return self._generate_azure_response(prompt, conversation_history)
            elif self.client['type'] == 'groq':
                return self._generate_groq_response(prompt, conversation_history)
        except Exception as e:
            return f"生成回复时发生错误: {str(e)}"
    
    def _generate_gemini_response(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """生成Gemini回复"""
        system_prompt = "你是一位广告学领域的专家，请根据用户的问题，用简体中文回答。"
        context = f"{system_prompt}\n\n用户问题: {prompt}"
        
        response = self.client['chat'].send_message(context)
        return response.text
    
    def _generate_ollama_response(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """生成Ollama回复"""
        return self.client['client'].generate_response(prompt, conversation_history)
    
    def _generate_azure_response(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """生成Azure OpenAI回复"""
        messages = [
            {"role": "system", "content": "你是一位广告学领域的专家，请根据用户的问题，用简体中文回答。"}
        ]

        # 添加历史对话
        if conversation_history:
            for msg in conversation_history[-10:]:  # 最近10条消息
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # 添加当前问题
        messages.append({"role": "user", "content": prompt})

        response = self.client['client'].chat.completions.create(
            model=self.client['deployment'],
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content

    def _generate_groq_response(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """生成Groq回复"""
        messages = [
            {"role": "system", "content": "你是一位广告学领域的专家，请根据用户的问题，用简体中文回答。"}
        ]

        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        messages.append({"role": "user", "content": prompt})

        response = self.client['client'].chat.completions.create(
            model=self.client['model'],
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content

    def _stream_groq(self, prompt: str, conversation_history: List[Dict] = None):
        """流式生成Groq回复"""
        messages = [
            {"role": "system", "content": "你是一位广告学领域的专家，请根据用户的问题，用简体中文回答。"}
        ]

        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        messages.append({"role": "user", "content": prompt})

        stream = self.client['client'].chat.completions.create(
            model=self.client['model'],
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def stream_response(self, prompt: str, conversation_history: List[Dict] = None):
        """流式生成回复"""
        if not self.client:
            yield "AI服务未正确初始化，请检查配置。"
            return

        try:
            if self.client['type'] == 'ollama':
                for chunk in self.client['client'].stream_response(prompt, conversation_history):
                    yield chunk
            elif self.client['type'] == 'groq':
                yield from self._stream_groq(prompt, conversation_history)
            else:
                # 对于不支持流式的后端，直接返回完整回复
                response = self.generate_response(prompt, conversation_history)
                yield response
        except Exception as e:
            yield f"生成回复时发生错误: {str(e)}"
    
    def get_backend_info(self) -> Dict:
        """获取当前后端信息"""
        if not self.client:
            return {"backend": self.backend, "status": "未初始化", "model": "未知"}
        
        info = {"backend": self.backend, "status": "已连接"}
        
        if self.client['type'] == 'gemini':
            info["model"] = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        elif self.client['type'] == 'ollama':
            info["model"] = self.client['client'].model
            info["base_url"] = self.client['client'].base_url
        elif self.client['type'] == 'azure_openai':
            info["model"] = self.client['deployment']
            info["endpoint"] = os.getenv('AZURE_OPENAI_ENDPOINT')
        elif self.client['type'] == 'groq':
            info["model"] = self.client['model']
        
        return info

def initialize_session_state():
    """初始化会话状态"""
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []
        st.session_state.ai_chat_history = []
    
    if "ai_client" not in st.session_state:
        st.session_state.ai_client = AIChat()

def append_message(role: str, content: str):
    """添加消息到历史记录"""
    if content:
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.ai_messages.append(message)
        st.session_state.ai_chat_history.append(message)
        
        # 保持历史记录在限定范围内
        max_history = 20
        if len(st.session_state.ai_messages) > max_history:
            st.session_state.ai_messages = st.session_state.ai_messages[-max_history:]
        if len(st.session_state.ai_chat_history) > max_history:
            st.session_state.ai_chat_history = st.session_state.ai_chat_history[-max_history:]

def display_chat():
    """显示聊天消息"""
    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def show_ai_settings():
    """显示AI设置"""
    ai_client = st.session_state.ai_client
    backend_info = ai_client.get_backend_info()
    username = st.session_state.get("username")

    # Check if admin (for showing backend switching instructions)
    is_admin = False
    try:
        from modules.auth import get_auth_manager
        from modules.database import get_database_manager
        db = get_database_manager()
        am = get_auth_manager(db_manager=db)
        is_admin = am.is_admin(username) if username else False
    except Exception:
        pass

    with st.sidebar:
        # Only admins see backend config & switching instructions
        if is_admin:
            st.markdown(f"### 🤖 {t('ai_settings')}")
            st.info(f"**{t('ai_backend')}**: {backend_info['backend'].upper()}")
            st.info(f"**Status**: {backend_info['status']}")
            if 'model' in backend_info:
                st.info(f"**{t('ai_model')}**: {backend_info['model']}")

            st.markdown(f"### 🔄 {t('ai_switch_backend')}")
            st.markdown("""
            To switch AI backend, set the following in `.env`:

            ```bash
            # Groq (Recommended)
            AI_BACKEND=groq
            GROQ_API_KEY=your_key
            GROQ_MODEL=llama-3.3-70b-versatile

            # Gemini
            AI_BACKEND=gemini
            GEMINI_API_KEY=your_key

            # Ollama
            AI_BACKEND=ollama
            OLLAMA_BASE_URL=http://localhost:11434
            OLLAMA_MODEL=llama2

            # Azure OpenAI
            AI_BACKEND=azure_openai
            AZURE_OPENAI_KEY=your_key
            AZURE_OPENAI_ENDPOINT=your_endpoint
            ```

            Then restart the app.
            """)

        # Chat settings visible to all users
        st.markdown(f"### ⚙️ {t('ai_chat_stats')}")
        if st.button(f"🗑️ {t('ai_clear_chat')}"):
            st.session_state.ai_messages = []
            st.session_state.ai_chat_history = []
            st.rerun()
        st.metric(t('ai_message_count'), len(st.session_state.ai_messages))
        if st.session_state.ai_messages:
            last_msg_time = st.session_state.ai_messages[-1]["timestamp"]
            st.caption(f"{t('ai_last_message')}: {last_msg_time[:16]}")

def chat_interface():
    """统一的AI聊天界面"""
    lang = t('app_title')  # just to ensure translations are loaded
    st.markdown(f"# 🤖 {t('ai_chat_title')}")

    # 初始化会话状态
    initialize_session_state()

    ai_client = st.session_state.ai_client
    backend_info = ai_client.get_backend_info()

    # 显示当前使用的AI后端
    st.markdown(f"**{t('ai_backend')}**: {backend_info['backend'].upper()} | **{t('ai_model')}**: {backend_info.get('model', 'N/A')}")

    # 显示AI设置
    show_ai_settings()

    # 检查AI客户端状态
    if not ai_client.client:
        st.error("AI service not initialized properly. Please check environment variable configuration.")
        st.markdown("""
        ### 🔧 Configuration Guide

        Configure the following environment variables in `.env`:

        **Groq** (Recommended):
        ```bash
        AI_BACKEND=groq
        GROQ_API_KEY=your_groq_api_key
        GROQ_MODEL=llama-3.3-70b-versatile
        ```

        **Gemini**:
        ```bash
        AI_BACKEND=gemini
        GEMINI_API_KEY=your_gemini_api_key
        GEMINI_MODEL=gemini-1.5-flash
        ```

        **Ollama**:
        ```bash
        AI_BACKEND=ollama
        OLLAMA_BASE_URL=http://localhost:11434
        OLLAMA_MODEL=llama2
        ```

        **Azure OpenAI**:
        ```bash
        AI_BACKEND=azure_openai
        AZURE_OPENAI_KEY=your_azure_key
        AZURE_OPENAI_ENDPOINT=your_azure_endpoint
        AZURE_OPENAI_CHATGPT_DEPLOYMENT=gpt-4o
        ```
        """)
        return

    # 显示聊天历史
    display_chat()

    # 聊天输入
    if prompt := st.chat_input(t('ai_placeholder')):
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 添加用户消息到历史
        append_message("user", prompt)
        
        # 生成AI回复
        with st.chat_message("assistant"):
            # 检查是否支持流式回复
            if backend_info['backend'] == 'ollama':
                # 流式回复
                response_placeholder = st.empty()
                full_response = ""
                
                try:
                    for chunk in ai_client.stream_response(prompt, st.session_state.ai_chat_history):
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    
                except Exception as e:
                    full_response = f"Error generating response: {str(e)}"
                    response_placeholder.markdown(full_response)
            else:
                # 非流式回复
                with st.spinner(t('ai_thinking')):
                    full_response = ai_client.generate_response(prompt, st.session_state.ai_chat_history)
                
                st.markdown(full_response)
        
        # 添加AI回复到历史
        append_message("assistant", full_response)

if __name__ == "__main__":
    # 可以单独运行此文件进行测试
    st.set_page_config(
        page_title="AI Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    chat_interface()