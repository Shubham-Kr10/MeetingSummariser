import streamlit as st
import datetime
from Scripts.Summarize import display_result, clean_text, extract_text, generate_response
from navigation import make_sidebar

make_sidebar()

# Get current date
current_date = datetime.date.today()

# Format date as string (e.g. "May 1, 2023")
formatted_date = current_date.strftime("%B %d, %Y")

def main():
    # st.set_page_config(page_title='Meeting Notes', page_icon=':clipboard:')
    # st.image("images/nc_header.png")
    st.header(':clipboard: Meeting Summarizer ')

    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    uploaded_file = st.file_uploader('Upload your transcript (PDF, Text, Word file)', type=['pdf','txt','docx','doc']) 
    
    names = set()
    warning_placeholder = st.empty()
    message_missing_file = "Please upload a valid file before proceeding"
    
    
    if uploaded_file is not None:
        transcript = extract_text(uploaded_file)  
        lines = transcript.strip().split('\n')
        names = [lines[i+1] for i in range(len(lines)) if '-->' in lines[i]]
        names = list(set(names)) 
    else:   
        warning_placeholder.empty()
        warning_placeholder.warning(message_missing_file) 

    # text = ""

    st.write("Actions:")

    st.markdown("""
        <style>
            div.stButton > button:first-child {
                height: 50px;
                width: 340px;
            }
            .output {
                color: black; /* Set text color to black */
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

    col1, col2 = st.columns(2)

    with col1:
        create_meeting_notes = st.button(":memo: Create Meeting Notes", key="button2")        
        
    with col2:
        list_action_items =  st.button(":scroll: List Action Items", key="button1")

    with st.expander("Advanced Options"):
        mode = st.radio(
            "Set the mode:",
            ["Q&A", "Summarize Meeting", "What Key Person Said?"],
            key="visibility",
            disabled=False,
            horizontal= True,
        )

        if mode == 'Q&A':
            if uploaded_file is not None:
                user_question_placeholder = st.empty()
                user_question = user_question_placeholder.text_input(':man-raising-hand: Ask your question',key='user_question', value="")
                submit_button = st.button("Submit")
                if submit_button and user_question != "":
                    if uploaded_file is not None:            
                        with st.spinner("Processing file..."):
                            text = extract_text(uploaded_file)                
                            text = clean_text(text)
                            prompt_request_1 = user_question +" : " 
                            prompt_request_2 = "Consolidate: "
                            response = generate_response(text, prompt_request_1, prompt_request_2)
                    else:
                        warning_placeholder.empty()
                        warning_placeholder.warning(message_missing_file) 
                    display_result(response)  
                    user_question = ""
            else:
                warning_placeholder.empty()
                warning_placeholder.warning(message_missing_file)       
            
        elif mode == 'Summarize Meeting':
            if uploaded_file is not None:        
                
                #st.write('You selected Summarize Meeting.')
                prompt_1_placeholder = st.empty()
                prompt_request_1 = prompt_1_placeholder.text_input(':thinking_face: How would you like to summarize the transcript?',key='prompt_1')
                prompt_2_placeholder = st.empty()
                prompt_request_2 = prompt_2_placeholder.text_input(':thinking_face: How would you like to structure the output?',key='prompt_2')
                # Create a submit button
                #submit_button = st.button("Submit")
                # Custom CSS for the submit button
                st.markdown("""
                <style>
                    .btn-custom {
                        background-color: #f63366;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 5px;
                        border: none;
                        cursor: pointer;
                    }
                    .btn-custom:hover {
                        background-color: #fa7c92;
                        }
                </style>
                """, unsafe_allow_html=True)


                # Create an HTML submit button with the custom style
                #submit_button = st.markdown('<button class="btn-custom" >Submit</button>', unsafe_allow_html=True)
                submit_button = st.button("Submit")


                # Check if the submit button is clicked
                if submit_button and (prompt_request_1 !="" and prompt_request_2 !=""):
                    #st.write("Submit button clicked")
                    with st.spinner("Processing file..."):
                            text = extract_text(uploaded_file)
                            text = clean_text(text)                                         
                            response = generate_response(text, prompt_request_1, prompt_request_2)
                        
                    display_result(response)
                    prompt_request_1 = prompt_1_placeholder.text_input(':thinking_face: How would you like to summarize the transcript?', value="", key='prompt_1')
            
                    prompt_request_2 = prompt_2_placeholder.text_input(':thinking_face: How would you like to structure the output?', value="", key='prompt_2')
                    #st.success("Successfully submitted: {} and {}".format(prompt_request_1, prompt_request_2))
            
                #elif submit_button and ( (not prompt_request_2 and not prompt_request_1) or (not prompt_request_2 and prompt_request_1) or ( prompt_request_2 and not prompt_request_1)):
                elif submit_button and ( (not prompt_request_2 and not prompt_request_1) or (not prompt_request_2 and prompt_request_1) or ( prompt_request_2 and not prompt_request_1) or (prompt_request_2 !="" or prompt_request_1 !="")):
                    #pass
                    st.warning("Please fill both input fields and click the submit button.")


                # Check if both inputs are filled and the submit button is clicked
                #if submit_button and prompt_request_1 and prompt_request_2:
                #    st.success("Successfully submitted: {} and {}".format(prompt_request_1, prompt_request_2))
                #else:
                #    if submit_button:
                #        st.warning("Please fill both input fields and click the submit button.")
            else:
                warning_placeholder.empty()
                warning_placeholder.warning(message_missing_file)     

        elif mode == 'What Key Person Said?':  

            #st.write("You selected Summarize Meeting What Key Person Said?")
            if uploaded_file is not None:  
                
                # Add a placeholder to the start of the list
                key_person_placeholder = st.empty()

                
                # Create an HTML submit button with the custom style
                
                st.markdown("""
                <style>
                    .btn-custom {
                        background-color: #f63366;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 5px;
                        border: none;
                        cursor: pointer;
                    }
                    .btn-custom:hover {
                        background-color: #fa7c92;
                        }
                </style>
                """, unsafe_allow_html=True)
                #submit_button = st.markdown('<button class="btn-custom" >Submit</button>', unsafe_allow_html=True)
            

                options = names
                selected_name = key_person_placeholder.multiselect("Select name from the list:", options)
                # Check if a real name was selected or typed          

                key_persons=""
                for name in selected_name:
                    key_persons = key_persons +',' + name

                    
                #key_person_placeholder = key_person_placeholder.selectbox(':office_worker: Type Key Person Name', options, key='key_person')

                #st.write('You selected:', selected_name)
                #key_person_placeholder = key_person_placeholder.text_input(':office_worker: Type Key Person Name',key='key_person')
            
                
                submit_button= st.button("Submit")
                if submit_button and selected_name and len(selected_name) > 0 and selected_name[0] != "Select a name...":
                
                #if key_person_placeholder  is not None :                     
                        with st.spinner("Processing file..."):
                            text = extract_text(uploaded_file)
                            #text = clean_text(text)
                            text = clean_text(text)
                            prompt_request_1 = "Summarize what "+ key_persons +" said in this meeting transcript: "
                            prompt_request_2 = "Consolidate these meeting summaries in bullet point: "
                            response = generate_response(text, prompt_request_1, prompt_request_2)
                            
                            #response = ask_question_from_transcript(text, user_question)
                        
                        display_result(response)
                elif submit_button and selected_name and len(selected_name) > 0 and selected_name[0] == "Select a name...":
                    st.warning("Please select a valid name and click the submit button.")
            else:
                warning_placeholder.empty()
                warning_placeholder.warning(message_missing_file)
            
            key_person_placeholder = ""


        

    if list_action_items:
        # user_question_placeholder.text_input(':man-raising-hand: Ask your question',key=user_question, value="")
        if uploaded_file is not None:
            with st.spinner("Processing file..."):
                text = extract_text(uploaded_file)
                text = clean_text(text)
                prompt_request_1 = "Provide a list of action items from the provided meeting transcript text: "
                #prompt_request_2 = "Consolidate these meeting action items and organize them by topic for easier tracking and follow-up. First, write a brief summary of the key takeaways from the meeting. Next, group the action items by relevant topics, assign responsible parties and due dates. Be clear and concise:" 
                prompt_request_2 = "Please thoroughly review the provided meeting transcript. I need you to ensure and compile all the points topics wise into a concise, easy-to-understand format, resembling natural human writing. Organize the content under the heading 'Action Items', under which you should itemize all the tasks or follow-ups identified in the meeting in a straightforward manner."
                response = generate_response(text, prompt_request_1, prompt_request_2)
            display_result(response)
        else:
            warning_placeholder.empty()
            warning_placeholder.warning(message_missing_file)
            
    if create_meeting_notes:
        if uploaded_file is not None:
            with st.spinner("Processing file..."):
                text = extract_text(uploaded_file)
                prompt_request_1 = "Summarize this meeting transcript: "
                # prompt_request_2 = "Consolidate meeting summaries and create a structured meeting note with the date "+ formatted_date +", meeting title, agenda, attendees, meeting summary, and action items with assigned individuals. Use bullet points or numbered lists to organize the information and make it easy to read. Be concise and clear in your writing."
                prompt_request_2 = "Please thoroughly review the provided meeting transcript. I need you to ensure and compile all the points topic wise into a concise, easy-to-understand format, resembling natural human writing. Organize the content under the heading 'Meeting Notes', where you list all the relevant points discussed during the meeting in a straightforward manner."
                response = generate_response(text, prompt_request_1, prompt_request_2)
            display_result(response)
        else:
            warning_placeholder.empty()
            warning_placeholder.warning(message_missing_file)    

if __name__ == '__main__':
    main()