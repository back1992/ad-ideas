import google.generativeai as genai
import streamlit as st
import os
from typing import List

# 常量
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']  # 替换为你的 API 密钥
MODEL_NAME = "gemini-1.5-flash"
SYSTEM_PROMPT = "你是一位广告学领域的专家，请根据用户的问题，用简体中文回答。"
MAX_HISTORY = 10

# 配置 Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

def initialize_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.chat = model.start_chat(history=[])

def append_message(role: str, content: str):
    """添加消息到历史记录"""
    if content:
        message = {"role": role, "content": content}
        st.session_state.messages.append(message)
        st.session_state.chat_history.append(message)

        # 保持历史记录在限定范围内
        if len(st.session_state.messages) > MAX_HISTORY * 2:
            st.session_state.messages = st.session_state.messages[-(MAX_HISTORY * 2):]
        if len(st.session_state.chat_history) > MAX_HISTORY * 2:
            st.session_state.chat_history = st.session_state.chat_history[-(MAX_HISTORY * 2):]

def get_gemini_response(prompt: str) -> str:
    """从 Gemini 获取响应"""
    try:
        # 添加系统提示和用户输入
        context = f"{SYSTEM_PROMPT}\n\n用户问题: {prompt}"
        response = st.session_state.chat.send_message(context)
        return response.text
    except Exception as e:
        return f"发生错误: {str(e)}"

def display_chat():
    """显示聊天消息"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def chat_interface():
    """聊天界面主函数"""
    st.title("💬 《广告思想简史》问答助手")
    initialize_session_state()
    display_chat()

    if prompt := st.chat_input("请输入您的问题..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        append_message("user", prompt)

        with st.spinner("思考中..."):
            response = get_gemini_response(prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            append_message("assistant", response)

if __name__ == "__main__":
    chat_interface()