import streamlit as st
import pandas as pd
from openpyxl import load_workbook

def analyze_file(uploaded_file):
    # Load the Excel file into a DataFrame
    df = pd.read_excel(uploaded_file)

    # Identify submodels where all variables have non-zero coefficients
    all_non_zero_submodels = df.groupby('solID').filter(lambda x: (x['coef'] != 0).all())
    
    # Identify submodels with at least one zero-coefficient variable
    submodels_with_zeros = df[df['coef'] == 0]

    # Summarize zero-coefficient variables for each submodel
    summary = submodels_with_zeros.groupby('solID').agg(
        zero_count=('rn', 'count'),
        total_spend_on_zeros=('total_spend', 'sum'),
        zero_vars=('rn', lambda x: list(x))
    ).reset_index()

    # Sort by the number of zero-coefficient variables (ascending order)
    summary = summary.sort_values(by='zero_count', ascending=True)
    # Format total spend values with dollar sign and comma separators
    summary['total_spend_on_zeros'] = summary['total_spend_on_zeros'].apply(
        lambda x: f"${x:,.2f}"
    )
    # Display results in Streamlit
    st.subheader("Submodels where all variables have non-zero coefficients:")
    if all_non_zero_submodels.empty:
        st.write("No submodels found where all variables have non-zero coefficients.")
    else:
        st.write(all_non_zero_submodels['solID'].unique())

    st.subheader("Summary of submodels with zero-coefficient variables:")
    if summary.empty:
        st.write("No submodels with zero-coefficient variables found.")
    else:
        st.dataframe(summary)

# Streamlit App UI
st.title("Submodel Analysis App")

# File uploader widget
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# Analyze the uploaded file when it is provided
if uploaded_file:
    analyze_file(uploaded_file)
