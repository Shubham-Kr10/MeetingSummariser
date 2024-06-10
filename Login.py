import streamlit as st
from streamlit_msal import Msal
import os
from time import sleep
# Define Azure AD settings
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'

# with st.sidebar:
#     auth_data = Msal.initialize_ui(
#         client_id=CLIENT_ID,
#         authority=AUTHORITY,
#         scopes=[], # Optional
#         # Customize (Default values):
#         connecting_label="Connecting",
#         disconnected_label="Disconnected",
#         sign_in_label="Sign in",
#         sign_out_label="Sign out"
#     )

# st.write(f"Hello {name}!")
# st.write("Protected content available")
def login():
     
    st.image("images/nc_header.png")
    st.title("Welcome to Meeting Summarizer")
    auth_data = Msal.initialize_ui(
                client_id=CLIENT_ID,
                authority=AUTHORITY,
                scopes=[], # Optional
                # Customize (Default values):
                connecting_label="Connecting",
                disconnected_label="Disconnected",
                sign_in_label="Sign in",
                sign_out_label="Sign out"
            )

    if not auth_data:
            st.write("Please authenticate to access Meeting Summarizer")
            st.stop()
    return  auth_data       

# account = auth_data["account"]
# print("account", account)

# name = account["name"]
# print("name", name)


if 'accessToken' not in st.session_state:
    
    authValues=login()
    account = authValues["account"]
    print("account", account)

    name = account["name"]
    print("name", name)
    # Getting useful information
    access_token = authValues["accessToken"]
    print("access_token", access_token)
    if account:
        st.session_state.logged_in = True
        # Store the name and access token in session state
        st.session_state.name = name
        st.session_state.access_token = access_token
        st.success("Logged in successfully!")
        print("Session State:", st.session_state)
        sleep(0.5)
    
        st.switch_page("pages/Meeting_Notes.py")
else:
    #st.session_state.logged_in = True
    #authValues=login()
    # account = authValues["account"]
    # print("account", account)

    # name = account["name"]
    # print("name", name)
    # Store the name and access token in session state
    # st.session_state.name = name
    st.success('You are already logged in.')
    print("Session State2:", st.session_state)
    st.switch_page("pages/Meeting_Notes.py")
