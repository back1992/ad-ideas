import requests
import streamlit as st
import json

# Constants
DEFAULT_MODEL = "Llama-3.2-3B-Instruct-Q6_K"
CHAT_API_URL = "https://ai-webui.izhixue.cc/completion"
OLLAMA_API_URL = "https://ai.izhixue.cc/api/chat"
# SYSTEM_PROMPT = "You are a helpful assistant knowledgeable about advertising history."
SYSTEM_PROMPT = "你是一位广告学领域的专家， 请根据用户的问题， 用简体中文回答。"

def initialize_session_state():
    """Initialize session state with defaults if not already set."""
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.chat_history = []

MAX_HISTORY = 10  # Maximum number of message pairs to keep

def append_message(role: str, content: str):
    """Append a message to both messages and chat_history with size limit."""
    if content:
        # Add new message
        st.session_state.messages.append({"role": role, "content": content})
        st.session_state.chat_history.append({"role": role, "content": content})

        # Keep only system message and last MAX_HISTORY * 2 messages
        # (each conversation turn has 2 messages: user + assistant)
        if len(st.session_state.messages) > (MAX_HISTORY * 2 + 1):
            # Keep system message
            st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-(MAX_HISTORY * 2):]

        # Keep only last MAX_HISTORY conversation turns in chat history
        if len(st.session_state.chat_history) > MAX_HISTORY * 2:
            st.session_state.chat_history = st.session_state.chat_history[-(MAX_HISTORY * 2):]

def stream_response(prompt: str) -> str:
    """Generate a streamed response from the Ollama API with chat history."""
    # Build messages array from chat history
    messages = [
        {"role": "system", "content": "你是一位广告学领域的专家，请回答用户关于广告创意和销售的问题。"}
    ]

    # Add chat history from session state
    for msg in st.session_state.chat_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current prompt
    messages.append({
        "role": "user",
        "content": prompt
    })

    payload = {
        "model": "mistral",
        "messages": messages,
        "stream": True
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        with st.spinner("思考中..."):
            content_placeholder = st.empty()
            response_chunks = []

            for line in response.iter_lines():
                if line:
                    try:
                        decoded_line = line.decode('utf-8')
                        chunk = json.loads(decoded_line).get("message", {}).get("content", "")
                        if chunk:
                            response_chunks.append(chunk)
                            content_placeholder.markdown("".join(response_chunks))
                    except json.JSONDecodeError:
                        continue

            full_response = "".join(response_chunks) or "未能生成回应。"
            content_placeholder.empty()
            return full_response

    except requests.RequestException as e:
        return f"连接错误: {str(e)}"
    except Exception as e:
        return f"系统错误: {str(e)}"


def display_chat():
    """Display non-system messages from chat history."""
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

def chat_lu():
    """Simplified chat interface."""
    st.title("💬 Advertising History Chat")
    initialize_session_state()
    display_chat()

    if prompt := st.chat_input("Ask about advertising history..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        append_message("user", prompt)

        response = stream_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)
        append_message("assistant", response)


if __name__ == "__main__":
    chat_lu()

