import streamlit as st
from navigation import make_sidebar

make_sidebar()

def main():

    hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.title('Meeting Summarizer Web App User Guide')

    st.header('Getting Started')
    st.write("""
    This application is a web-based tool that helps you process and analyze meeting notes. You can upload a document (PDF, text, or Word file) and perform various actions like creating meeting notes, listing action items, and asking questions about the uploaded document.
    """)

    st.header('Instructions')
    st.subheader('1. Uploading a Document')
    st.write("""
    Click the `Browse files` button under the `Upload your PDF,TEXT,WORD file` section to upload your file. This file should contain your meeting transcript.
    """)

    st.subheader('2. Actions')
    st.write("""
    Below the file uploader, there are two buttons: `Create Meeting Notes` and `List Action Items`.
    - `Create Meeting Notes`: This button will generate a summary of the meeting transcript. It will structure the summary with the date, meeting title, agenda, attendees, meeting summary, and action items with assigned individuals.
    - `List Action Items`: This button will generate a list of action items from the meeting transcript. It organizes them by topic for easier tracking and follow-up.
    """)

    st.subheader('3. Set the Mode')
    st.write("""
    There are three modes to choose from: `Q&A`, `Summarize Meeting`, and `What Key Person Said?`.
    - `Q&A`: In this mode, you can ask a question about the meeting. Type your question into the provided text box and click `Submit`. The app will generate a response based on the meeting transcript.
    - `Summarize Meeting`: In this mode, you are asked to provide two prompts to guide the summary of the meeting transcript. The first prompt should describe how you want the transcript summarized, and the second prompt should describe how you want the output structured. After filling both prompts, click `Submit` to generate the summary.
    - `What Key Person Said?`: In this mode, you can select a key person from the meeting and generate a summary of what they said. Select the person's name from the dropdown list and click `Submit` to generate the summary.
    """)

    st.subheader('Additional Information')
    st.write("""
    The application also includes some customization options to improve the aesthetics and usability of the web interface. For example, the hamburger menu and footer are hidden, and a custom background image is used for the sidebar.
    """)

    st.subheader('Troubleshooting')
    st.write("""
    If you encounter any issues while using the application, please ensure that the uploaded document is in a valid format (PDF, text, Word) and contains a meeting transcript. If the issue persists, please contact the system administrator.
    """)

if __name__ == "__main__":
    main()
