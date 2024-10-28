import streamlit as st
from PathEditor import path_editor_page
from ExcelProcessor import excel_processor_page

# Set the page configuration
st.set_page_config(page_title="Multi-Page App", layout="wide")

# Initialize the session state to track the selected page
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "Home"

# Menu bar at the top
menu_options = ["Home", "Path Editor", "Excel Processor"]
selected_option = st.radio("Navigate", menu_options, horizontal=True)

# Update the session state based on the selected option
st.session_state["selected_page"] = selected_option

# Display the selected page content
if st.session_state["selected_page"] == "Home":
    st.title("Welcome to the Multi-Page Streamlit App!")
    st.write("Use the menu bar above to navigate between pages.")
elif st.session_state["selected_page"] == "Path Editor":
    path_editor_page()
elif st.session_state["selected_page"] == "Excel Processor":
    excel_processor_page()
