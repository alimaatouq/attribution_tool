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

def aggregate_spend(df, consolidated_df):
    spend_data = []

    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        match = re.match(r'([A-Za-z]+)_([A-Za-z]+)', consolidated_name)
        if match:
            channel = match.group(1)
            creative = match.group(2)
            
            matching_spend_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            spend_sum = df[matching_spend_columns].sum(axis=1).sum()

            spend_data.append({
                'Channel': channel,
                'Creative': creative,
                'Spend': spend_sum
            })

    spend_df = pd.DataFrame(spend_data)
    return spend_df

def summarize_channel_spend(spend_df, total_sessions):
    # Calculate total spend by channel
    channel_summary = spend_df.groupby('Channel')['Spend'].sum().reset_index()

    # Set Website Visits to the same total_sessions value for each channel
    channel_summary['Website Visits'] = total_sessions
    channel_summary['Cost per Visit'] = channel_summary['Spend'] / channel_summary['Website Visits']

    # Calculate total spend and cost per visit for the Total row
    total_spend = channel_summary['Spend'].sum()
    total_cost_per_visit = total_spend / total_sessions

    # Add a row for the total
    total_row = pd.DataFrame([{
        'Channel': 'Total',
        'Spend': total_spend,
        'Website Visits': total_sessions,
        'Cost per Visit': total_cost_per_visit,
    }])
    channel_summary = pd.concat([channel_summary, total_row], ignore_index=True)

    return channel_summary


def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        writer.close()
    output.seek(0)
    return output

def main():
    st.title("Aggregated Spend Data by Channel with Cost per Visit")
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        filter_option = st.selectbox("Select Variable Type to Consolidate", 
                                     options=["All Variables", "Spend Variables", "Impression Variables"])

        consolidated_df, unique_columns_df = consolidate_columns(df, filter_option)

        st.subheader("Column Consolidation Mapping")
        st.write(consolidated_df)

        if filter_option == "Spend Variables":
            spend_df = aggregate_spend(df, consolidated_df)

            # Calculate total website visits from KPI_Website_Sessions column
            total_sessions = df['KPI_Website_Sessions'].sum()
            st.write(f"Total Website Visits: {total_sessions}")

            channel_summary_df = summarize_channel_spend(spend_df, total_sessions)
            st.subheader("Channel Summary with Cost per Visit and Percentage Contribution")
            st.write(channel_summary_df)

            excel_data_final_output = download_excel(channel_summary_df, sheet_name='Final Output')
            st.download_button(
                label="Download Final Output Table as Excel",
                data=excel_data_final_output,
                file_name="final_output_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

if __name__ == "__main__":
    main()
