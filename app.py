import streamlit as st
import pandas as pd
import hydralit_components as hc  # For the top navigation bar

# Page configuration
st.set_page_config(page_title="Streamlit App with Top Menu", layout="wide")

# Define menu data
menu_data = [
    {'label': "Overview", 'icon': 'bi bi-bar-chart-line'},
    {'label': "EDA", 'icon': "bi bi-graph-up-arrow"},
    {'label': "Tableau", 'icon': 'bi bi-clipboard-data'},
    {'label': "Application", 'icon': 'fa fa-brain'}
]

# Customize theme
over_theme = {
    'txc_inactive': 'white',
    'menu_background': 'rgb(0,0,128)',
    'option_active': 'white'
}

# Render the top navigation bar
menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    hide_streamlit_markers=True,
    sticky_nav=True,
    sticky_mode='sticky'  # Can also be 'pinned'
)

# Handle menu selection and display corresponding content
if menu_id == "Overview":
    st.title("Overview")
    st.write("This is the overview section. Use the top menu to navigate.")
    
elif menu_id == "EDA":
    st.title("Exploratory Data Analysis (EDA)")
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("First five rows of your data:")
        st.write(df.head())
        
elif menu_id == "Tableau":
    st.title("Tableau Section")
    st.write("This section could include Tableau integration or iframe embedding.")

elif menu_id == "Application":
    st.title("Application - Path Editor")
    user_input = st.text_input("Enter the path:")

    def double_backslashes(path):
        path = path.replace('\\', '\\\\')
        path = path.replace('/', '\\\\')
        return path

    if user_input:
        edited_path = double_backslashes(user_input)
        st.write("**Edited Path:**")
        st.code(edited_path, language="text")
