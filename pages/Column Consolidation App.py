import streamlit as st
import pandas as pd
import re

def consolidate_columns(df):
    # Get initial column names
    columns = df.columns
    # Consolidate column names by removing trailing numbers (e.g., "_1", "_2", etc.)
    consolidated_columns = []
    for col in columns:
        new_col = re.sub(r'(_\d+)', '', col)
        consolidated_columns.append(new_col)

    # Create a DataFrame to show old and new column names
    consolidated_df = pd.DataFrame({
        'Original Column Name': columns,
        'Consolidated Column Name': consolidated_columns
    })

    # Deduplicate columns for download
    unique_columns_df = pd.DataFrame({'Consolidated Column Names': list(set(consolidated_columns))})
    return consolidated_df, unique_columns_df

def main():
    st.title("Column Consolidation App")
    st.write("Upload an Excel file to consolidate similar column names.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)

        # Process the DataFrame
        consolidated_df, unique_columns_df = consolidate_columns(df)

        # Display the consolidated column mapping as a table
        st.subheader("Column Consolidation Mapping")
        st.write(consolidated_df)

        # Display the unique consolidated column names for easy copying
        st.subheader("Consolidated Column Names")
        st.write(unique_columns_df)

        # Provide a download button for Excel
        csv = unique_columns_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Consolidated Column Names as CSV",
            data=csv,
            file_name="consolidated_column_names.csv",
            mime="text/csv",
        )

# Run the main function
if __name__ == "__main__":
    main()
