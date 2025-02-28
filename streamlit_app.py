import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from chat_ad import chat_lu
from classic_ad_100 import classic_ad
from homepage import intro
from pages import memorabilia, superstar, plotting_data

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