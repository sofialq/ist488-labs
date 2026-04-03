import ollama
import streamlit as st
from ollama import chat

# define tool schema 
import ollama

# Step 1: Define the tool schema (like Lab 5's get_current_weather tool)
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information based on the user's question",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# create client
client = ollama.Client(
    api_key=st.secrets["OLLAMA_API_KEY"]
)

# initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

# chatbot
if prompt := st.chat_input("Ask a question"):
    st.write(f"you said: {prompt}")
    
    try:
        no_web = client.chat(
            model='mistral:latest',
            messages=[{"role": "user", "content": prompt}],
            tools=tools
        )

        messages=[{"role": "user", "content": prompt}]

        if no_web.message.tool_calls:
            for tool_call in no_web.message.tool_calls:
                query = tool_call.function.arguments['query']

                web_search = ollama.web_search(prompt)

                messages.append({"role": "tool", "content": str(web_search)})

        stream = client.chat(
            model='mistral:latest',
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        # stream response and save to session state
        with st.chat_message("assistant"):
            def stream_response():
                for chunk in stream:
                    yield chunk.message.content
            full_response = st.write_stream(stream_response())
    except Exception as e:
        st.error(f"Error: {e}")
