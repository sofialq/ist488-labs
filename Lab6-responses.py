import streamlit as st
from openai import OpenAI
from pydantic import BaseModel

# openai client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Show title and description.
st.title("Lab 6 with OpenAI Responses API")
st.write(" ")
st.title("Questions Chatbot")
st.write("Ask the bot any questions you have in mind! " \
"This bot uses a multi-turn agent that uses a built-in tool and maintains conversation state without manually managing a message history list.")
st.write(" ")


# initialize session state
if "last_response_id" not in st.session_state:
    st.session_state.last_response_id = None

if "previous_question" not in st.session_state:
    st.session_state.previous_question = ""

if "response" not in st.session_state:
    st.session_state.response = None

if "follow_up" not in st.session_state:
    st.session_state.follow_up = ""

if "key_facts" not in st.session_state:
    st.session_state.key_facts = None

if "source_hint" not in st.session_state:
    st.session_state.source_hint = None


# return structured summary
st.sidebar.write("Check for agent to return structured object instead of free text.")
return_structured = st.sidebar.checkbox("Return structured summary")

class ResearchSummary(BaseModel):
    main_answer: str
    key_facts: list[str]
    source_hint: str

if not return_structured:
    st.session_state.key_facts = None
    st.session_state.source_hint = None


# user input
question = st.text_input("Ask any question: ")
st.caption("User agent has web search enabled.")
st.divider()

# bot call
if question and question != st.session_state.previous_question:
    
    st.session_state.follow_up = ""
    st.session_state.previous_question = question

    if return_structured:
        response = client.responses.parse(
            model="gpt-4.1-mini",
            instructions=(
                "You are a helpful research assistant. Always cite your sources in your response. "
                "Give user potential follow up questions they can ask."
            ),
            input=question,
            tools=[{"type": "web_search_preview"}],
            text_format=ResearchSummary
        )

        st.session_state.last_response_id = response.id
        
        parsed_output = next(
            (item.content[0].parsed for item in response.output
            if hasattr(item, "content") and item.content and hasattr(item.content[0], "parsed")),
            None
        )

        if parsed_output:
            st.session_state.response = parsed_output.main_answer
            st.session_state.key_facts = parsed_output.key_facts
            st.session_state.source_hint = parsed_output.source_hint

    else:
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=(
                "You are a helpful research assistant. Always cite your sources in your response. "
                "Give user potential follow up questions they can ask."
            ),
            input=question,
            tools=[{"type": "web_search_preview"}],
        )

        st.session_state.last_response_id = response.id
        st.session_state.response = response.output_text

if st.session_state.response:
    st.write(st.session_state.response)

    if st.session_state.key_facts:
        st.subheader("Key Facts")
        for fact in st.session_state.key_facts:
            st.markdown(f"- {fact}")
    if st.session_state.source_hint:
        st.caption(st.session_state.source_hint)


# follow up question
if st.session_state.last_response_id:
    st.divider()
    follow_up = st.text_input("Any follow-up questions? ",
                                  key="follow_up")

    if follow_up:
        follow_up_response = client.responses.create(
            model = "gpt-4.1-mini",
            instructions = "You are a helpful research assistant. Always cite your sources in your response." \
            "If information from the first response is used, include that in citations for the follow-up." \
            "Reference the first response given to go into more detail. Don't prompt user to ask more questions in follow-up response.",
            input = follow_up,
            tools = [{"type": "web_search_preview"}],
            previous_response_id = st.session_state.last_response_id
        )

        st.write(follow_up_response.output_text)