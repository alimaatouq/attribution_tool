import streamlit as st
import pandas as pd

# Streamlit app
st.title("Date Range Finder")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the Excel file
    try:
        data = pd.read_excel(uploaded_file)

        # Ensure there's a 'Date' column and parse dates
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            data = data.dropna(subset=['Date'])  # Drop rows with invalid dates
            
            # Get the start and end dates
            window_start = data['Date'].min().strftime('%Y-%m-%d')
            window_end = data['Date'].max().strftime('%Y-%m-%d')

            # Display the output code block
            st.code(f'window_start = "{window_start}"\nwindow_end = "{window_end}"', language='r')
        else:
            st.error("The uploaded file does not contain a 'Date' column.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload an Excel file to proceed.")
