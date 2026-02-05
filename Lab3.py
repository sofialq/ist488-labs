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
    [{"role": "system", "content": "You are a helpful assistant. "
    "Always explain things in a simple way a 10-year-old can understand"},
      {"role": "assistant", "content": "How can I help you?"}]

if "more_info" not in st.session_state:
    st.session_state.more_info = False

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.more_info:
        lower = prompt.lower().strip()

        if lower == "yes":
            system_msg = st.session_state.messages[0] 
            conversation = st.session_state.messages[1:] 
            buffer = conversation[-4:] # keep last two messages from user
            messages = [system_msg] + buffer # implement conversation buffer

            client = st.session_state.client
            stream = client.chat.completions.create(
                model = model,
                messages = messages, 
                stream = True
            )
            with st.chat_message("assistant"): 
                more_info = st.write_stream(stream)

            more_info_answer = more_info + "\n\nDo you want more info?"
            st.session_state.messages.append({"role": "assistant", "content": more_info_answer})

        elif lower == "no":
            reply = "what else can I help you with?"
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.more_info = False
        else: 
            reply = "Please reply with Yes or No." 
            st.session_state.messages.append({"role": "assistant", "content": reply})

    else:
        system_msg = st.session_state.messages[0] 
        conversation = st.session_state.messages[1:] 
        buffer = conversation[-4:] # keep last two messages from user
        messages = [system_msg] + buffer # implement conversation buffer

        client = st.session_state.client
        stream = client.chat.completions.create(
            model = model,
            messages = messages, 
            stream = True
        )

        with st.chat_message("assistant"):
            response = st.write_stream(stream)

        final_response = response + "\n\nDo you want more info?"

        st.session_state.messages.append({"role": "assistant", "content": final_response})

        st.session_state.more_info = True

for msg in st.session_state.messages:
    #st.chat_message(msg["role"]).write(msg["content"])
    #with st.chat_message(msg["roles"]):
    #   st.write(msg["content"])
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])


