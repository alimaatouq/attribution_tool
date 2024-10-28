import streamlit as st
import pandas as pd
from hydralit_components import Navbar
from io import BytesIO

# App Configuration
st.set_page_config(
    page_title="Excel Processor & Path Editor",
    layout='wide'
)

# Define the top menu using hydralit_components
menu_data = [
    {'label': "Upload & Process Excel"},
    {'label': "Path Editor"}
]

# Create the navigation bar
choice = Navbar(menu_data=menu_data, sticky_nav=True, sticky_mode='pinned')

# Excel Processor Functionality
def upload_process_excel():
    st.title("Excel Processor")
    st.write("Upload your Excel file to extract 'Spend' and 'Impressions' columns.")

    # Step 1: Upload the Excel file
    uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])

    if uploaded_file is not None:
        # Step 3: Load the Excel data into a DataFrame
        df = pd.read_excel(uploaded_file)

        # Step 4: Identify columns containing the word 'Spend' and 'Impressions'
        spend_columns = [col for col in df.columns if 'Spend' in col]
        impression_columns = [col for col in df.columns if 'Impressions' in col]

        # Step 5 & 6: Format the columns to match your requested output
        spend_output = (
            'paid_media_spends = c(\n    "' +
            '",\n    "'.join(spend_columns) +
            '")'
        )

        impression_output = (
            'paid_media_vars = c(\n    "' +
            '",\n    "'.join(impression_columns) +
            '")'
        )

        # Step 7: Display both outputs
        st.write("Copy and paste the following outputs:")
        st.code(spend_output, language="text")
        st.code(impression_output, language="text")

# Path Editor Functionality
def path_editor():
    st.title("Path Editor - Double Backslashes")
    st.write("Paste your folder path below:")

    # User input for the folder path
    user_input = st.text_input("Enter the path:")

    # Process and display the modified path
    if user_input:
        edited_path = double_backslashes(user_input)
        st.write("**Edited Path:**")
        st.code(edited_path, language="text")

# Function to double backslashes
def double_backslashes(path):
    # Handle both backslashes and forward slashes
    path = path.replace('\\', '\\\\')  # Double backslashes
    path = path.replace('/', '\\\\')   # Replace forward slashes with double backslashes
    return path

# Render the selected page based on the menu choice
if choice == "Upload & Process Excel":
    upload_process_excel()
elif choice == "Path Editor":
    path_editor()
