import streamlit as st
import pandas as pd
import numpy as np
import re
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

# --- New functions for Max Channel CPA Calculation ---

def standardize_channel_name(name):
    """
    Transforms names like 'Media_Digital_..._1_Impressions' to 'Media Digital ... Impressions'.
    It removes trailing '_N' and replaces remaining underscores with spaces.
    """
    if pd.isna(name):
        return name
    
    # 1. Remove '_N' at the end of the name (e.g., _1, _2, _3)
    # The regex r'_\d+($|_)' looks for an underscore followed by one or more digits, 
    # either at the end ($) or followed by another underscore (_).
    name_no_adstock = re.sub(r'_\d+($|_)', '', name)
    
    # 2. Replace remaining underscores with spaces, then strip any extra whitespace
    name_standardized = name_no_adstock.replace('_', ' ').strip()
    
    return name_standardized

def calculate_max_channel_cpa(df):
    """
    Calculates the max channel CPA for each model (solID).
    """
    # Filter out non-channel variables (like intercept, trend, season)
    ignore_vars = ['(Intercept)', 'trend', 'season', 'weekday', 'monthly', 'holiday']
    df_channels = df[~df['rn'].isin(ignore_vars)].copy()
    
    # Apply the standardization function
    df_channels['Channel_Name_Std'] = df_channels['rn'].apply(standardize_channel_name)
    
    # Aggregate by model (solID) and standardized channel name
    channel_agg = df_channels.groupby(['solID', 'Channel_Name_Std']).agg(
        total_spend=('total_spend', 'sum'),
        total_effect=('xDecompAgg', 'sum'),
    ).reset_index()

    # Calculate Channel CPA: Spend / Effect. Handle division by zero/near zero.
    channel_agg['Channel_CPA'] = np.divide(
        channel_agg['total_spend'],
        channel_agg['total_effect'],
        out=np.full_like(channel_agg['total_spend'], np.nan),
        where=channel_agg['total_effect'] > 1e-6 # Ensure effect is not negligible
    )
    
    # Find the maximum CPA across all channels for each model
    max_cpa_summary = channel_agg.groupby('solID').agg(
        Max_Channel_CPA=('Channel_CPA', 'max'),
    ).reset_index()
    
    # Merge model-level metrics for R-squared as a tie-breaker
    # Use the intercept row or first row for metrics
    model_metrics = df[df['rn'] == '(Intercept)'][['solID', 'rsq_train', 'rsq_val', 'rsq_test', 'nrmse', 'decomp.rssd']].copy()
    if model_metrics.empty:
        metric_cols = ['rsq_train', 'rsq_val', 'rsq_test', 'nrmse', 'decomp.rssd']
        model_metrics = df.groupby('solID')[metric_cols].first().reset_index()
    
    # Merge and replace inf/-inf with NaN before ranking
    final_ranking_df = pd.merge(max_cpa_summary, model_metrics, on='solID', how='left')
    final_ranking_df = final_ranking_df.replace([np.inf, -np.inf], np.nan)
    
    return final_ranking_df

# *** Core Ranking and Display Function ***
def rank_and_display_models_by_max_cpa(df):
    """
    Calculates and displays models ranked by the Max Channel CPA.
    """
    st.subheader("Model Stability Ranking: Max Channel CPA")
    st.markdown("""
        This table ranks models based on the **lowest Maximum Channel CPA**. 
        This is a proxy for **channel stability** and consistency, avoiding models 
        where one or two channels have an extremely high, outlier CPA, even if the 
        overall model CPA (which depends on contribution) is low.
    """)
    
    ranking_df = calculate_max_channel_cpa(df.copy())
    
    # Drop rows where Max_Channel_CPA is NaN (i.e., model has only 0 effect channels)
    ranking_df = ranking_df.dropna(subset=['Max_Channel_CPA'])

    if ranking_df.empty:
        st.warning("No models with calculated Max Channel CPA were found.")
        return

    # 1. Rank the models: Sort by Max_Channel_CPA (smallest to largest) and then R-Squared (largest to smallest)
    ranking_df = ranking_df.sort_values(
        by=['Max_Channel_CPA', 'rsq_train'],
        ascending=[True, False]
    ).reset_index(drop=True)

    # 2. Add a Rank column
    ranking_df['Rank'] = ranking_df.index + 1

    # 3. Format columns for better display
    ranking_df['Max Channel CPA'] = ranking_df['Max_Channel_CPA'].apply(lambda x: f"${x:,.4f}" if x is not None else "N/A")
    ranking_df['R-Squared (Train)'] = ranking_df['rsq_train'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
    ranking_df['NRMSE'] = ranking_df['nrmse'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
    
    # 4. Select and rename final columns
    ranking_df_display = ranking_df[[
        'Rank', 'solID', 'Max Channel CPA', 'R-Squared (Train)', 'NRMSE', 'decomp.rssd'
    ]].rename(columns={
        'solID': 'Model ID',
        'decomp.rssd': 'Decomp RSSD'
    })
    
    st.dataframe(ranking_df_display, use_container_width=True, hide_index=True)


# --- Original analyze_file modified to call the new ranking function ---
def analyze_file(uploaded_file):
    """
    Analyzes the uploaded pareto_aggregated file.
    It performs Max Channel CPA ranking and the original zero-coefficient analysis.
    """
    # Load the Excel file into a DataFrame
    try:
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return

    # Ensure required columns exist for analysis
    required_cols = ['rn', 'solID', 'coef', 'total_spend', 'xDecompAgg', 'rsq_train', 'decomp.rssd']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing one or more required columns: {', '.join(required_cols)}. Cannot proceed with analysis.")
        return
        
    # --- 1. New Max Channel CPA Ranking and Display ---
    with st.container():
        rank_and_display_models_by_max_cpa(df.copy())
    
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
