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

    # Consolidate column names by removing trailing numbers with underscores or hyphens (e.g., "_1", "-2", etc.)
    consolidated_columns = []
    seen_columns = set()
    ordered_unique_columns = []

    for col in filtered_columns:
        # Updated regex to match either underscore or hyphen before numbers
        new_col = re.sub(r'([_-]\d+)', '', col)
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

def aggregate_spend(df, consolidated_df):
    spend_data = []

    # Group consolidated spend columns by channel and creative
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        # Extract channel and creative from the consolidated column name
        match = re.match(r'([A-Za-z]+)_([A-Za-z]+)', consolidated_name)
        if match:
            channel = match.group(1)
            creative = match.group(2)
            
            # Sum up all original columns that match this consolidated name pattern
            matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            spend_sum = df[matching_columns].sum(axis=1).sum()  # Sum across rows and then total
            
            # Append to spend_data list
            spend_data.append({'Channel': channel, 'Creative': creative, 'Spend': spend_sum})

    # Convert spend data to DataFrame
    spend_df = pd.DataFrame(spend_data)
    return spend_df

def download_excel(df):
    # Save DataFrame to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Consolidated Spend')
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

        # If "Spend Variables" selected, aggregate spend columns
        if filter_option == "Spend Variables":
            spend_df = aggregate_spend(df, consolidated_df)

            # Display the aggregated spend data
            st.subheader("Aggregated Spend Data")
            st.write(spend_df)

            # Provide a download button for Excel
            excel_data = download_excel(spend_df)
            st.download_button(
                label="Download Aggregated Spend Data as Excel",
                data=excel_data,
                file_name="aggregated_spend_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# Run the main function
if __name__ == "__main__":
    main()
