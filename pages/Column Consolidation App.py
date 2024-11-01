import streamlit as st
import pandas as pd
import re
from io import BytesIO

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

    # Consolidate column names by removing trailing numbers (e.g., "_1", "_2", etc.)
    consolidated_columns = []
    seen_columns = set()
    ordered_unique_columns = []

    for col in filtered_columns:
        # Remove trailing numbers and apply transformation to remove "spend" or similar words
        new_col = re.sub(r'(_\d+)', '', col)
        new_col = re.sub(r'(_Spend|_Impressions)', '', new_col, flags=re.IGNORECASE)  # Remove specified words
        consolidated_columns.append(new_col)

        # Preserve order of first occurrences only
        if new_col not in seen_columns:
            ordered_unique_columns.append(new_col)
            seen_columns.add(new_col)

    # Create a DataFrame to show old and new column names for filtered columns only
    consolidated_df = pd.DataFrame({
        'Original Column Name': filtered_columns,
        'Consolidated Column Name': consolidated_columns
    })

    # Convert ordered unique columns to DataFrame for download
    unique_columns_df = pd.DataFrame({'Consolidated Column Names': ordered_unique_columns})
    return consolidated_df, unique_columns_df

def download_excel(df):
    # Save DataFrame to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Consolidated Columns')
        writer.close()  # Use close() instead of save()
    output.seek(0)
    return output

def main():
    st.title("Column Consolidation App")
    st.write("Upload an Excel file to consolidate similar column names.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)

        # Filter options for selecting columns
        filter_option = st.selectbox("Select Variable Type to Consolidate", 
                                     options=["All Variables", "Spend Variables", "Impression Variables"])

        # Process the DataFrame based on selected filter
        consolidated_df, unique_columns_df = consolidate_columns(df, filter_option)

        # Display the consolidated column mapping as a table
        st.subheader("Column Consolidation Mapping")
        st.write(consolidated_df)

        # Display the unique consolidated column names in original order for easy copying
        st.subheader("Ordered Consolidated Column Names")
        st.write(unique_columns_df)

        # Provide a download button for Excel
        excel_data = download_excel(unique_columns_df)
        st.download_button(
            label="Download Ordered Consolidated Column Names as Excel",
            data=excel_data,
            file_name="ordered_consolidated_column_names.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# Run the main function
if __name__ == "__main__":
    main()
