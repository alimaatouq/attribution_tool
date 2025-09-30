import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from openpyxl import load_workbook

def convert_csv_to_excel(csv_file):
    """Convert CSV to Excel format (in-memory) to standardize file handling."""
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None
        
    excel_file = BytesIO()
    # Write to BytesIO object (in-memory Excel)
    df.to_excel(excel_file, index=False, engine='openpyxl', sheet_name='Sheet1')
    excel_file.seek(0)
    return excel_file

def analyze_file(uploaded_file):
    """
    Analyzes the uploaded pareto_aggregated file to identify submodels
    with zero-coefficient variables, specifically focusing on variables
    containing 'own' in their name and calculating their spend percentage.
    """
    # Load the Excel file into a DataFrame
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return

    # Ensure required columns exist
    required_cols = ['rn', 'solID', 'coef', 'total_spend', 'rsq_train', 'decomp.rssd']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing one or more required columns: {', '.join(required_cols)}")
        return

    # List of variables to ignore when checking for coefficients
    ignore_vars = ['(Intercept)', 'trend', 'season', 'weekday', 'monthly', 'holiday']

    # Filter out the rows with the variables we want to ignore
    df_filtered = df[~df['rn'].isin(ignore_vars)].copy()

    # --- Part 1: All Non-Zero Submodels ---
    # Identify submodels where all relevant variables have non-zero coefficients
    all_non_zero_submodels = df_filtered.groupby('solID').filter(lambda x: (x['coef'] != 0).all())

    if not all_non_zero_submodels.empty:
        non_zero_summary = all_non_zero_submodels.groupby('solID').agg(
            rsq_train_avg=('rsq_train', 'mean'),
            decomp_rssd_avg=('decomp.rssd', 'mean')
        ).reset_index()

        # Sort by rsq_train_avg in descending order
        non_zero_summary = non_zero_summary.sort_values(by='rsq_train_avg', ascending=False)
    else:
        non_zero_summary = pd.DataFrame()

    # --- Part 2: Submodels with 'Own' Zero-Coefficient Variables ---

    # 1. Identify ALL 'own' variables (for total spend calculation denominator)
    # Case=False makes the search case-insensitive ('Own', 'own', 'OWN' are included)
    df_own_vars = df_filtered[df_filtered['rn'].str.contains('own_', case=False, na=False)].copy()

    # 2. Calculate total spend on ALL 'own' variables per submodel (Denominator)
    total_own_spend = df_own_vars.groupby('solID')['total_spend'].sum().reset_index()
    total_own_spend.rename(columns={'total_spend': 'total_spend_on_all_own'}, inplace=True)

    # 3. Identify all zero-coefficient variables (excluding ignored)
    submodels_with_zeros = df_filtered[df_filtered['coef'] == 0].copy()

    # 4. Filter the zero-coefficient variables to include ONLY those with 'own' in their name (Numerator variables)
    submodels_with_own_zeros = submodels_with_zeros[
        submodels_with_zeros['rn'].str.contains('own', case=False, na=False)
    ].copy()

    # If no 'own' zero variables are found, initialize an empty summary
    if submodels_with_own_zeros.empty:
        summary = pd.DataFrame()
    else:
        # 5. Summarize the 'own' zero-coefficient variables for each submodel
        summary_own_zeros = submodels_with_own_zeros.groupby('solID').agg(
            own_zero_count=('rn', 'count'), # Count of 'own' zero variables
            total_spend_on_own_zeros=('total_spend', 'sum'), # Total spend on 'own' zero variables (numerator)
            own_zero_vars=('rn', lambda x: list(x)), # List of 'own' zero variables
            rsq_train_avg=('rsq_train', 'mean'),
            decomp_rssd_avg=('decomp.rssd', 'mean')
        ).reset_index()

        # 6. Merge the total spend on all 'own' variables into the summary
        summary = pd.merge(summary_own_zeros, total_own_spend, on='solID', how='left')
        
        # Fill NaN values (where a solution has zero-coef 'own' variables but somehow no total 'own' spend)
        summary['total_spend_on_all_own'] = summary['total_spend_on_all_own'].fillna(0)

        # 7. Calculate the percentage of spend on 'own' zero-coef variables
        # Use np.divide for safe division, returning 0 where denominator is 0
        summary['pct_spend_on_own_zeros'] = np.divide(
            summary['total_spend_on_own_zeros'] * 100,
            summary['total_spend_on_all_own'],
            out=np.zeros_like(summary['total_spend_on_own_zeros'], dtype=float),
            where=summary['total_spend_on_all_own'] != 0
        )
        
        # 8. Reorder and format columns
        summary = summary[['solID', 'rsq_train_avg', 'decomp_rssd_avg',
                           'own_zero_count', 'total_spend_on_own_zeros', 'total_spend_on_all_own',
                           'pct_spend_on_own_zeros', 'own_zero_vars']]

        # Format total spend values
        summary['total_spend_on_own_zeros'] = summary['total_spend_on_own_zeros'].apply(
            lambda x: f"${x:,.2f}"
        )
        summary['total_spend_on_all_own'] = summary['total_spend_on_all_own'].apply(
            lambda x: f"${x:,.2f}"
        )

        # Format percentage column
        summary['pct_spend_on_own_zeros'] = summary['pct_spend_on_own_zeros'].apply(
            lambda x: f"{x:.2f}%"
        )

        # Sort by the number of zero-coefficient 'own' variables (ascending order)
        summary = summary.sort_values(by='own_zero_count', ascending=True)

    # --- Display Results ---
    st.subheader("Submodels with All Non-Zero Coefficients (Simplified)")
    if non_zero_summary.empty:
        st.info("No submodels found where all relevant variables have non-zero coefficients.")
    else:
        st.dataframe(non_zero_summary, use_container_width=True)

    st.subheader("Summary of Submodels with 'Own' Zero-Coefficient Variables")
    st.markdown("""
        The table below shows models where **'own' variables** have been selected 
        but given a **zero coefficient** (i.e., they are ineffective). 
        The **Pct Spend** column shows the proportion of total spend on *all* 'own' variables 
        that was allocated to these ineffective ones.
    """)
    if summary.empty:
        st.info("No submodels with 'own' zero-coefficient variables found.")
    else:
        # Rename columns for display clarity
        display_summary = summary.rename(columns={
            'rsq_train_avg': 'R-sq Avg',
            'decomp_rssd_avg': 'RSSD Avg',
            'own_zero_count': 'Own Zeros Count',
            'total_spend_on_own_zeros': 'Spend on Own Zeros',
            'total_spend_on_all_own': 'Total Spend on All Own',
            'pct_spend_on_own_zeros': 'Pct Spend on Own Zeros',
            'own_zero_vars': 'Own Zero Variables'
        })
        st.dataframe(display_summary, use_container_width=True)

# Streamlit App UI entry point
def main():
    st.set_page_config(layout="wide")
    st.title("Pareto Aggregation Model Spend Analysis")
    
    # File uploader widget (supports CSV and Excel)
    uploaded_file = st.file_uploader("Upload pareto_aggregated Excel or CSV file", type=["xlsx", "csv"])

    # Analyze the uploaded file if it is provided
    if uploaded_file:
        # Check file type and convert to Excel in memory if CSV
        if uploaded_file.name.endswith(".csv"):
            with st.spinner('Converting CSV to Excel format...'):
                uploaded_file = convert_csv_to_excel(uploaded_file)
        
        if uploaded_file: # Proceed only if conversion was successful
            with st.spinner('Analyzing file and calculating spend percentages...'):
                analyze_file(uploaded_file)
            
if __name__ == '__main__':
    main()
