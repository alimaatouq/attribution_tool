import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Attribution Multipage App", layout='wide')

# Load and display the appropriate page
if page == "Path Editor":
    exec(Path("pages/Path_Editor.py").read_text())
elif page == "Paid Media Spends":
    exec(Path("pages/Paid_Media_Spends_Vars.py").read_text())
elif page == "Submodel Analysis":
    exec(Path("pages/Sub_Model_Analysis.py").read_text())
