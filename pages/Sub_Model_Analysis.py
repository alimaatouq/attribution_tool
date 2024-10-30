import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook

def convert_csv_to_excel(csv_file):
    """Convert CSV to Excel format."""
    df = pd.read_csv(csv_file)
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl', sheet_name='Sheet1')
    excel_file.seek(0)
    return excel_file

def analyze_file(uploaded_file):
    # Load the Excel file into a DataFrame
    df = pd.read_excel(uploaded_file, engine='openpyxl')

    # Identify submodels where all variables have non-zero coefficients
    all_non_zero_submodels = df.groupby('solID').filter(lambda x: (x['coef'] != 0).all())

    # Identify submodels with at least one zero-coefficient variable
    submodels_with_zeros = df[df['coef'] == 0]

    # Summarize zero-coefficient variables for each submodel
    summary = submodels_with_zeros.groupby('solID').agg(
        zero_count=('rn', 'count'),
        total_spend_on_zeros=('total_spend', 'sum'),
        zero_vars=('rn', lambda x: list(x)),
        rsq_train_avg=('rsq_train', 'mean')  # Calculate the average rsq_train for each solID
    ).reset_index()

    # Reorder columns to place rsq_train_avg after solID
    summary = summary[['solID', 'rsq_train_avg', 'zero_count', 'total_spend_on_zeros', 'zero_vars']]

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

# File uploader widget (supports CSV and Excel)
uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["xlsx", "csv"])

# Analyze the uploaded file if it is provided
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        # Convert CSV to Excel format
        uploaded_file = convert_csv_to_excel(uploaded_file)
    analyze_file(uploaded_file)
