import streamlit as st
import pandas as pd
import re
from io import BytesIO

def consolidate_columns(df):
    # Filter columns to include only "spend" variables
    filtered_columns = [col for col in df.columns if "spend" in col.lower()]

    # Consolidate column names by removing trailing numbers with underscores or hyphens
    consolidated_columns = []
    seen_columns = set()
    ordered_unique_columns = []

    for col in filtered_columns:
        new_col = re.sub(r'([_-]\d+)', '', col)
        consolidated_columns.append(new_col)

        # Preserve order of first occurrences only
        if new_col not in seen_columns:
            ordered_unique_columns.append(new_col)
            seen_columns.add(new_col)

    consolidated_df = pd.DataFrame({
        'Original Column Name': filtered_columns,
        'Consolidated Column Name': consolidated_columns
    })

    return consolidated_df

def aggregate_spend(df, consolidated_df):
    spend_data = []

    # Group consolidated spend columns by channel and creative
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        match = re.match(r'([A-Za-z]+)_([A-Za-z]+)', consolidated_name)
        if match:
            channel = match.group(1)
            creative = match.group(2)
            
            # Sum up all original columns that match this consolidated name pattern
            matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            spend_sum = df[matching_columns].sum(axis=1).sum()  # Sum across rows and then total
            
            # Append to spend_data list
            spend_data.append({'Channel': channel, 'Creative': creative, 'Spend': spend_sum})

    spend_df = pd.DataFrame(spend_data)
    return spend_df

def summarize_channel_spend(spend_df):
    # Calculate total spend by channel
    channel_summary = spend_df.groupby('Channel')['Spend'].sum().reset_index()
    total_spend = channel_summary['Spend'].sum()
    
    # Calculate percentage contribution for each channel, rounded to nearest whole number
    channel_summary['Percentage Contribution'] = ((channel_summary['Spend'] / total_spend) * 100).round(0).astype(int)

    # Add a row for the total spend
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
    
    for _, row in channel_summary_df.iterrows():
        channel = row['Channel']
        if channel != 'Total':
            contribution_percentage = int(row['Percentage Contribution'])
            final_df.loc[final_df['Channel'] == channel, 'Channel - Contribution'] = f"{channel} - {contribution_percentage}%"

    # Format the Spend column as numbers
    final_df['Spend'] = final_df['Spend'].apply(lambda x: f"{x:,.0f}")

    final_df = final_df[['Channel - Contribution', 'Creative', 'Spend']]
    return final_df

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def main():
    st.title("Spend Data Consolidation App")
    st.write("Upload the Processed Data Excel file to consolidate and analyze spend data by channel and creative.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)

        # Consolidate columns with spend data only
        consolidated_df = consolidate_columns(df)

        # Aggregate and summarize spend data
        spend_df = aggregate_spend(df, consolidated_df)
        channel_summary_df = summarize_channel_spend(spend_df)
        final_output_df = create_final_output_table(spend_df, channel_summary_df)

        # Display the final output table
        st.subheader("Final Output Table")
        st.write(final_output_df)

        # Provide download option for the final output table
        excel_data_final_output = download_excel(final_output_df, sheet_name='Final Output')
        st.download_button(
            label="Download Final Output Table as Excel",
            data=excel_data_final_output,
            file_name="final_output_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
