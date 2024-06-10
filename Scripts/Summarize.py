from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
import docx
import re
from transformers import AutoTokenizer
import datetime
import os
import openai
import openai_async
import asyncio
import base64
import streamlit as st

# Get current date
current_date = datetime.date.today()

# Format date as string (e.g. "May 1, 2023")
formatted_date = current_date.strftime("%B %d, %Y")

load_dotenv()

# Initialise environment variables

openai.api_key = os.getenv("OPENAI_API_KEY")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
MODEL = os.getenv("MODEL")

import asyncio
from openai import AsyncOpenAI
client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def display_result(text):  
            
    
    
    response = text
    #st.write(response)  
    st.write("Result:")

    # Input your text here
    input_text = response
     
    # Display the formatted text in a box with fixed height and auto scroll   
    # Wrap the response text with the 'output' class to apply the custom CSS
    response_text = f"<div class='output'>{input_text}</div>"
    st.markdown(response_text, unsafe_allow_html=True)
    


    # Generate the download link for the text
    download_link = text_to_download_link(input_text, "Result.txt")
    st.markdown(download_link, unsafe_allow_html=True)       
    
    
    
def text_to_download_link(text, filename):
   
    b64 = base64.b64encode(text.encode()).decode()    
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}">Download Result</a>'
    
    return href


    

def clean_text(text):
    # Remove lines starting and ending with '0'
    lines = text.split('\n')
    lines = [line for line in lines if not ((line.startswith('1') or line.startswith('0')) and line.endswith('0'))]

    # Remove any unnecessary text or formatting
    cleaned_lines = []
    for line in lines:
        # Remove leading and trailing whitespaces
        cleaned_line = line.strip()
        # Remove any unnecessary text/formatting (e.g., replace multiple whitespaces with a single space)
        cleaned_line = ' '.join(cleaned_line.split())
        cleaned_lines.append(cleaned_line)

    # Remove newline characters
    cleaned_text = ' '.join(cleaned_lines)
        
    cleaned_text = cleaned_text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    cleaned_text = re.sub('\s+', ' ', cleaned_text)  
    return cleaned_text

def extract_text(uploaded_file):
    text = ""
    file_type = uploaded_file.type
    if file_type == 'application/pdf':
        pdf_reader = PdfReader(uploaded_file)            
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
            
    elif file_type == 'text/plain':
        #print(uploaded_file.name)
        # Open the file and read its contents
        #text = uploaded_file.read().decode('utf-8')
        text = uploaded_file.getvalue().decode('utf-8')
        #st.success(text)
        return text
            
    
    elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        doc = docx.Document(uploaded_file)        
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'
        return text
    else:
        text = None
        st.write('File not supported') 
        return text

# Starting AI Functions

async def summarize_meeting(prompt, timeout, max_tokens):
       
    temperature = float(os.getenv("temperature"))   
    top_p = 1
    frequency_penalty = 0
    presence_penalty = 0
    timeout = None
    
    # Call the OpenAI GPT-3 API
    # response = await openai_async.complete(
    #     openai.api_key,
    #     timeout=timeout,
    #     payload={
    #         "model": "text-davinci-004",
    #         "prompt": prompt,
    #         "temperature": temperature,
    #         "max_tokens": max_tokens,
    #         "top_p": top_p,
    #         "frequency_penalty": frequency_penalty,
    #         "presence_penalty": presence_penalty
    #     },
    # )
    
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=MODEL,
        temperature = temperature
    )

    # Return the generated text
    return response

def break_up_text_to_chunks(text, chunk_size=2000, overlap=100):
    tokenizer = AutoTokenizer.from_pretrained("gpt2")    

 
    tokens = tokenizer.encode(text)
    num_tokens = len(tokens)
    
    chunks = []
    for i in range(0, num_tokens, chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks


def generate_response(text,prompt_request_1,prompt_request_2):
    
    prompt_response = []
    prompt_tokens = []

    chunks = break_up_text_to_chunks(text)

    for i, chunk in enumerate(chunks):
        prompt_request = prompt_request_1 + tokenizer.decode(chunks[i])
        
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(summarize_meeting(prompt = prompt_request, timeout=120, max_tokens = 1000))
        
        #prompt_response.append(response.json()["choices"][0]["text"].strip())
        #prompt_tokens.append(response.json()["usage"]["total_tokens"])
        prompt_response.append(response.choices[0].message.content)
        prompt_tokens.append(response.usage.total_tokens)

  
    prompt_request = prompt_request_2 + str(prompt_response)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    summary= loop.run_until_complete(summarize_meeting(prompt = prompt_request, timeout=60, max_tokens = 1000))

    # Print the total tokens used
    prompt_token_total = 0
    for e in range(0, len(prompt_tokens)):
        prompt_token_total = prompt_token_total + prompt_tokens[e]

    print("Total prompt usage in tokens: ", prompt_token_total)
    
    #return(summary.json()["choices"][0]["text"].strip())
    return(summary.choices[0].message.content)

#print(summarize_meeting(prompt = "Hi", timeout=120, max_tokens = 1000))

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# response = loop.run_until_complete(summarize_meeting(prompt = "Compose a poem that explains the concept of recursion in programming.", timeout=120, max_tokens = 1000))
        

# print(response.choices[0].message.content)
# print(response.usage.total_tokens)


# from openai import OpenAI
# client = OpenAI()

# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     #{"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )

# print(completion.choices[0].message.content)





# Function to break up text into chunks
# Function to break up text into chunks
# def break_up_text_to_chunks_transcipt_fetch(text, max_chunk_size=3000):
#     chunks = []
#     current_chunk = []
#     current_length = 0
    
#     for line in text.strip().split('\n'):
#         if current_length + len(line) > max_chunk_size:
#             chunks.append('\n'.join(current_chunk))
#             current_chunk = []
#             current_length = 0
#         current_chunk.append(line)
#         current_length += len(line)
    
#     if current_chunk:
#         chunks.append('\n'.join(current_chunk))
    
#     return chunks

# # Function to summarize meeting using OpenAI API
# async def summarize_meeting_transcipt_fetch(prompt, timeout, max_tokens):
#     response = openai.Completion.create(
#         engine="text-davinci-003",
#         prompt=prompt,
#         max_tokens=max_tokens,
#         n=1,
#         stop=None,
#         temperature=0.7
#     )
#     return response

# # Main function to generate the response
# def generate_response_transcipt_fetch(text, prompt_request_1, prompt_request_2):
#     prompt_response = []
#     prompt_tokens = []

#     chunks = break_up_text_to_chunks_transcipt_fetch(text)

#     for i, chunk in enumerate(chunks):
#         prompt_request = prompt_request_1 + "\n\n" + chunk
        
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         response = loop.run_until_complete(summarize_meeting_transcipt_fetch(prompt=prompt_request, timeout=120, max_tokens=1000))
        
#         prompt_response.append(response.choices[0].text.strip())
#         prompt_tokens.append(response.usage.total_tokens)

#     consolidated_summaries = "\n".join(prompt_response)
#     prompt_request = prompt_request_2 + consolidated_summaries
    
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     summary = loop.run_until_complete(summarize_meeting_transcipt_fetch(prompt=prompt_request, timeout=60, max_tokens=1000))

#     prompt_token_total = sum(prompt_tokens)
#     print("Total prompt usage in tokens: ", prompt_token_total)
    
#     return summary.choices[0].text.strip()

