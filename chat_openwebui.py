import streamlit as st
import requests
import json
from typing import List, Dict, Optional
import os
from datetime import datetime

# 常量
OPENWEBUI_BASE_URL = os.getenv('OPENWEBUI_BASE_URL', 'http://localhost:3000')
OPENWEBUI_API_KEY = os.getenv('OPENWEBUI_API_KEY', '')
OPENWEBUI_MODEL = os.getenv('OPENWEBUI_MODEL', 'llama3.2:latest')
SYSTEM_PROMPT = "你是一位广告学领域的专家，请根据用户的问题，用简体中文回答。请提供专业、准确、有见地的回答。"
MAX_HISTORY = 10

class OpenWebUIChat:
    def __init__(self, base_url: str = OPENWEBUI_BASE_URL, api_key: str = OPENWEBUI_API_KEY, model: str = OPENWEBUI_MODEL):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.system_prompt = SYSTEM_PROMPT
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def check_connection(self) -> bool:
        """检查Open WebUI服务连接"""
        try:
            response = requests.get(
                f"{self.base_url}/api/models",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"无法连接到Open WebUI服务: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            response = requests.get(
                f"{self.base_url}/api/models",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                # Open WebUI returns models in data array
                if isinstance(data, dict) and 'data' in data:
                    return [model['id'] for model in data.get('data', [])]
                elif isinstance(data, list):
                    return [model['id'] if isinstance(model, dict) else str(model) for model in data]
            return []
        except Exception as e:
            st.error(f"获取模型列表失败: {e}")
            return []
    
    def generate_response(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """生成AI回复"""
        try:
            # 构建对话上下文
            messages = []
            
            # 添加系统提示
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # 添加历史对话
            if conversation_history:
                for msg in conversation_history[-MAX_HISTORY:]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # 添加当前用户输入
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 调用Open WebUI API (OpenAI-compatible)
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '抱歉，我无法生成回复。')
            else:
                return f"API调用失败，状态码: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "请求超时，请稍后重试。"
        except requests.exceptions.ConnectionError:
            return "无法连接到Open WebUI服务，请检查服务是否正在运行。"
        except Exception as e:
            return f"发生错误: {str(e)}"
    
    def stream_response(self, prompt: str, conversation_history: List[Dict] = None):
        """流式生成回复"""
        try:
            # 构建对话上下文
            messages = []
            
            # 添加系统提示
            messages.append({
                "role": "system", 
                "content": self.system_prompt
            })
            
            # 添加历史对话
            if conversation_history:
                for msg in conversation_history[-MAX_HISTORY:]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # 添加当前用户输入
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 调用流式API
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            line_text = line_text[6:]  # Remove 'data: ' prefix
                        
                        if line_text.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(line_text)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"API调用失败，状态码: {response.status_code}"
                
        except Exception as e:
            yield f"发生错误: {str(e)}"

def initialize_session_state():
    """初始化会话状态"""
    if "openwebui_messages" not in st.session_state:
        st.session_state.openwebui_messages = []
        st.session_state.openwebui_chat_history = []
    
    if "openwebui_client" not in st.session_state:
        st.session_state.openwebui_client = OpenWebUIChat()

def append_message(role: str, content: str):
    """添加消息到历史记录"""
    if content:
        message = {
            "role": role, 
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.openwebui_messages.append(message)
        st.session_state.openwebui_chat_history.append(message)
        
        # 保持历史记录在限定范围内
        if len(st.session_state.openwebui_messages) > MAX_HISTORY * 2:
            st.session_state.openwebui_messages = st.session_state.openwebui_messages[-(MAX_HISTORY * 2):]
        if len(st.session_state.openwebui_chat_history) > MAX_HISTORY * 2:
            st.session_state.openwebui_chat_history = st.session_state.openwebui_chat_history[-(MAX_HISTORY * 2):]

def display_chat():
    """显示聊天消息"""
    for msg in st.session_state.openwebui_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def show_model_selector():
    """显示模型选择器"""
    openwebui_client = st.session_state.openwebui_client
    
    with st.sidebar:
        st.markdown("### 🌐 Open WebUI 设置")
        
        # 检查连接状态
        if openwebui_client.check_connection():
            st.success("✅ Open WebUI 连接正常")
            
            # 获取可用模型
            available_models = openwebui_client.get_available_models()
            
            if available_models:
                selected_model = st.selectbox(
                    "选择模型",
                    available_models,
                    index=0 if openwebui_client.model not in available_models else available_models.index(openwebui_client.model)
                )
                
                if selected_model != openwebui_client.model:
                    openwebui_client.model = selected_model
                    st.success(f"已切换到模型: {selected_model}")
                
                st.info(f"当前模型: {openwebui_client.model}")
            else:
                st.warning("未找到可用模型")
        else:
            st.error("❌ Open WebUI 连接失败")
            st.markdown("""
            **请检查:**
            1. Open WebUI 服务是否运行
            2. API密钥是否正确
            3. 服务地址是否正确
            4. 网络连接是否正常
            
            **配置环境变量:**
            ```bash
            OPENWEBUI_BASE_URL=http://localhost:3000
            OPENWEBUI_API_KEY=your_api_key
            OPENWEBUI_MODEL=llama3.2:latest
            ```
            """)

def chat_interface():
    """Open WebUI聊天界面"""
    st.markdown("""
    <div class="page-header">
        <h1>💬 与AI专家对话</h1>
        <p>Chat with Masters — 广告大师智能对话</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    st.markdown("基于Open WebUI平台的广告学专业问答")
    
    # 初始化会话状态
    initialize_session_state()
    
    # 显示模型选择器
    show_model_selector()
    
    openwebui_client = st.session_state.openwebui_client
    
    # 检查连接状态
    if not openwebui_client.check_connection():
        st.error("无法连接到Open WebUI服务，请检查配置")
        return
    
    # 聊天设置
    with st.sidebar:
        st.markdown("### ⚙️ 聊天设置")
        
        use_stream = st.checkbox("流式回复", value=True, help="实时显示AI回复过程")
        
        if st.button("🗑️ 清空对话"):
            st.session_state.openwebui_messages = []
            st.session_state.openwebui_chat_history = []
            st.rerun()
        
        # 显示对话统计
        st.markdown("### 📊 对话统计")
        st.metric("消息数量", len(st.session_state.openwebui_messages))
        if st.session_state.openwebui_messages:
            last_msg_time = st.session_state.openwebui_messages[-1]["timestamp"]
            st.caption(f"最后消息: {last_msg_time[:16]}")
    
    # 显示聊天历史
    display_chat()
    
    # 聊天输入
    if prompt := st.chat_input("请输入您关于广告学的问题..."):
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 添加用户消息到历史
        append_message("user", prompt)
        
        # 生成AI回复
        with st.chat_message("assistant"):
            if use_stream:
                # 流式回复
                response_placeholder = st.empty()
                full_response = ""
                
                try:
                    for chunk in openwebui_client.stream_response(prompt, st.session_state.openwebui_chat_history):
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    
                except Exception as e:
                    full_response = f"生成回复时发生错误: {str(e)}"
                    response_placeholder.markdown(full_response)
            else:
                # 非流式回复
                with st.spinner("AI正在思考中..."):
                    full_response = openwebui_client.generate_response(prompt, st.session_state.openwebui_chat_history)
                
                st.markdown(full_response)
        
        # 添加AI回复到历史
        append_message("assistant", full_response)

if __name__ == "__main__":
    # 可以单独运行此文件进行测试
    st.set_page_config(
        page_title="Open WebUI Chat",
        page_icon="🌐",
        layout="wide"
    )
    
    chat_interface()
