import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import streamlit as st
from typing import List, Dict
from requests.adapters import HTTPAdapter
import urllib3.util.retry
import json
import chromadb
from chromadb.config import Settings

# Load environment variables
load_dotenv()
OLLAMA_API_KEY = os.environ.get('OLLAMA_API_KEY')

# Initialize Chroma client
chroma_client = chromadb.Client(Settings(
    persist_directory=".chroma",
    is_persistent=True
))

def initialize_session_state():
    """Initialize session state variables with default values."""
    defaults = {
        "messages": [{"role": "system", "content": "You are an AI assistant knowledgeable about advertising history."}],
        "chat_history": [],
        "model_name": "llama3.1:8b-instruct-q4_0",
        "collection_id": "2200479b-d722-45a4-ad06-06ea537f5af4"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_chat_context(messages: List[Dict[str, str]], max_context: int = 3) -> List[Dict[str, str]]:
    """Extract recent chat context up to max_context messages."""
    system_message = next((msg for msg in messages if msg["role"] == "system"), None)
    recent_messages = messages[-max_context * 2:] if len(messages) > max_context * 2 else messages

    context = []
    if system_message:
        context.append(system_message)
    context.extend(recent_messages)
    return context

def store_embedding(prompt: str, embedding: List[float]):
    """Store the embedding in Chroma."""
    collection = chroma_client.get_or_create_collection(name=st.session_state.collection_id)
    collection.add(documents=[prompt], embeddings=[embedding])

def query_embedding(prompt: str) -> List[float]:
    """Query the embedding from Chroma."""
    collection = chroma_client.get_or_create_collection(name=st.session_state.collection_id)
    results = collection.query(query_texts=[prompt], n_results=1)
    if results['documents']:
        return results['embeddings'][0]
    return None

def generate_response_webui(prompt: str) -> str:
    """Generate a response using the Ollama API with context awareness."""
    session = None

    if not OLLAMA_API_KEY:
        return "Error: API key not found in environment variables."

    system_prompt = (
        "You are an expert in advertising history and creativity. "
        "When answering questions, provide specific examples, case studies, "
        "and actionable insights. Please be thorough and detailed in your responses. "
        "Always respond in Chinese."
    )

    try:
        context = get_chat_context(st.session_state.messages)
        context.insert(0, {"role": "system", "content": system_prompt})

        url = "http://open-webui.zbb-api.wqketang.com/ollama/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {OLLAMA_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': st.session_state.model_name,
            'messages': [{"role": "user", "content": prompt}],  # Simplified messages
            'stream': False,
            'temperature': 0.7,
            'max_tokens': 2000
        }

        session = requests.Session()

        with st.spinner('生成回答中...'):
            response = session.post(url, headers=headers, json=payload, timeout=30)

            # Check response status
            if response.status_code != 200:
                return f"API Error: Status code {response.status_code}"

            # Parse response carefully
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                return "Error: Invalid JSON response"

            # Validate response structure
            if not isinstance(response_data, dict):
                return "Error: Invalid response format"

            if 'choices' not in response_data:
                return "Error: No choices in response"

            choices = response_data['choices']
            if not choices or not isinstance(choices, list):
                return "Error: Empty or invalid choices"

            first_choice = choices[0]
            if not isinstance(first_choice, dict):
                return "Error: Invalid choice format"

            message = first_choice.get('message')
            if not message or not isinstance(message, dict):
                return "Error: Invalid message format"

            content = message.get('content')
            if not content:
                return "Error: No content in response"

            return content.strip()

    except requests.exceptions.Timeout:
        return "请求超时，请重试"
    except requests.exceptions.RequestException as e:
        return f"API请求错误: {str(e)}"
    except Exception as e:
        return f"系统错误: {str(e)}"
    finally:
        if session:
            session.close()

def update_chat_history(role: str, content: str):
    """Update session state with new message."""
    if content:
        st.session_state.messages.append({"role": role, "content": content})
        st.session_state.chat_history.append({"role": role, "content": content})


def generate_response(prompt: str) -> str:
    """Generate a streamed response from Ollama API."""
    try:
        url = "http://llama3.zbb-api.wqketang.com/api/generate"
        payload = {
            'model': st.session_state.model_name,
            'prompt': f"作为一位资深广告专家，分析如何创造令人难忘的广告。请分步骤思考并详细说明：\n\n{prompt}",
            'stream': True
        }

        placeholder = st.empty()
        full_response = ""

        with st.spinner('AI正在思考...'):
            response = requests.post(url, json=payload, stream=True, timeout=3600)  # 1 hour timeout

            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line)
                        chunk = json_response.get('response', '')
                        full_response += chunk
                        placeholder.markdown(full_response)
                    except json.JSONDecodeError:
                        continue

        return full_response

    except requests.exceptions.ConnectionError:
        return "无法连接到服务器，请检查网络连接"
    except Exception as e:
        return f"系统错误: {str(e)}"


def display_chat_history():
    """Display all messages in the chat history."""
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def chat_lu():
    """Enhanced chat interface with context awareness."""
    st.title("💬 Chat with Advertising History")
    initialize_session_state()

    # Display chat history
    display_chat_history()

    # Handle new user input
    if prompt := st.chat_input("Ask about advertising history..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        update_chat_history("user", prompt)

        # Generate and display assistant response
        response = generate_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)
        update_chat_history("assistant", response)

if __name__ == "__main__":
    chat_lu()