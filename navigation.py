import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
from streamlit_msal import Msal


def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]


def make_sidebar():
    with st.sidebar:
        # Retrieve the name from session state
        name = st.session_state.name
        st.image("images/nc_header.png")
        #st.title("💎 NathCorp")
        st.write(f"Hello, {name} !")
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):
            st.page_link("pages/Meeting_Notes.py", label="Meeting Summarizer", icon="📜")
            st.page_link("pages/Transcript_Fetch.py", label="Meeting Summarizer via Mail", icon="📃")
            st.page_link("pages/User_Guide.py", label="User Guide", icon="📒")
            
            st.write("")
            st.write("")

            # Custom CSS for card-like buttons
            # Custom CSS for card-like buttons
            st.markdown("""
            <style>
            
                div.stButton > button:first-child {
                    height: 50px;
                    width: 340px;
                    
                }
                
                .output {
                    height: 600px;
                    overflow-y: auto;                
                    background-color: #e8f9ee;
                    border: 0px solid #ccc;                
                    border-radius: 3px;
                    padding: 23px;
                    font-family: 'Lucida Console', monospace;
                    font-weight: normal;
                    space: pre-wrap;
                
                }
            </style>
            """, unsafe_allow_html=True)


            if st.button("Log out"):
                logout()

        elif 'accessToken' not in st.session_state:
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("Login.py")


def logout():
    st.session_state.logged_in = False
    Msal.sign_out()
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("Login.py")