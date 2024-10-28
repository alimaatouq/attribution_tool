import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Attribution Multipage App", layout='wide')
st.sidebar.success("Select a demo above.")

st.write("# Welcome to the Attribution Tool! 👋")

st.markdown("""
An all-in-one platform designed to streamline your data handling tasks. This app offers powerful tools to assist with path editing, media spend analysis, and submodel evaluations. Navigate through the pages using the sidebar to access the following features:

\n📂 ***Path Editor***

Easily reformat file paths by converting slashes to double backslashes for use in various environments. Perfect for Windows directory paths or coding scenarios requiring special formatting.
\n📊 ***Paid Media Spends Analyzer***

Upload your Excel files to extract columns related to media spends and impressions. Quickly copy pre-formatted outputs for further use in R or other statistical tools.
\n 📈 ***Submodel Analysis Tool***

Analyze models from Excel or CSV files to identify submodels with non-zero coefficients and generate insightful summaries. Understand where zero-coefficient variables impact your spend and optimize your strategies effectively.
""")
