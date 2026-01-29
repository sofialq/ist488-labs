import streamlit as st
from openai import OpenAI
import requests

# initialize session state
if 'lab2_key' not in st.session_state: 
    st.session_state['lab2_key'] = 'value'

# Show title and description.
st.title("Lab 2")
st.write(" ")

st.title("📄 Document Summarization")
st.write(
    "Upload a document below and GPT will summarize it! "
    "This app uses a secret key."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
secret_key = st.secrets.OPEN_AI_KEY 

# Create an OpenAI client.
client = OpenAI(api_key=secret_key)

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md)", type=("txt", "md")
)
advanced_model = st.checkbox("Use advanced model")

# choose summary type in sidebar of page
st.sidebar.header("Summary Options") 
summary_type = st.sidebar.radio( "How do you want your document summarized?", 
                                ["100 words", "2 connecting paragraphs", "5 bullet points"] )

if uploaded_file:

    # create prompt 
    def create_prompt(text: str, summary_type: str) -> str: 
        if summary_type == "100 words": 
            return f"Summarize the following document in about 100 words:\n\n{text}" 
        elif summary_type == "2 paragraphs": 
            return f"Summarize the following document in 2 connecting paragraphs:\n\n{text}" 
        elif summary_type == "5 bullet points": 
            return f"Summarize the following document in 5 bullet points:\n\n{text}" 
        else: 
            return f"Summarize the following document:\n\n{text}"

    # Process the uploaded file.
    document = uploaded_file.read().decode()
    prompt = create_prompt(document, summary_type)
    messages = [ {"role": "system", "content": "You are a helpful assistant."}, 
                {"role": "user", "content": prompt} ]

    # Generate an answer using prompt and the OpenAI API.
    model = "gpt-5-nano"
    if advanced_model: 
        model = "gpt-4o"

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=1
    )

    # Stream the response to the app using `st.write_stream`.
    st.write(f"Summarizing your document in {summary_type}")
    st.write_stream(stream)