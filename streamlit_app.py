import streamlit as st

#multi-page application for all labs
lab1_page = st.Page('Lab1.py', title = "Lab 1")
lab2_page = st.Page('Lab2.py', title = "Lab 2")

pg = st.navigation([lab2_page, lab1_page]) # default to lab 2
st.set_page_config(page_title = 'IST 488 Labs')
pg.run()
