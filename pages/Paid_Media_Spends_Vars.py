import streamlit as st
import pandas as pd

# Streamlit App Title
st.title("Excel Column Extractor")

# Step 1: Check if the uploaded file exists in session state
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None

# Step 2: File uploader, only if no file in session state
if st.session_state["uploaded_file"] is None:
    uploaded_file = st.file_uploader("Please upload your Processed Data Excel file", type=["xlsx"])
    if uploaded_file:
        st.session_state["uploaded_file"] = uploaded_file  # Save to session state
else:
    st.success("Using previously uploaded file.")

# Step 3: Use the uploaded file from session state
uploaded_file = st.session_state["uploaded_file"]

if uploaded_file:
    # Step 4: Load the Excel data into a DataFrame
    df = pd.read_excel(uploaded_file)

    # Step 5: Identify columns containing 'Spend' and 'Impressions'
    spend_columns = [col for col in df.columns if 'Spend' in col]
    impression_columns = [col for col in df.columns if 'Impressions' in col]

    # Step 6: Format the 'Spend' columns
    spend_output = (
        'paid_media_spends = c(\n    "' +
        '",\n    "'.join(spend_columns) +
        '")'
    )

    # Step 7: Format the 'Impressions' columns
    impression_output = (
        'paid_media_vars = c(\n    "' +
        '",\n    "'.join(impression_columns) +
        '")'
    )

    # Step 8: Display the outputs
    st.subheader("Copy the following outputs:")
    st.code(spend_output, language='R', line_numbers=False, wrap_lines=True)
    st.code(impression_output, language='R', line_numbers=False, wrap_lines=True)
else:
    st.info("Please upload an Excel file to proceed.")
