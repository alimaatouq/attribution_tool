import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from openpyxl import load_workbook

# Helper function to standardize file format to in-memory Excel BytesIO object
def convert_csv_to_excel(csv_file):
    """Convert CSV to Excel format (in-memory) to standardize file handling."""
    try:
        csv_file.seek(0)
        df = pd.read_csv(csv_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None
        
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl', sheet_name='Sheet1')
    excel_file.seek(0)
    return excel_file

# *** New function for CPA ranking and model metric comparison ***
def rank_and_display_models(df):
    """
    Extracts model-level metrics, ranks them by CPA, and displays the summary.
    """
    
    # 1. Try to extract model-level metrics from the (Intercept) row (Robyn's standard)
    model_metrics = df[df['rn'] == '(Intercept)'][['solID', 'cpa_total', 'rsq_train', 'rsq_val', 'rsq_test', 'nrmse', 'decomp.rssd']].copy()

    # 2. Alternative aggregation if (Intercept) fails or is missing cpa_total
    if model_metrics.empty or model_metrics['cpa_total'].isnull().all():
        metric_cols = ['cpa_total', 'rsq_train', 'rsq_val', 'rsq_test', 'nrmse', 'decomp.rssd']
        
        # Group by solID and take the first non-NA value for the metric columns
        model_metrics_alt = df.groupby('solID')[metric_cols].first().reset_index()
        
        # Replace inf/-inf with NaN for reliable dropna
        model_metrics_alt = model_metrics_alt.replace([np.inf, -np.inf], np.nan)
        
        # Filter out rows where cpa_total is NA
        model_metrics_alt = model_metrics_alt.dropna(subset=['cpa_total'])
        
        model_metrics = model_metrics_alt

    if model_metrics.empty:
        st.warning("No models with a valid 'cpa_total' were found for ranking.")
        return

    # 3. Rank the models: Sort by 'cpa_total' (smallest to largest) and then 'rsq_train' (largest to smallest)
    model_metrics = model_metrics.sort_values(
        by=['cpa_total', 'rsq_train'],
        ascending=[True, False]
    ).reset_index(drop=True)

    # 4. Add a Rank column
    model_metrics['Rank'] = model_metrics.index + 1

    # 5. Select and reorder final columns
    final_cols = ['Rank', 'solID', 'cpa_total', 'rsq_train', 'rsq_val', 'rsq_test', 'nrmse', 'decomp.rssd']
    model_metrics = model_metrics[final_cols]

    # 6. Format columns for better display
    model_metrics['CPA Total'] = model_metrics['cpa_total'].apply(lambda x: f"${x:,.4f}")
    model_metrics['R-Squared (Train)'] = model_metrics['rsq_train'].apply(lambda x: f"{x*100:.2f}%")
    model_metrics['R-Squared (Validation)'] = model_metrics['rsq_val'].apply(lambda x: f"{x*100:.2f}%")
    model_metrics['R-Squared (Test)'] = model_metrics['rsq_test'].apply(lambda x: f"{x*100:.2f}%")
    model_metrics['NRMSE'] = model_metrics['nrmse'].apply(lambda x: f"{x*100:.2f}%")
    
    # Rename for display
    model_metrics = model_metrics.rename(columns={
        'decomp.rssd': 'Decomp RSSD',
        'solID': 'Model ID'
    })

    # Drop the unformatted CPA and R-squared/NRMSE values
    model_metrics_display = model_metrics.drop(columns=['cpa_total', 'rsq_train', 'rsq_val', 'rsq_test', 'nrmse']).copy()
    
    st.subheader("Model CPA Ranking and Metrics")
    st.markdown("""
        This table ranks all models by **CPA Total** (Cost Per Acquisition, smallest to largest).
        The best models will have a **low CPA** and generally **high R-Squared** (closer to $100\%$) 
        and **low NRMSE / Decomp RSSD** (closer to $0.00$).
    """)

    st.dataframe(model_metrics_display, use_container_width=True, hide_index=True)


# --- Original analyze_file modified to call the new ranking function ---
def analyze_file(uploaded_file):
    """
    Analyzes the uploaded pareto_aggregated file.
    It performs CPA ranking and the original zero-coefficient analysis.
    """
    # Load the Excel file into a DataFrame
    try:
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return

    # Ensure required columns exist for full analysis
    required_cols = ['rn', 'solID', 'coef', 'total_spend', 'cpa_total', 'rsq_train', 'decomp.rssd']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing one or more required columns for full analysis: {', '.join(required_cols)}. CPA ranking might be incomplete.")
        if not ('solID' in df.columns and 'cpa_total' in df.columns):
            return
        
    # --- 1. New CPA Ranking and Display ---
    with st.container():
        rank_and_display_models(df.copy())
    
    st.markdown("---")
    
    # --- 2. Original Zero-Coefficient Analysis ---
    
    st.subheader("Submodels with 'own\\_' Zero-Coefficient Variables")
    
    # List of variables to ignore when checking for coefficients
    ignore_vars = ['(Intercept)', 'trend', 'season', 'weekday', 'monthly', 'holiday']

    # Filter out the rows with the variables we want to ignore
    df_filtered = df[~df['rn'].isin(ignore_vars)].copy()

    # --- Part 1: All Non-Zero Submodels (Simplified - kept for completeness) ---
    all_non_zero_submodels = df_filtered.groupby('solID').filter(lambda x: (x['coef'] != 0).all())

    if not all_non_zero_submodels.empty:
        non_zero_summary = all_non_zero_submodels.groupby('solID').agg(
            rsq_train_avg=('rsq_train', 'mean'),
            decomp_rssd_avg=('decomp.rssd', 'mean')
        ).reset_index()

        non_zero_summary = non_zero_summary.sort_values(by='rsq_train_avg', ascending=False)
        
        # Display simplified non-zero summary in an expander
        with st.expander("Show Submodels with All Non-Zero Coefficients (Simplified)"):
            non_zero_summary = non_zero_summary.rename(columns={
                'rsq_train_avg': 'R-sq Avg',
                'decomp_rssd_avg': 'RSSD Avg',
                'solID': 'Model ID'
            })
            st.dataframe(non_zero_summary, use_container_width=True, hide_index=True)


    # --- Part 2: Submodels with 'Own_' Zero-Coefficient Variables ---
    
    OWN_PREFIX = 'own_'
    
    df_own_vars = df_filtered[df_filtered['rn'].str.contains(OWN_PREFIX, case=False, na=False)].copy()

    # 1. Calculate total spend on ALL 'own_' variables per submodel (Denominator)
    total_own_spend = df_own_vars.groupby('solID')['total_spend'].sum().reset_index()
    total_own_spend.rename(columns={'total_spend': 'total_spend_on_all_own'}, inplace=True)

    # 2. Identify all zero-coefficient variables (excluding ignored)
    submodels_with_zeros = df_filtered[df_filtered['coef'] == 0].copy()

    # 3. Filter the zero-coefficient variables to include ONLY those with 'own_' in their name (Numerator variables)
    submodels_with_own_zeros = submodels_with_zeros[
        submodels_with_zeros['rn'].str.contains(OWN_PREFIX, case=False, na=False)
    ].copy()

    # If no 'own_' zero variables are found, initialize an empty summary
    if submodels_with_own_zeros.empty:
        summary = pd.DataFrame()
    else:
        # 4. Summarize the 'own_' zero-coefficient variables for each submodel
        summary_own_zeros = submodels_with_own_zeros.groupby('solID').agg(
            own_zero_count=('rn', 'count'), 
            total_spend_on_own_zeros=('total_spend', 'sum'), 
            own_zero_vars=('rn', lambda x: list(x)), 
            rsq_train_avg=('rsq_train', 'mean'),
            decomp_rssd_avg=('decomp.rssd', 'mean')
        ).reset_index()

        # 5. Merge the total spend on all 'own_' variables into the summary
        summary = pd.merge(summary_own_zeros, total_own_spend, on='solID', how='left')
        
        summary['total_spend_on_all_own'] = summary['total_spend_on_all_own'].fillna(0)

        # 6. Calculate the percentage of spend on 'own_' zero-coef variables
        summary['pct_spend_on_own_zeros'] = np.divide(
            summary['total_spend_on_own_zeros'] * 100,
            summary['total_spend_on_all_own'],
            out=np.zeros_like(summary['total_spend_on_own_zeros'], dtype=float),
            where=summary['total_spend_on_all_own'] != 0
        )
        
        # 7. Reorder and format columns
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

        # Sort by the number of zero-coefficient 'own_' variables (ascending order)
        summary = summary.sort_values(by='own_zero_count', ascending=True)

    # --- Display Results for Original Analysis ---
    
    st.markdown("""
        The table below shows models where **'own\\_' prefixed variables** have been selected 
        but given a **zero coefficient** (i.e., they are ineffective). 
        The **Pct Spend** column shows the proportion of total spend on *all* 'own\\_' variables 
        that was allocated to these ineffective ones.
    """)
    if summary.empty:
        st.info("No submodels with 'own\\_' zero-coefficient variables found.")
    else:
        # Rename columns for display clarity
        display_summary = summary.rename(columns={
            'rsq_train_avg': 'R-sq Avg',
            'decomp_rssd_avg': 'RSSD Avg',
            'own_zero_count': 'Own Zeros Count',
            'total_spend_on_own_zeros': 'Spend on Own Zeros',
            'total_spend_on_all_own': 'Total Spend on All Own',
            'pct_spend_on_own_zeros': 'Pct Spend on Own Zeros',
            'own_zero_vars': 'Own Zero Variables',
            'solID': 'Model ID'
        })
        st.dataframe(display_summary, use_container_width=True, hide_index=True)


# Streamlit App UI entry point for a multi-page app
# This function is what Streamlit will execute when the page is accessed.
def main_page_func():
    st.set_page_config(layout="wide")
    st.title("Pareto Aggregation Model Analysis Dashboard")
    
    # File uploader widget (supports CSV and Excel)
    uploaded_file = st.file_uploader("Upload pareto_aggregated Excel or CSV file", type=["xlsx", "csv"])

    # Analyze the uploaded file if it is provided
    if uploaded_file:
        # Check file type and convert to Excel in memory if CSV
        file_to_analyze = uploaded_file
        if uploaded_file.name.endswith(".csv"):
            with st.spinner('Converting CSV to Excel format...'):
                file_to_analyze = convert_csv_to_excel(uploaded_file)
        
        if file_to_analyze: # Proceed only if conversion was successful
            with st.spinner('Analyzing file and calculating metrics...'):
                analyze_file(file_to_analyze)
            
if __name__ == '__main__':
    main_page_func()
