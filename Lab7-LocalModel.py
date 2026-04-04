import ollama
import streamlit as st
from ollama import chat
from ollama import web_search

# define the tool schema 
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
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {st.secrets['OLLAMA_API_KEY']}"}
)

# initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

# chatbot
if prompt := st.chat_input("Ask a question"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        messages = [{"role": "user", "content": prompt}]

        # detect if web search is needed
        no_web = client.chat(
            model='ministral-3:3b',
            messages=messages,
            tools=tools
        )

        # append assistant's response (including any tool calls)
        messages.append(no_web.message)

        if no_web.message.tool_calls:
            for tool_call in no_web.message.tool_calls:
                query = tool_call.function.arguments['query']

                # ollama web search
                search_results = web_search(query)
                results_text = "\n".join(
                    f"{r.title}: {r.content}" for r in search_results.results
                )
                messages.append({"role": "tool", "content": results_text})

        # generate final response with search context
        stream = client.chat(
            model='ministral-3:3b',
            messages=messages,  
            stream=True,
        )

        with st.chat_message("assistant"):
            def stream_response():
                for chunk in stream:
                    yield chunk.message.content
            full_response = st.write_stream(stream_response())

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"Error: {e}")
