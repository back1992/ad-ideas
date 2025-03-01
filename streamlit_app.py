import dotenv
import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# from chat_ad import initialize_session_state, generate_response
# from chat_ad import chat_lu
from classic_ad_100 import classic_ad
from homepage import intro
from pages import memorabilia, superstar, plotting_data


ENV = dotenv.dotenv_values(".env")

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

def load_config(file_path):
    """Load configuration from a YAML file."""
    with open(file_path) as file:
        return yaml.load(file, Loader=SafeLoader)

def privilege():
    """Handle user authentication and privileges."""
    config = load_config('./config.yaml')
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    name, authentication_status, username = authenticator.login('main', 'Login')

    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*')
        if username == 'jsmith':
            st.title('Application 1')
        elif username == 'rbriggs':
            st.title('Application 2')
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')

page_names_to_funcs = {
    "首页": intro,
    "广告大事年表": memorabilia,
    "20世纪广告百位巨星榜": superstar,
    "20世纪最成功的广告T0P100": classic_ad,
    "行业数据": plotting_data,
    "与大师对话": chat_lu,
    "会员": privilege
}

demo_name = st.sidebar.selectbox("请选择", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()