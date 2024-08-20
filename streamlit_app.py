import streamlit as st
import streamlit_authenticator as stauth

from classic_ad_100 import classic_ad
# from streamlit_authenticator import Authenticate

from pages import intro, memorabilia, superstar,  plotting_data, chat_lu

import yaml
from yaml.loader import SafeLoader


# hashed_passwords = stauth.Hasher(['abc', 'def']).generate()

# st.write(f'Welcome *{hashed_passwords}*')


# name, authentication_status, username = authenticator.login('main', 'Login')
# if authentication_status:
#     authenticator.logout('Logout', 'main')
#     if username == 'jsmith':
#         st.write(f'Welcome *{name}*')
#         st.title('Application 1')
#     elif username == 'rbriggs':
#         st.write(f'Welcome *{name}*')
#         st.title('Application 2')
# elif not authentication_status:
#     st.error('Username/password is incorrect')
# elif authentication_status is None:
#     st.warning('Please enter your username and password')

def privilege():
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
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
        if username == 'jsmith':
            st.write(f'Welcome *{name}*')
            st.title('Application 1')
        elif username == 'rbriggs':
            st.write(f'Welcome *{name}*')
            st.title('Application 2')
    elif not authentication_status:
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
