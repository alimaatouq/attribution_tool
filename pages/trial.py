import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Helper function to consolidate and analyze based on 'rn' column for Spend variables only
def consolidate_by_rn_spend(df):
    # Filter rows where 'rn' column contains "Spend"
    df = df[df['rn'].str.contains("Spend", case=False)]

    # Standardize 'rn' values by removing numeric identifiers and '_Spend'
    df['rn'] = df['rn'].apply(lambda x: re.sub(r'(_\d+|_Spend)', '', x, flags=re.IGNORECASE).replace('_', ' '))

    # Group by consolidated 'rn' and sum 'spend_share' and 'effect_share'
    consolidated_df = df.groupby('rn', as_index=False).agg({
        'spend_share': 'sum',
        'effect_share': 'sum'
    })

    # Calculate 'difference' column
    consolidated_df['difference'] = consolidated_df['effect_share'] - consolidated_df['spend_share']

    # Sort by 'effect_share' in descending order
    consolidated_df = consolidated_df.sort_values(by='effect_share', ascending=True).reset_index(drop=True)

    return consolidated_df

# Function to create a downloadable Excel file
def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

# Main function for the app
def main():
    st.title("Effect and Spend Share Data Prep & Difference Calculator")

    # File uploader for CSV file
    uploaded_file = st.file_uploader("Upload the pareto_aggregated CSV file", type="csv")
    
    if uploaded_file is not None:
        # Load CSV file
        df = pd.read_csv(uploaded_file)

        # Ensure required columns are present
        required_columns = {'solID', 'rn', 'spend_share', 'effect_share'}
        if not required_columns.issubset(df.columns):
            st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
            return

        # Select solID to filter models
        unique_sol_ids = df['solID'].unique()
        selected_model = st.selectbox("Select Model (solID) to Analyze", options=unique_sol_ids)
        
        # Filter DataFrame based on the selected solID model
        filtered_df = df[df['solID'] == selected_model]

        # Consolidate by 'rn' for Spend variables and calculate required fields
        consolidated_df = consolidate_by_rn_spend(filtered_df)

        # Display consolidated DataFrame
        st.subheader("Consolidated Data")
        st.write(consolidated_df)

        # Download option for consolidated data
        excel_data = download_excel(consolidated_df, sheet_name='Consolidated Data')
        st.download_button(
            label="Download Consolidated Data as Excel",
            data=excel_data,
            file_name="consolidated_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# Run the main function
if __name__ == "__main__":
    main()
