import streamlit as st

#multi-page application for all labs
lab1_page = st.Page('Lab1.py', title = "Lab 1")
lab2_page = st.Page('Lab2.py', title = "Lab 2")
lab3_page = st.Page('Lab3.py', title = "Lab 3")

pg = st.navigation([lab3_page, lab2_page, lab1_page]) # default to lab 3
st.set_page_config(page_title = 'IST 488 Labs')
pg.run()
