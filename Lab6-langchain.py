import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# initialize llm
llm = init_chat_model(
    model="claude-haiku-4-5-20251001",
    model_provider="anthropic",
    temperature=0,
    max_tokens=1024,
)

# Show title and description.
st.title("Lab 6 with LangChain")
st.write(" ")
st.title("Movie Recommendation Chatbot")
st.write("Get movie recommendations and learn about the suggested options!")