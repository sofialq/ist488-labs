import streamlit as st
from ollama import chat

st.write("app loaded")

if prompt := st.chat_input("Ask a question"):
    st.write(f"you said: {prompt}")
    
    try:
        stream = chat(
            model='mistral:latest',
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        with st.chat_message("assistant"):
            def stream_response():
                for chunk in stream:
                    yield chunk.message.content
            full_response = st.write_stream(stream_response())
    except Exception as e:
        st.error(f"Error: {e}")