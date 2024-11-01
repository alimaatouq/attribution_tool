import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Helper function to consolidate columns
def consolidate_columns(df, filter_option):
    # Get initial column names and filter based on selected option
    columns = df.columns
    filtered_columns = []

    for col in columns:
        # Check the filter option and match keywords accordingly
        if filter_option == "Spend Variables" and "spend" not in col.lower():
            continue
        elif filter_option == "Impression Variables" and "impressions" not in col.lower():
            continue
        filtered_columns.append(col)

    # Consolidate column names by removing trailing numbers with underscores or hyphens
    consolidated_columns = []
    seen_columns = set()
    ordered_unique_columns = []

    for col in filtered_columns:
        new_col = re.sub(r'([_-]\d+)', '', col)
        consolidated_columns.append(new_col)

        if new_col not in seen_columns:
            ordered_unique_columns.append(new_col)
            seen_columns.add(new_col)

    consolidated_df = pd.DataFrame({
        'Original Column Name': filtered_columns,
        'Consolidated Column Name': consolidated_columns
    })

    unique_columns_df = pd.DataFrame({'Consolidated Column Names': ordered_unique_columns})
    return consolidated_df, unique_columns_df

# Additional functions remain unchanged
# Aggregate, summarize, create final output functions...

# Function to filter and analyze based on `solID`
def analyze_model(df):
    st.title("Analyze Model Selection")

    # Select solID to filter models
    unique_sol_ids = df['solID'].unique() if 'solID' in df.columns else []
    selected_model = st.selectbox("Select Model (solID) to Analyze", options=unique_sol_ids)

    # Filter the DataFrame based on the selected solID model
    filtered_df = df[df['solID'] == selected_model]

    st.subheader(f"Filtered Data for Model: {selected_model}")
    st.write(filtered_df)

    # Choose variable type to consolidate
    filter_option = st.selectbox("Select Variable Type to Consolidate",
                                 options=["All Variables", "Spend Variables", "Impression Variables"])
    consolidated_df, unique_columns_df = consolidate_columns(filtered_df, filter_option)
    
    st.subheader("Column Consolidation Mapping")
    st.write(consolidated_df)

    # Display unique consolidated column names
    st.subheader("Ordered Consolidated Column Names")
    st.write(unique_columns_df)

    if filter_option == "Spend Variables":
        spend_df = aggregate_spend(filtered_df, consolidated_df)
        channel_summary_df = summarize_channel_spend(spend_df)
        final_output_df = create_final_output_table(spend_df, channel_summary_df)

        st.subheader("Final Output Table")
        st.write(final_output_df)

        # Download option for final output
        excel_data_final_output = download_excel(final_output_df, sheet_name='Final Output')
        st.download_button(
            label="Download Final Output Table as Excel",
            data=excel_data_final_output,
            file_name="final_output_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# Main function to add navigation between pages
def main():
    st.sidebar.title("Navigation")
    pages = {
        "Column Consolidation": consolidate_page,
        "Analyze Model Selection": analyze_model
    }
    
    page_selection = st.sidebar.radio("Go to", list(pages.keys()))
    pages[page_selection]()

# Page function for consolidation
def consolidate_page():
    st.title("Column Consolidation App")
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        filter_option = st.selectbox("Select Variable Type to Consolidate", 
                                     options=["All Variables", "Spend Variables", "Impression Variables"])

        consolidated_df, unique_columns_df = consolidate_columns(df, filter_option)
        st.subheader("Column Consolidation Mapping")
        st.write(consolidated_df)

        st.subheader("Ordered Consolidated Column Names")
        st.write(unique_columns_df)

        if filter_option == "Spend Variables":
            spend_df = aggregate_spend(df, consolidated_df)
            channel_summary_df = summarize_channel_spend(spend_df)
            final_output_df = create_final_output_table(spend_df, channel_summary_df)

            st.subheader("Final Output Table")
            st.write(final_output_df)

            excel_data_final_output = download_excel(final_output_df, sheet_name='Final Output')
            st.download_button(
                label="Download Final Output Table as Excel",
                data=excel_data_final_output,
                file_name="final_output_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

if __name__ == "__main__":
    main()
