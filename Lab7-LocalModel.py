import streamlit as st
from ollama import chat

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
        stream = chat(
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
