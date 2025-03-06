import os
from dotenv import load_dotenv
import requests
import streamlit as st
from typing import List, Dict

load_dotenv()
OLLAMA_API_KEY = os.environ.get('OLLAMA_API_KEY')

def initialize_session_state():
    """Initialize session state variables with default values."""
    defaults = {
        "messages": [{"role": "system", "content": "You are an AI assistant knowledgeable about advertising history."}],
        "chat_history": [],
        "model_name": "llamafamily/llama3-chinese-8b-instruct:latest",
        "collection_id": "2200479b-d722-45a4-ad06-06ea537f5af4"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_chat_context(messages: List[Dict[str, str]], max_context: int = 5) -> List[Dict[str, str]]:
    """Extract recent chat context up to max_context messages."""
    system_message = next((msg for msg in messages if msg["role"] == "system"), None)
    recent_messages = messages[-max_context*2:] if len(messages) > max_context*2 else messages

    context = []
    if system_message:
        context.append(system_message)
    context.extend(recent_messages)
    return context

def generate_response(prompt: str) -> str:
    """Generate a response using the Ollama API with chat context."""
    try:
        url = "http://open-webui.zbb-api.wqketang.com/ollama/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {OLLAMA_API_KEY}',
            'Content-Type': 'application/json'
        }

        # Get recent chat context
        context_messages = get_chat_context(st.session_state.messages)
        context_messages.append({"role": "user", "content": prompt})

        payload = {
            'model': st.session_state.model_name,
            'messages': context_messages,
            'files': [{'type': 'collection', 'id': st.session_state.collection_id}]
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()

        if 'choices' in response_data and response_data['choices']:
            return response_data['choices'][0]['message']['content']
        return "No response received from the API"

    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return f"Error generating response: {str(e)}"

def update_chat_history(role: str, content: str):
    """Update session state with new message."""
    st.session_state.messages.append({"role": role, "content": content})

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
        update_chat_history("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display response
        with st.chat_message("assistant"):
            response = generate_response(prompt)
            st.markdown(response)
            update_chat_history("assistant", response)