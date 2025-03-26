import streamlit as st
from pathlib import Path
from st_pages import add_page_title, get_nav_from_toml


st.set_page_config(page_title="Attribution Multipage App", layout='wide')

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

#edit footer
page_style= """
    <style>
    footer{
        visibility: visible;
        }
    footer:after{
        content: 'Developed by Ali Maatouk - Analytics @ Data Sciences';
        display:block;
        position:relative;
        color:#1e54e4;
    }
    </style>"""

st.markdown(page_style, unsafe_allow_html=True)

sections = st.sidebar.toggle("Sections", value=True, key="use_sections")

nav = get_nav_from_toml(
    ".streamlit/pages_sections.toml" if sections else ".streamlit/pages.toml"
)

pg = st.navigation(nav)

add_page_title(pg)

pg.run()
