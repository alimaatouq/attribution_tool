import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Multipage App", layout='wide')

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to", 
    ["Path Editor", "Paid Media Spends", "Submodel Analysis"]
)

# Load and display the appropriate page
if page == "Path Editor":
    exec(Path("pages/Path_Editor.py").read_text(), globals())
elif page == "Paid Media Spends":
    exec(Path("pages/Paid_Media_Spends_Vars.py").read_text(), globals())
elif page == "Submodel Analysis":
    exec(Path("pages/Sub_Model_Analysis.py").read_text(), globals())
