import streamlit as st
from openai import OpenAI


# initialize session state
if 'lab3_key' not in st.session_state: 
    st.session_state['lab3_key'] = 'value'
    
# Show title and description.
st.title("Lab 3")
st.write(" ")

st.title("MY Lab3 questions answering chatbot")

openAI_model = st.sidebar.selectbox("Which Model?",
                                    ("mini", "regular"))

if openAI_model == "mini":
    model = "gpt-4o-mini"
else:
    model = "gpt-4o"

# create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = \
    [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    #st.chat_message(msg["role"]).write(msg["content"])
    #with st.chat_message(msg["roles"]):
    #   st.write(msg["content"])
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    client = st.session_state.client
    stream = client.chat.completions.create(
        model = model,
        messages = st.session_state.messages,
        stream = True
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})



