import base64
import json
import os
import requests
import streamlit as st
import datetime
from urllib.parse import unquote,urlparse, parse_qs
import re
from Scripts.Summarize import display_result, clean_text, extract_text, generate_response
#from urllib.parse import 
#import st_state_patch
from navigation import make_sidebar
from datetime import datetime, timedelta, date

make_sidebar()

# Microsoft Graph API endpoint
graph_api_url = "https://graph.microsoft.com/v1.0"

POWER_AUTOMATE_URL = os.getenv("POWER_AUTOMATE_URL")


# Extract attendees from the transcript
def extract_attendees(transcript):
    pattern = re.compile(r"(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*:")
    matches = pattern.findall(transcript)
    attendees = sorted(set(matches), key=matches.index)
    return attendees

# Generate formatted attendees list
def format_attendees(attendees):
    return "\n".join(f"- {attendee}" for attendee in attendees)


# Function to get access token
def get_access_token():
    # You need to implement your own method to obtain the access token,
    # such as using Microsoft Authentication Library (MSAL) or OAuth 2.0.
    # Return the access token here.
    access_token=st.session_state.access_token
    return access_token

# Function to make API requests
#@st.cache
def call_graph_api(access_token,endpoint):
    #access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    full_url=graph_api_url + endpoint
    print("full_url",full_url)
    response = requests.get(full_url, headers=headers)
    return response.json()

def call_graph_api_for_transcripts(access_token, endpoint):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    full_url = endpoint
    response = requests.get(full_url, headers=headers)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')
        if 'application/json' in content_type:
            return response.json()
        else:
            return response.text
    else:
        return None, None  # Handle errors if needed
    
# Define function to convert date string to Microsoft Graph API format
#@st.cache
def convert_to_ms_graph_date2(date):
    if date is None:
        return None
    else:
        return date.strftime('%Y-%m-%dT%H:%M:%SZ')

def convert_to_ms_graph_date(date_input):
    if date_input is None:
        return None
    elif isinstance(date_input, str):
        # Convert string to datetime object
        date_obj = datetime.strptime(date_input, '%Y-%m-%d')
    elif isinstance(date_input, date):
        # Convert date object to datetime object (if necessary)
        date_obj = datetime.combine(date_input, datetime.min.time())
    elif isinstance(date_input, datetime):
        date_obj = date_input
    else:
        raise TypeError("The input must be a string, datetime.date, or datetime.datetime object")
    
    # Format the datetime object
    return date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')    


# Function to format Meeting ID 
def formatting_id(oid_value,meeting_id):
    formatted_value=f"1*{oid_value}*0**{meeting_id}"
    print("formatted_value",formatted_value)
    return formatted_value

#@st.cache
def get_meeting_data(access_token, start_date_ms_graph, end_date_ms_graph):
    endpoint = f"/me/calendarview?startdatetime={start_date_ms_graph}&enddatetime={end_date_ms_graph}&$count=true&$filter=isCancelled ne true"
    meeting_data = call_graph_api(access_token, endpoint)
    return meeting_data

def get_meeting_data_filter_on_subject(access_token, start_date_ms_graph, end_date_ms_graph,subject_filter):
    endpoint = f"/me/calendarview?startdatetime={start_date_ms_graph}&enddatetime={end_date_ms_graph}&$count=true&$filter=isCancelled ne true and subject eq '{subject_filter}'"
    meeting_data = call_graph_api(access_token, endpoint)
    return meeting_data

def get_meeting_data_filter_on_subject_and_id(access_token, start_date_ms_graph, end_date_ms_graph, subject_filter,selected_id):
    endpoint = f"/me/calendarview?startdatetime={start_date_ms_graph}&enddatetime={end_date_ms_graph}&$count=true&$filter=isCancelled ne true and id eq '{selected_id}'"
    meeting_data = call_graph_api(access_token, endpoint)
    return meeting_data

def get_meeting_data_eventid(access_token, start_date_ms_graph, end_date_ms_graph,selected_id):
    # Create the endpoint to directly access the event by its ID
    endpoint = f"/me/events/{selected_id}"
    meeting_data = call_graph_api(access_token, endpoint)
    return meeting_data

def get_parsed_url(join_urls):
    decoded_url = unquote(join_urls[0])
    #st.write("decoded_url ",decoded_url)
    parsed_url = urlparse(decoded_url)
    return parsed_url

def get_meeting_id(parsed_url):
    path_segments = parsed_url.path.split('/')
    meeting_id = path_segments[3]
    print("Meeting ID:", meeting_id)
    #st.write("Meeting ID:", meeting_id)
    return meeting_id

def get_oid(parsed_url):
    query_params = parse_qs(parsed_url.query)
    oid_value = query_params['context'][0].split('"Oid":"')[1].split('"')[0]
    print("Oid Value:", oid_value)
    #st.write("Oid Value:", oid_value)
    return oid_value

def base64encoding(formatted_id):
    encoded_string = base64.b64encode(formatted_id.encode()).decode()
    print("encoded_string",encoded_string)
    #st.write("encoded_string",encoded_string)
    return encoded_string

#@st.cache
def get_online_meeting_data(access_token, encoded_string):
    onlineMeeting_endpoint = f"/me/onlineMeetings/{encoded_string}"
    onlineMeeting_endpoint_data = call_graph_api(access_token, onlineMeeting_endpoint)
    return onlineMeeting_endpoint_data

def get_online_meeting_List_transcript_data(access_token,start_date_ms_graph, end_date_ms_graph, encoded_string):
    onlineMeeting_endpoint = f"/me/onlineMeetings/{encoded_string}/transcripts"
    onlineMeeting_endpoint_data = call_graph_api(access_token, onlineMeeting_endpoint)
    return onlineMeeting_endpoint_data

def get_online_meeting_call_transcript_id_prev(access_token,start_date_ms_graph, end_date_ms_graph, encoded_string):
    onlineMeeting_endpoint = f"/me/onlineMeetings/{encoded_string}/transcripts?$filter=createdDateTime ge {start_date_ms_graph} and createdDateTime le {end_date_ms_graph}"
    onlineMeeting_endpoint_data = call_graph_api(access_token, onlineMeeting_endpoint)
    return onlineMeeting_endpoint_data



def get_online_meeting_call_transcript_id(access_token, start_date_ms_graph, end_date_ms_graph, encoded_string):
    # Construct the endpoint without the filter
    onlineMeeting_endpoint = f"/me/onlineMeetings/{encoded_string}/transcripts"
    
    # Fetch all transcripts for the meeting
    onlineMeeting_endpoint_data = call_graph_api(access_token, onlineMeeting_endpoint)
    
    # Filter the transcripts based on the date range
    filtered_transcripts = []
    for transcript in onlineMeeting_endpoint_data.get('value', []):
        transcript_date = transcript.get('createdDateTime')
        if transcript_date and start_date_ms_graph <= transcript_date <= end_date_ms_graph:
            filtered_transcripts.append(transcript)
    
    return filtered_transcripts


def get_online_meeting_call_transcript_data(access_token,transcript_content_urls):
    onlineMeetingTranscript_endpoint = f"{transcript_content_urls}?$format=text/vtt"
    print("onlineMeetingTranscript_endpoint:", onlineMeetingTranscript_endpoint)
    #st.write("onlineMeetingTranscript_endpoint:", onlineMeetingTranscript_endpoint)
    onlineMeeting_endpoint_data = call_graph_api_for_transcripts(access_token, onlineMeetingTranscript_endpoint)
    return onlineMeeting_endpoint_data

def get_online_meeting_call_transcript_data2(access_token,encoded_string,transcriptId):
    onlineMeetingTranscript_endpoint = f"/me/onlineMeetings/{encoded_string}/transcripts/{transcriptId}/content?$format=text/vtt"
    print("onlineMeetingTranscript_endpoint:", onlineMeetingTranscript_endpoint)
    #st.write("onlineMeetingTranscript_endpoint:", onlineMeetingTranscript_endpoint)
    onlineMeeting_endpoint_data = call_graph_api(access_token, onlineMeetingTranscript_endpoint)
    return onlineMeeting_endpoint_data

def parse_chat_log(chat_log):
    messages = []
    pattern = re.compile(r'<v (.*?)>(.*?)<\/v>')
    for line in chat_log.split('\n'):
        match = pattern.search(line)
        if match:
            username = match.group(1)
            message = match.group(2)
            messages.append((username, message))
    return messages

# Include all action items by ensuring all names are checked in the prompt or post-process
def ensure_all_action_items(transcript, meeting_notes, attendees):
    for attendee in attendees:
        if attendee.split()[0] not in meeting_notes:
            name_regex = re.compile(rf'{attendee.split()[0]}.*?:.*')
            matches = name_regex.findall(transcript)
            if matches:
                meeting_notes += f"\n   {attendee.split()[0]}: \n      - " + "\n      - ".join([match.split(':')[-1].strip() for match in matches])
    return meeting_notes

def get_access_token_powerAutomate():
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    #scope = 'https://graph.microsoft.com/.default'
    #scope = f'{client_id}/.default'
    scope = 'https://service.flow.microsoft.com//.default'
    
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    body = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }
    
    response = requests.post(url, headers=headers, data=body)
    
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        if not access_token:
            st.error("Access token not found in the response.")
            return None
        return access_token
    else:
        st.error("Failed to obtain access token.")
        st.error(f"Response status: {response.status_code}")
        st.error(f"Response content: {response.content}")
        return None

def power_automateflow(organizer_upn, attendee_upns, meeting_notes, selected_subject, transcript_date):
    access_token = get_access_token_powerAutomate()
    #st.write("access_token",access_token)
    if not access_token:
        st.error("Access token retrieval failed.")
        return
    
    mail_subject = f"Meeting Notes of {selected_subject} on {transcript_date}"
    # Data to be sent
    transcript_data = {
        'organizer_upn': organizer_upn,
        'attendee_upns': attendee_upns,
        'meeting_notes': meeting_notes,
        'mail_subject': mail_subject
    }

    # Set the headers with the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Power Automate flow endpoint URL
    power_automate_url = os.getenv("POWER_AUTOMATE_URL")
    if not power_automate_url:
        st.error("Power Automate URL is not set.")
        return

    # Making the POST request to Power Automate flow
    response = requests.post(power_automate_url, headers=headers, json=transcript_data)
    #print("response",response)
    if response.status_code in [200, 202]:
        st.success("Meeting Notes sent successfully for organizer's approval!")
        st.success("Check your mail once they approve.")
    else:
        st.error(f"Failed to send Meeting Notes. Status code: {response.status_code}")
        st.error(f"Response content: {response.content}")
        print(f"Failed to send Meeting Notes. Status code: {response.status_code}")
        print(f"Response content: {response.content}")


# Function to add one day to a given date
def add_one_day(date_str):
    if isinstance(date_str, date):
        # Convert date object to string
        date_str = date_str.strftime('%Y-%m-%d')
    elif not isinstance(date_str, str):
        raise TypeError("The input must be a string or a datetime.date object")
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    next_day = date_obj + timedelta(days=1)
    return next_day.strftime('%Y-%m-%d')    

def create_meeting_dict(meetings):
    meeting_dict = {}
    for meeting in meetings:
        subject = meeting["subject"]
        meeting_id = meeting["id"]
        meeting_dict[subject] = meeting_id
    return meeting_dict  

def create_meeting_dict(subjects, ids):
    meeting_dict = {}
    for subject, meeting_id in zip(subjects, ids):
        meeting_dict[subject] = meeting_id
    return meeting_dict

def create_meeting_list_dict(subjects, ids,createdDateTimes):
    return [{"subject": subject, "id": meeting_id, "createdDateTime": createdDateTime} for subject, meeting_id, createdDateTime in zip(subjects, ids, createdDateTimes)]

# Function to convert the given timestamp to a datetime object
def convert_timestamp(timestamp_str):
    # Removing the 'Z' and parsing manually to handle extra precision
    timestamp_str = timestamp_str.rstrip('Z')
    dt = datetime.strptime(timestamp_str[:26], "%Y-%m-%dT%H:%M:%S.%f")
    return dt


def main():
    st.title("Meeting Notes by Mail")

    # Date input for start date
    start_date = st.date_input("Enter Meeting Date", value=None)
    #st.write(start_date)
    # Date input for end date
    #end_date = st.date_input("Enter End Date", value=None)
   
    access_token = get_access_token()
    #st.write("access_token",access_token)
    
    if start_date :
        start_date_ms_graph = convert_to_ms_graph_date(start_date)
        end_date = add_one_day(start_date)
        #st.write("end_date",end_date)
        end_date_ms_graph = convert_to_ms_graph_date(end_date)
        
        meeting_data = st.cache_data(get_meeting_data)(access_token, start_date_ms_graph, end_date_ms_graph)
        #st.write("meeting_data:", meeting_data)
        
        if meeting_data and "value" in meeting_data:
            meetings = [(event["subject"], event["id"], event["createdDateTime"]) for event in meeting_data["value"]]
            subjects = [meeting[0] for meeting in meetings]
            ids = [meeting[1] for meeting in meetings]
            createdDateTimes = [meeting[2] for meeting in meetings]
            # Create the meeting dictionary
            meeting_list_dict = create_meeting_list_dict(subjects, ids, createdDateTimes)
            #st.write("subjects:", subjects)
            #st.write("ids:", ids)
            #st.write("meeting_list_dict:", meeting_list_dict)

            if meeting_list_dict:
                #formated_timestamp=convert_timestamp()
               # Convert meeting subjects with creation date
                subject_with_date = [
                    f"{meeting['subject']} (CreatedOn: {convert_timestamp(meeting['createdDateTime'])})" for meeting in meeting_list_dict
                ]

                # Streamlit app
                # st.title("Meeting Selector")

                
                # Dropdown to select a meeting subject
                selected_meeting_str = st.selectbox("Select a meeting:", subject_with_date)

                # Extract the selected subject and createdDateTime from the selected string
                selected_subject, selected_date = selected_meeting_str.rsplit(" (CreatedOn: ", 1)
                selected_date = selected_date.rstrip(")")

                # Find the meeting with the selected subject and createdDateTime
                selected_meeting = next(
                    meeting for meeting in meeting_list_dict
                    if meeting["subject"] == selected_subject and convert_timestamp(meeting["createdDateTime"]) == datetime.fromisoformat(selected_date)
                )


                # Display the created date and time
                #st.write(f"Created DateTime: {selected_meeting['createdDateTime']}")

                # Display the meeting ID
                #st.write(f"Meeting ID: {selected_meeting['id']}")

                selected_Meeting_ID= selected_meeting['id']
                #st.write(f"selected_Meeting_ID:", selected_Meeting_ID)

            # # Initialize session state
            # if "selected_index" not in st.session_state:
            #     st.session_state.selected_index = None

            # subject_meeting_data = None  # Initialize subject_meeting_data here    

            # # Generate unique subject names by appending a unique identifier to duplicates
            # unique_subjects = [f"{subject} ({i+1})" if subjects.count(subject) > 1 else subject for i, subject in enumerate(subjects)]

            # selected_subject = st.selectbox("Select Meeting", options=unique_subjects, index=None, placeholder="Select Meeting ...")
            # if selected_subject in subjects:
            #     selected_index = subjects.index(selected_subject)
            #     selected_id = ids[selected_index]
            #     st.write("You selected:", selected_subject)
            #     st.write("ID associated with the selected meeting:", selected_id)
                
                #subject_meeting_data = st.cache_data(get_meeting_data_filter_on_subject)(access_token, start_date_ms_graph, end_date_ms_graph, selected_subject)
                #subject_meeting_data = st.cache_data(get_meeting_data_filter_on_subject_and_id)(access_token, start_date_ms_graph, end_date_ms_graph, selected_subject,selected_Meeting_ID)
                subject_meeting_data = st.cache_data(get_meeting_data_eventid)(access_token, start_date_ms_graph, end_date_ms_graph, selected_Meeting_ID)
                #st.write("subject_meeting_data",subject_meeting_data)

                #if subjects and ids:
                # selected_index = st.selectbox(
                #     "Select Meeting", 
                #     subjects, 
                #     index=st.session_state.selected_index or 0,
                #     placeholder="Select Meeting ..."
                # )
                # st.session_state.selected_index = selected_index

                # if isinstance(selected_index, int):
                #     selected_subject = subjects[selected_index]
                #     selected_id = ids[selected_index]
                #     #st.session_state.selected_index = selected_index  # Store selected index in session state
                #     st.write("You selected:", selected_subject)
                #     st.write("You selected_id:", selected_id)
                #     subject_meeting_data = st.cache_data(get_meeting_data_filter_on_subject)(
                #         access_token,
                #         start_date_ms_graph,
                #         end_date_ms_graph,
                #         selected_subject,
                #         selected_id
                #     )
                



                
                if isinstance(subject_meeting_data, list):  # Check if subject_meeting_data is a list
                    join_urls = [event.get("onlineMeeting", {}).get("joinUrl") for event in subject_meeting_data]
                elif isinstance(subject_meeting_data, dict):  # Check if subject_meeting_data is a dictionary
                    join_urls = [subject_meeting_data.get("onlineMeeting", {}).get("joinUrl")]

                    if join_urls:
                        parsed_url = st.cache_data(get_parsed_url)(join_urls)
                        meeting_id = st.cache_data(get_meeting_id)(parsed_url)
                        oid = st.cache_data(get_oid)(parsed_url)
                        formatted_id = st.cache_data(formatting_id)(oid, meeting_id)
                        encoded_string = st.cache_data(base64encoding)(formatted_id)
                        
                        onlineMeeting_data = st.cache_data(get_online_meeting_data)(access_token, encoded_string)
                        #st.write("onlineMeeting_data:", onlineMeeting_data)
                        if 'participants'in onlineMeeting_data:
                            organizer_upn = onlineMeeting_data['participants']['organizer']['upn']
                            attendee_upns = [attendee['upn'] for attendee in onlineMeeting_data['participants']['attendees']]
                            #st.write("organizer_upn:", organizer_upn)
                            #st.write("attendee_upns:", attendee_upns)

                            transcript_data_id = st.cache_data(get_online_meeting_call_transcript_id)(access_token, start_date_ms_graph, end_date_ms_graph, encoded_string)
                            #st.write("transcript_data:", transcript_data_id)

                            if transcript_data_id:
                                transcript_id = transcript_data_id[0]['id']
                                transcript_content_url = transcript_data_id[0]['transcriptContentUrl']
                                #st.write("transcript_id:", transcript_id)
                                #st.write("transcript_content_url:", transcript_content_url)

                                transcript_data = st.cache_data(get_online_meeting_call_transcript_data)(access_token, transcript_content_url)
                                
                                if transcript_data:
                                    st.subheader("Transcript Content:")
                                    st.text_area("Transcript", transcript_data, height=400)

                                    if st.button("📧 Get Meeting Notes by Mail"):
                                        with st.spinner("Processing file..."):
                                            content = transcript_data
                                            messages = parse_chat_log(content)
                                            formatted_messages = [f"{username}: {message}" for username, message in messages]
                                            formatted_transcript = "\n".join(formatted_messages)
                                            #st.text_area("Transcript Cleaned", formatted_transcript, height=400)

                                            attendees = extract_attendees(formatted_transcript)
                                            formatted_attendees = format_attendees(attendees)
                                            transcript_date = start_date.strftime("%B %d, %Y")

                                            prompt_request_1 = "Summarize this meeting transcript: "
                                            prompt_request_2 = "Please thoroughly review the provided meeting transcript. I need you to ensure and compile all the points topic wise into a concise, easy-to-understand format, resembling natural human writing. Organize the content under main heading 'Meeting Notes', where you list all the relevant points discussed during the meeting in a straightforward manner."
                                            response = generate_response(formatted_transcript, prompt_request_1, prompt_request_2)
                                            meeting_notes = ensure_all_action_items(formatted_transcript, response, attendees)
                                            #st.text_area("Meeting Notes:", meeting_notes, height=400)
                                            #st.write("response", response)
                                            power_automateflow(organizer_upn,attendee_upns,meeting_notes,selected_subject,transcript_date)
                                else:
                                    st.error("Failed to fetch transcript content.")
                            else:
                                st.write("No transcript data available for the selected meeting.")
                        else:
                            st.write("No meeting details available for the selected subject.")         
                    else:
                        st.write("No join URLs found for the selected subject.")
                else:
                    st.write("No meeting data available for the selected subject.")
            else:
                st.write("The list of subjects is empty.")
        else:
            st.write("No meeting data available.")
    else:
        st.write("Please provide Meeting date.")

if __name__ == "__main__":
    main()
