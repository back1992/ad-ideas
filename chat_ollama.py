import streamlit as st
import requests
import json
from typing import List, Dict, Optional
import os
from datetime import datetime

# 常量
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
SYSTEM_PROMPT = "你是一位广告学领域的专家，请根据用户的问题，用简体中文回答。请提供专业、准确、有见地的回答。"
MAX_HISTORY = 10

class OllamaChat:
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.system_prompt = SYSTEM_PROMPT
    
    def check_connection(self) -> bool:
        """检查Ollama服务连接"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            st.error(f"无法连接到Ollama服务: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
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
            
            # 调用Ollama API
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '抱歉，我无法生成回复。')
            else:
                return f"API调用失败，状态码: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "请求超时，请稍后重试。"
        except requests.exceptions.ConnectionError:
            return "无法连接到Ollama服务，请检查服务是否正在运行。"
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
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'message' in data and 'content' in data['message']:
                                yield data['message']['content']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"API调用失败，状态码: {response.status_code}"
                
        except Exception as e:
            yield f"发生错误: {str(e)}"

def initialize_session_state():
    """初始化会话状态"""
    if "ollama_messages" not in st.session_state:
        st.session_state.ollama_messages = []
        st.session_state.ollama_chat_history = []
    
    if "ollama_client" not in st.session_state:
        st.session_state.ollama_client = OllamaChat()

def append_message(role: str, content: str):
    """添加消息到历史记录"""
    if content:
        message = {
            "role": role, 
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.ollama_messages.append(message)
        st.session_state.ollama_chat_history.append(message)
        
        # 保持历史记录在限定范围内
        if len(st.session_state.ollama_messages) > MAX_HISTORY * 2:
            st.session_state.ollama_messages = st.session_state.ollama_messages[-(MAX_HISTORY * 2):]
        if len(st.session_state.ollama_chat_history) > MAX_HISTORY * 2:
            st.session_state.ollama_chat_history = st.session_state.ollama_chat_history[-(MAX_HISTORY * 2):]

def display_chat():
    """显示聊天消息"""
    for msg in st.session_state.ollama_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def show_model_selector():
    """显示模型选择器"""
    ollama_client = st.session_state.ollama_client
    
    with st.sidebar:
        st.markdown("### 🤖 Ollama 设置")
        
        # 检查连接状态
        if ollama_client.check_connection():
            st.success("✅ Ollama 连接正常")
            
            # 获取可用模型
            available_models = ollama_client.get_available_models()
            
            if available_models:
                selected_model = st.selectbox(
                    "选择模型",
                    available_models,
                    index=0 if ollama_client.model not in available_models else available_models.index(ollama_client.model)
                )
                
                if selected_model != ollama_client.model:
                    ollama_client.model = selected_model
                    st.success(f"已切换到模型: {selected_model}")
                
                st.info(f"当前模型: {ollama_client.model}")
            else:
                st.warning("未找到可用模型，请先下载模型")
                st.code("ollama pull llama2")
        else:
            st.error("❌ Ollama 连接失败")
            st.markdown("""
            **请检查:**
            1. Ollama 服务是否运行
            2. 服务地址是否正确
            3. 网络连接是否正常
            
            **启动命令:**
            ```bash
            ollama serve
            ```
            """)

def chat_interface():
    """Ollama聊天界面"""
    st.markdown("# 🤖 与AI专家对话 (Ollama)")
    st.markdown("基于本地Ollama模型的广告学专业问答")
    
    # 初始化会话状态
    initialize_session_state()
    
    # 显示模型选择器
    show_model_selector()
    
    ollama_client = st.session_state.ollama_client
    
    # 检查连接状态
    if not ollama_client.check_connection():
        st.error("无法连接到Ollama服务，请检查配置")
        return
    
    # 聊天设置
    with st.sidebar:
        st.markdown("### ⚙️ 聊天设置")
        
        use_stream = st.checkbox("流式回复", value=True, help="实时显示AI回复过程")
        
        if st.button("🗑️ 清空对话"):
            st.session_state.ollama_messages = []
            st.session_state.ollama_chat_history = []
            st.experimental_rerun()
        
        # 显示对话统计
        st.markdown("### 📊 对话统计")
        st.metric("消息数量", len(st.session_state.ollama_messages))
        if st.session_state.ollama_messages:
            last_msg_time = st.session_state.ollama_messages[-1]["timestamp"]
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
                    for chunk in ollama_client.stream_response(prompt, st.session_state.ollama_chat_history):
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    
                except Exception as e:
                    full_response = f"生成回复时发生错误: {str(e)}"
                    response_placeholder.markdown(full_response)
            else:
                # 非流式回复
                with st.spinner("AI正在思考中..."):
                    full_response = ollama_client.generate_response(prompt, st.session_state.ollama_chat_history)
                
                st.markdown(full_response)
        
        # 添加AI回复到历史
        append_message("assistant", full_response)

def show_ollama_info():
    """显示Ollama信息页面"""
    st.markdown("# 🦙 关于 Ollama")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 什么是 Ollama？
        
        Ollama 是一个开源的大语言模型运行平台，允许您在本地运行各种AI模型，包括：
        
        - **Llama 2** - Meta开源的强大语言模型
        - **Code Llama** - 专门用于代码生成的模型
        - **Mistral** - 高效的开源模型
        - **Vicuna** - 基于Llama微调的对话模型
        
        ## 优势
        
        - 🔒 **隐私保护**: 数据不会发送到外部服务器
        - 💰 **成本控制**: 无需支付API调用费用
        - 🚀 **高性能**: 本地运行，响应速度快
        - 🛠️ **可定制**: 可以微调和定制模型
        """)
    
    with col2:
        st.markdown("""
        ## 🚀 快速开始
        
        ### 1. 安装 Ollama
        ```bash
        # macOS
        brew install ollama
        
        # Linux
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Windows
        # 下载安装包
        ```
        
        ### 2. 启动服务
        ```bash
        ollama serve
        ```
        
        ### 3. 下载模型
        ```bash
        ollama pull llama2
        ollama pull mistral
        ```
        
        ### 4. 配置环境变量
        ```bash
        OLLAMA_BASE_URL=http://localhost:11434
        OLLAMA_MODEL=llama2
        ```
        """)
    
    # 系统要求
    st.markdown("## 💻 系统要求")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 最低配置
        - **内存**: 8GB RAM
        - **存储**: 4GB 可用空间
        - **CPU**: 现代多核处理器
        """)
    
    with col2:
        st.markdown("""
        ### 推荐配置
        - **内存**: 16GB+ RAM
        - **存储**: 10GB+ 可用空间
        - **GPU**: NVIDIA GPU (可选)
        """)
    
    with col3:
        st.markdown("""
        ### 生产环境
        - **内存**: 32GB+ RAM
        - **存储**: 50GB+ SSD
        - **GPU**: 高端 NVIDIA GPU
        """)
    
    # 模型对比
    st.markdown("## 🤖 模型对比")
    
    model_comparison = {
        "模型": ["Llama 2 7B", "Llama 2 13B", "Mistral 7B", "Code Llama 7B"],
        "大小": ["3.8GB", "7.3GB", "4.1GB", "3.8GB"],
        "内存需求": ["8GB", "16GB", "8GB", "8GB"],
        "特点": ["通用对话", "更强性能", "高效快速", "代码专用"],
        "适用场景": ["日常问答", "复杂任务", "快速响应", "编程助手"]
    }
    
    import pandas as pd
    df = pd.DataFrame(model_comparison)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    # 可以单独运行此文件进行测试
    st.set_page_config(
        page_title="Ollama Chat",
        page_icon="🦙",
        layout="wide"
    )
    
    tab1, tab2 = st.tabs(["💬 聊天", "ℹ️ 关于"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        show_ollama_info()