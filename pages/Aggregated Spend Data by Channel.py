import streamlit as st
import pandas as pd
import re
from io import BytesIO

def consolidate_columns(df, filter_option):
    columns = df.columns
    filtered_columns = []

    for col in columns:
        if filter_option == "Spend Variables" and "spend" not in col.lower():
            continue
        elif filter_option == "Impression Variables" and "impressions" not in col.lower():
            continue
        filtered_columns.append(col)

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

def aggregate_spend_by_channel(df, consolidated_df):
    spend_data = []
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        match = re.match(r'([A-Za-z]+)', consolidated_name)
        if match:
            channel = match.group(1)
            matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            spend_sum = df[matching_columns].sum(axis=1).sum()
            spend_data.append({'Channel': channel, 'Spend': spend_sum})
    spend_df = pd.DataFrame(spend_data).groupby('Channel', as_index=False).sum()
    return spend_df

def create_final_output_table(spend_df):
    # Create a version with TOTAL row for display
    display_df = spend_df.copy()
    total_spend = display_df['Spend'].sum()
    display_df = pd.concat([display_df, pd.DataFrame([{'Channel': 'Total', 'Spend': total_spend}])], ignore_index=True)
    
    # Create a version without TOTAL row for download
    download_df = spend_df.copy()
    
    return display_df, download_df

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def main():
    st.title("Channel Spend Aggregation App")
    st.write("Upload an Excel file to consolidate similar column names.")

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
            spend_df = aggregate_spend_by_channel(df, consolidated_df)

            st.subheader("Aggregated Spend Data by Channel")
            st.write(spend_df)

            # Get the final output tables with and without TOTAL row
            final_display_df, final_download_df = create_final_output_table(spend_df)

            # Display the table with TOTAL row
            st.subheader("Final Output Table (with TOTAL row)")
            st.write(final_display_df)

            # Prepare the version without TOTAL row for download
            excel_data_final_output = download_excel(final_download_df, sheet_name='Final Output')
            st.download_button(
                label="Download Final Output Table as Excel",
                data=excel_data_final_output,
                file_name="final_output_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

if __name__ == "__main__":
    main()
