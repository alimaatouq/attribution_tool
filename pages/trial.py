import streamlit as st
import pandas as pd
import re
from io import BytesIO

def consolidate_columns(df, filter_option):
    columns = df.columns
    filtered_columns = []

    for col in columns:
        # Only include columns with "spend" in their names if filter option is "Spend Variables"
        if filter_option == "Spend Variables" and "spend" not in col.lower():
            continue
        filtered_columns.append(col)

    # Consolidate by removing trailing numbers with underscores or hyphens (e.g., "_1", "-2", etc.)
    consolidated_columns = []
    seen_columns = set()
    ordered_unique_columns = []

    for col in filtered_columns:
        new_col = re.sub(r'([_-]\d+)', '', col)
        consolidated_columns.append(new_col)

        # Preserve order of unique consolidated column names
        if new_col not in seen_columns:
            ordered_unique_columns.append(new_col)
            seen_columns.add(new_col)

    # DataFrame to show original and consolidated column names
    consolidated_df = pd.DataFrame({
        'Original Column Name': filtered_columns,
        'Consolidated Column Name': consolidated_columns
    })

    unique_columns_df = pd.DataFrame({'Consolidated Column Names': ordered_unique_columns})
    return consolidated_df, unique_columns_df

def aggregate_spend(df, consolidated_df):
    spend_data = []

    # Aggregate spend by each unique consolidated column name (each channel)
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        # Extract channel name
        channel = consolidated_name.split('_')[0]  # Assuming channel is first part of name
        
        # Sum up all columns that match the consolidated column pattern
        matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
        spend_sum = df[matching_columns].sum(axis=1).sum()  # Sum across rows and then total
        
        # Append to spend_data list
        spend_data.append({'Channel': channel, 'Spend': spend_sum})

    spend_df = pd.DataFrame(spend_data)
    return spend_df

def summarize_channel_spend(spend_df):
    channel_summary = spend_df.groupby('Channel')['Spend'].sum().reset_index()
    total_spend = channel_summary['Spend'].sum()
    channel_summary['Percentage Contribution'] = ((channel_summary['Spend'] / total_spend) * 100).round(0).astype(int)

    total_row = pd.DataFrame([{
        'Channel': 'Total',
        'Spend': total_spend,
        'Percentage Contribution': 100
    }])
    channel_summary = pd.concat([channel_summary, total_row], ignore_index=True)

    return channel_summary

def create_final_output_table(spend_df, channel_summary_df):
    final_df = spend_df.copy()
    final_df['Channel - Contribution'] = final_df['Channel']
    
    # Add percentage contribution to each channel row
    for _, row in channel_summary_df.iterrows():
        channel = row['Channel']
        if channel != 'Total':
            contribution_percentage = int(row['Percentage Contribution'])
            final_df.loc[final_df['Channel'] == channel, 'Channel - Contribution'] = f"{channel} - {contribution_percentage}%"

    final_df['Spend'] = final_df['Spend'].apply(lambda x: f"${x:,.0f}")
    final_df = final_df[['Channel - Contribution', 'Spend']]
    
    return final_df

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def main():
    st.title("Spend Aggregation App")
    st.write("Upload an Excel file to consolidate and aggregate spend by channel.")

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        filter_option = st.selectbox("Select Variable Type to Consolidate", ["Spend Variables"])

        consolidated_df, unique_columns_df = consolidate_columns(df, filter_option)
        st.subheader("Column Consolidation Mapping")
        st.write(consolidated_df)

        if filter_option == "Spend Variables":
            spend_df = aggregate_spend(df, consolidated_df)
            st.subheader("Aggregated Spend Data by Channel")
            st.write(spend_df)

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
