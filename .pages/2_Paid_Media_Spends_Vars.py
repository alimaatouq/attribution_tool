import streamlit as st
import pandas as pd
import pyperclip

# Streamlit App Title
st.title("Excel Column Extractor")

# Step 1: Upload the Excel file
uploaded_file = st.file_uploader("Please upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Step 2: Load the Excel data into a DataFrame
    df = pd.read_excel(uploaded_file)

    # Step 3: Identify columns containing 'Spend' and 'Impressions'
    spend_columns = [col for col in df.columns if 'Spend' in col]
    impression_columns = [col for col in df.columns if 'Impressions' in col]

    # Step 4: Format the 'Spend' columns
    spend_output = (
        'paid_media_spends = c(\n    "' +
        '",\n    "'.join(spend_columns) +
        '")'
    )

    # Step 5: Format the 'Impressions' columns
    impression_output = (
        'paid_media_vars = c(\n    "' +
        '",\n    "'.join(impression_columns) +
        '")'
    )

    # Step 6: Display the outputs
    st.subheader("Copy the following outputs:")
    st.code(spend_output, language='text')
    st.code(impression_output, language='text')

    # Step 7: Button to copy to clipboard
    if st.button("Copy to Clipboard"):
        pyperclip.copy(spend_output + "\n\n" + impression_output)
        st.success("Copied to clipboard!")
