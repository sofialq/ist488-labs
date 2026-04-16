import streamlit as st

#multi-page application for all labs
lab1_page = st.Page('Lab1.py', title = "Lab 1")
lab2_page = st.Page('Lab2.py', title = "Lab 2")
lab3_page = st.Page('Lab3.py', title = "Lab 3")
lab4_page = st.Page('Lab4.py', title = "Lab 4")
lab5_page = st.Page('Lab5.py', title = "Lab 5")
responses_page = st.Page('Lab6-responses.py', title = "Lab 6- OpenAI Responses")
langchain_page = st.Page('Lab6-langchain.py', title = "Lab 6- LangChain")
localmodel_page = st.Page('Lab7-LocalModel.py', title = "Lab 7- Local Model")
rag_page = st.Page('Lab8-RAG.py', title = "Lab 8- RAG Reranking")
mas_page = st.Page('Lab9-MAS.py', title = "Lab 9- MAS")

pg = st.navigation([mas_page, rag_page, localmodel_page, langchain_page, responses_page, lab5_page, lab4_page, 
                    lab3_page, lab2_page, lab1_page]) # default to lab 9
st.set_page_config(page_title = 'IST 488 Labs')
pg.run()
