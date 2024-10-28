import streamlit as st
import pandas as pd

def excel_processor_page():
    st.title("Excel File Processor")

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        spend_columns = [col for col in df.columns if 'Spend' in col]
        impression_columns = [col for col in df.columns if 'Impressions' in col]

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

        st.write("Copy and paste the following outputs:")
        st.code(spend_output, language="text")
        st.code(impression_output, language="text")
