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

    # List of variables to ignore when checking for zero coefficients
    ignore_vars = ['(Intercept)', 'trend', 'season', 'weekday', 'monthly', 'holiday']

    # Filter out the rows with the variables we want to ignore
    df_filtered = df[~df['rn'].isin(ignore_vars)]

    # Identify submodels where all relevant variables have non-zero coefficients
    all_non_zero_submodels = df_filtered.groupby('solID').filter(lambda x: (x['coef'] != 0).all())

    # Create a simplified summary with solID, average rsq_train, and average decomp.rssd
    if not all_non_zero_submodels.empty:
        non_zero_summary = all_non_zero_submodels.groupby('solID').agg(
            rsq_train_avg=('rsq_train', 'mean'),
            decomp_rssd_avg=('decomp.rssd', 'mean')
        ).reset_index()

        # Sort by rsq_train_avg in descending order
        non_zero_summary = non_zero_summary.sort_values(by='rsq_train_avg', ascending=False)
    else:
        non_zero_summary = pd.DataFrame()

    # Identify submodels with at least one zero-coefficient variable (excluding ignored variables)
    submodels_with_zeros = df_filtered[df_filtered['coef'] == 0]

    # Summarize zero-coefficient variables for each submodel
    summary = submodels_with_zeros.groupby('solID').agg(
        zero_count=('rn', 'count'),
        total_spend_on_zeros=('total_spend', 'sum'),
        zero_vars=('rn', lambda x: list(x)),
        rsq_train_avg=('rsq_train', 'mean'),
        decomp_rssd_avg=('decomp.rssd', 'mean')
    ).reset_index()

    # Reorder columns to place rsq_train_avg and decomp_rssd_avg after solID
    summary = summary[['solID', 'rsq_train_avg', 'decomp_rssd_avg', 'zero_count', 'total_spend_on_zeros', 'zero_vars']]

    # Format total spend values with dollar sign and comma separators
    summary['total_spend_on_zeros'] = summary['total_spend_on_zeros'].apply(
        lambda x: f"${x:,.2f}"
    )

    # Sort by the number of zero-coefficient variables (ascending order)
    summary = summary.sort_values(by='zero_count', ascending=True)

    # Display results in Streamlit
    st.subheader("Submodels where all relevant variables have non-zero coefficients (simplified):")
    if non_zero_summary.empty:
        st.write("No submodels found where all relevant variables have non-zero coefficients.")
    else:
        st.dataframe(non_zero_summary)

    st.subheader("Summary of submodels with zero-coefficient variables (excluding ignored variables):")
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
