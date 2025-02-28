import os
import tempfile
import dotenv
import openai
import requests
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader

# Load environment variables
ENV = dotenv.dotenv_values(".env")

openai.api_type = "azure"
openai.api_base = ENV["AZURE_OPENAI_ENDPOINT"]
openai.api_version = ENV["AZURE_OPENAI_API_VERSION"]
openai.api_key = ENV["AZURE_OPENAI_KEY"]

def initialize_session_state():
    """Initialize session state variables for Streamlit."""
    if "generated" not in st.session_state:
        st.session_state["generated"] = []
    if "past" not in st.session_state:
        st.session_state["past"] = []
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": ""}]
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = []
    if "cost" not in st.session_state:
        st.session_state["cost"] = []
    if "total_tokens" not in st.session_state:
        st.session_state["total_tokens"] = []
    if "total_cost" not in st.session_state:
        st.session_state["total_cost"] = 0.0

def generate_response_azure(prompt):
    """Generate a response using the OpenAI API."""
    st.session_state["messages"].append({"role": "user", "content": prompt})
    try:
        completion = openai.ChatCompletion.create(
            engine=ENV["AZURE_OPENAI_CHATGPT_DEPLOYMENT"],
            messages=st.session_state["messages"],
        )
        response = completion.choices[0].message.content
    except openai.error.APIError as e:
        response = f"The API could not handle this content: {str(e)}"
    st.session_state["messages"].append({"role": "assistant", "content": response})
    return response

def generate_response(prompt):
    """Generate a response using the Ollama API."""
    st.session_state["messages"].append({"role": "user", "content": prompt})
    try:
        url = "http://open-webui.zbb-api.wqketang.com/ollama/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {ENV['OLLAMA_API_KEY']}',
            'Content-Type': 'application/json'
        }
        model = "llama3.2"
        collection_id = "2200479b-d722-45a4-ad06-06ea537f5af4"
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'files': [{'type': 'collection', 'id': collection_id}]
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        print("Response Data:", response_data)  # Debugging line

        # Extract the assistant's response from the choices key
        if 'choices' in response_data and len(response_data['choices']) > 0:
            assistant_response = response_data['choices'][0]['message']['content']
        else:
            assistant_response = "No response from Ollama API"
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)  # Debugging line
        assistant_response = f"The API could not handle this content: {str(e)}"
    st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
    return assistant_response

def chat_lu():
    """Chat interface version 1."""
    st.title("💬 Chat with Advertising History")
    initialize_session_state()

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        response = generate_response(prompt)
        with st.chat_message("assistant"):
            st.write(response)

