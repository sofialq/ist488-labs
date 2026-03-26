import streamlit as st

#multi-page application for all labs
lab1_page = st.Page('Lab1.py', title = "Lab 1")
lab2_page = st.Page('Lab2.py', title = "Lab 2")
lab3_page = st.Page('Lab3.py', title = "Lab 3")
lab4_page = st.Page('Lab4.py', title = "Lab 4")
lab5_page = st.Page('Lab5.py', title = "Lab 5")
lab6_page1 = st.Page('Lab6-openai_responses.py', title = "Lab 6- OpenAI Responses")
lab6_page2 = st.Page('Lab6-langchain.py', title = "Lab 6- LangChain")

pg = st.navigation([lab6_page2, lab6_page1, lab5_page, lab4_page, 
                    lab3_page, lab2_page, lab1_page]) # default to lab 6.2
st.set_page_config(page_title = 'IST 488 Labs')
pg.run()
