import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Helper function to consolidate and analyze based on 'rn' column for Spend variables only
def consolidate_by_rn_spend(df):
    # Filter rows where 'rn' column contains "Spend"
    df = df[df['rn'].str.contains("Spend", case=False)]

    # Remove trailing numbers from 'rn' values (e.g., Snap_InteriorOnly_2_Spend to Snap_InteriorOnly_Spend)
    df['rn'] = df['rn'].apply(lambda x: re.sub(r'(_\d+)(?=_Spend)', '', x))

    # Group by consolidated 'rn' and sum 'spend_share' and 'effect_share'
    consolidated_df = df.groupby('rn').agg({
        'spend_share': 'sum',
        'effect_share': 'sum'
    }).reset_index()

    # Calculate 'difference' column
    consolidated_df['difference'] = consolidated_df['effect_share'] - consolidated_df['spend_share']

    # Reorder columns: 'rn', 'effect_share', 'spend_share', 'difference'
    consolidated_df = consolidated_df[['rn', 'effect_share', 'spend_share', 'difference']]

    # Sort by 'effect_share' in descending order, with the highest at the bottom
    consolidated_df = consolidated_df.sort_values(by='effect_share', ascending=True).reset_index(drop=True)

    return consolidated_df

# Function to create a downloadable Excel file
def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        writer.close()
    output.seek(0)
    return output

# New page for consolidating based on 'rn' and analyzing
def consolidate_and_analyze_page():
    st.title("Consolidate and Analyze Spend Variables by Model")

    # File uploader for CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Load CSV file
        df = pd.read_csv(uploaded_file)

        # Ensure required columns are present
        if 'solID' not in df.columns or 'rn' not in df.columns or 'spend_share' not in df.columns or 'effect_share' not in df.columns:
            st.error("The uploaded file must contain 'solID', 'rn', 'spend_share', and 'effect_share' columns.")
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

# Main function to add navigation between pages
def main():
    st.sidebar.title("Navigation")
    pages = {
        "Consolidate and Analyze Spend Variables by Model": consolidate_and_analyze_page
    }
    
    page_selection = st.sidebar.radio("Go to", list(pages.keys()))
    pages[page_selection]()

if __name__ == "__main__":
    main()
