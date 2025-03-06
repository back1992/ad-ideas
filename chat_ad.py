import os
from dotenv import load_dotenv
import requests
import streamlit as st
from typing import List, Dict
from requests.adapters import HTTPAdapter
import urllib3.util.retry
import json

# Load environment variables
load_dotenv()
OLLAMA_API_KEY = os.environ.get('OLLAMA_API_KEY')

def initialize_session_state():
    """Initialize session state variables with default values."""
    defaults = {
        "messages": [{"role": "system", "content": "You are an AI assistant knowledgeable about advertising history."}],
        "chat_history": [],
        "model_name": "llama3.1:8b-instruct-q4_0",  # Updated to match curl
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

def generate_response(prompt: str) -> str:
    """Generate a response using the Ollama API with retry mechanism and debugging."""
    if not OLLAMA_API_KEY:
        return "Error: API key not found in environment variables."

    # Match curl: Use HTTP instead of HTTPS
    url = "http://open-webui.zbb-api.wqketang.com/ollama/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {OLLAMA_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Start with minimal payload like curl, then add context
    payload = {
        'model': st.session_state.model_name,
        'messages': [{"role": "user", "content": prompt}],  # Simplified for testing
        'stream': False
    }

    # Uncomment to include context (after confirming minimal works)
    # context_messages = get_chat_context(st.session_state.messages)
    # context_messages.append({"role": "user", "content": prompt})
    # payload['messages'] = context_messages

    # Debug: Show the payload
    # st.write("DEBUG: Request Payload:", json.dumps(payload, indent=2))

    # Configure retry strategy
    retry_strategy = urllib3.util.retry.Retry(
        total=3,  # Reduced retries to speed up debugging
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    # Create session
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)

    try:
        with st.spinner('Generating response...'):
            response = session.post(
                url,
                headers=headers,
                json=payload,
                timeout=30  # Match curl’s quick response
            )
            response.raise_for_status()

            response_data = response.json()

            if 'choices' in response_data and response_data['choices']:
                content = response_data['choices'][0]['message']['content'].strip()
                if content:
                    return content
                return "Error: Empty response from API."
            return "Error: No valid response received from the API."

    except requests.exceptions.Timeout:
        st.error("Request timed out after 30 seconds. Server might be slow from this client.")
        return "Response generation timed out."
    except requests.exceptions.RequestException as e:
        error_detail = getattr(e.response, 'text', str(e)) if hasattr(e, 'response') else str(e)
        st.error(f"API Error: {error_detail}")
        return f"Error generating response: {error_detail}"
    finally:
        session.close()

def update_chat_history(role: str, content: str):
    """Update session state with new message."""
    if content:
        st.session_state.messages.append({"role": role, "content": content})
        st.session_state.chat_history.append({"role": role, "content": content})

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