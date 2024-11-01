import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Helper function to consolidate columns
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
        writer.close()
    output.seek(0)
    return output

# Main function for single-page app
def main():
    st.title("Model Selection and Column Consolidation App")
    st.write("Upload a CSV or Excel file to consolidate column names and analyze selected model.")

    # File uploader for both CSV and Excel files
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)

        # Select solID to filter models if solID column exists
        if 'solID' in df.columns:
            unique_sol_ids = df['solID'].unique()
            selected_model = st.selectbox("Select Model (solID) to Analyze", options=unique_sol_ids)
            df = df[df['solID'] == selected_model]
            st.subheader(f"Filtered Data for Model: {selected_model}")
            st.write(df)
        else:
            st.warning("The uploaded file does not contain a 'solID' column.")

        # Select variable type for consolidation
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

