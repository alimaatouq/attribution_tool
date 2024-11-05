import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Helper function to consolidate columns
def consolidate_columns(df):
    # Filter columns that contain "spend"
    filtered_columns = [col for col in df.columns if "spend" in col.lower()]

    # Consolidate column names by removing trailing numbers
    consolidated_columns = []
    seen_columns = set()
    ordered_unique_columns = []

    for col in filtered_columns:
        new_col = re.sub(r'([_-]\d+)', '', col)
        consolidated_columns.append(new_col)

        if new_col not in seen_columns:
            ordered_unique_columns.append(new_col)
            seen_columns.add(new_col)

    # Create a DataFrame to map original to consolidated names
    consolidated_df = pd.DataFrame({
        'Original Column Name': filtered_columns,
        'Consolidated Column Name': consolidated_columns
    })

    unique_columns_df = pd.DataFrame({'Consolidated Column Names': ordered_unique_columns})
    return consolidated_df, unique_columns_df

# Function to aggregate spend data
def aggregate_spend(df, consolidated_df):
    spend_data = []
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        match = re.match(r'([A-Za-z]+)_([A-Za-z]+)', consolidated_name)
        if match:
            channel = match.group(1)
            creative = match.group(2)
            matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            spend_sum = df[matching_columns].sum(axis=1).sum()
            spend_data.append({'Channel': channel, 'Creative': creative, 'Spend': spend_sum})

    spend_df = pd.DataFrame(spend_data)
    return spend_df

# Function to summarize channel spend
def summarize_channel_spend(spend_df):
    channel_summary = spend_df.groupby('Channel')['Spend'].sum().reset_index()
    total_spend = channel_summary['Spend'].sum()
    channel_summary['Percentage Contribution'] = ((channel_summary['Spend'] / total_spend) * 100).round(0).astype(int)
    total_row = pd.DataFrame([{'Channel': 'Total', 'Spend': total_spend, 'Percentage Contribution': 100}])
    channel_summary = pd.concat([channel_summary, total_row], ignore_index=True)
    return channel_summary

# Function to create the final output table
def create_final_output_table(spend_df, channel_summary_df):
    final_df = spend_df.copy()
    final_df['Channel - Contribution'] = final_df['Channel']
    for _, row in channel_summary_df.iterrows():
        channel = row['Channel']
        if channel != 'Total':
            contribution_percentage = int(row['Percentage Contribution'])
            final_df.loc[final_df['Channel'] == channel, 'Channel - Contribution'] = f"{channel} - {contribution_percentage}%"
    final_df['Spend'] = final_df['Spend'].apply(lambda x: f"${x:,.0f}")
    final_df = final_df[['Channel - Contribution', 'Creative', 'Spend']]
    return final_df

# Function to create a downloadable Excel file
def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

# Main function for single-page app
def main():
    st.title("Channel Spend Consolidation App")
    st.write("Upload a CSV or Excel file to consolidate and analyze spend data.")

    # File uploader for both CSV and Excel files
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)

        # Consolidate columns with spend data only
        consolidated_df, unique_columns_df = consolidate_columns(df)

        # Aggregate and summarize spend data
        spend_df = aggregate_spend(df, consolidated_df)
        channel_summary_df = summarize_channel_spend(spend_df)
        final_output_df = create_final_output_table(spend_df, channel_summary_df)

        # Display the final output table
        st.subheader("Final Output Table")
        st.write(final_output_df)

        # Download option for the final output
        excel_data_final_output = download_excel(final_output_df, sheet_name='Final Output')
        st.download_button(
            label="Download Final Output Table as Excel",
            data=excel_data_final_output,
            file_name="final_output_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
