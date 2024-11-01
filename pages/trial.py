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

def aggregate_spend_and_visits(df, consolidated_df):
    spend_data = []

    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        match = re.match(r'([A-Za-z]+)_([A-Za-z]+)', consolidated_name)
        if match:
            channel = match.group(1)
            creative = match.group(2)
            
            matching_spend_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            spend_sum = df[matching_spend_columns].sum(axis=1).sum()

            # Assuming visits data is available in the format 'Channel_Visits' for each channel
            visit_column = f"{channel}_Visits"
            visits = df[visit_column].sum() if visit_column in df.columns else 0

            spend_data.append({
                'Channel': channel,
                'Creative': creative,
                'Spend': spend_sum,
                'Website Visits': visits
            })

    spend_df = pd.DataFrame(spend_data)
    spend_df['Cost per Visit'] = spend_df['Spend'] / spend_df['Website Visits']
    return spend_df

def summarize_channel_spend(spend_df):
    # Calculate total spend and visits by channel
    channel_summary = spend_df.groupby('Channel')[['Spend', 'Website Visits']].sum().reset_index()

    # Calculate Cost per Visit for each channel
    channel_summary['Cost per Visit'] = channel_summary['Spend'] / channel_summary['Website Visits']

    # Calculate totals for Spend and Visits and a weighted Cost per Visit for the Total row
    total_spend = channel_summary['Spend'].sum()
    total_visits = channel_summary['Website Visits'].sum()
    total_cost_per_visit = total_spend / total_visits

    # Add a row for the total
    total_row = pd.DataFrame([{
        'Channel': 'Total',
        'Spend': total_spend,
        'Website Visits': total_visits,
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
            spend_df = aggregate_spend_and_visits(df, consolidated_df)

            channel_summary_df = summarize_channel_spend(spend_df)
            st.subheader("Channel Summary with Cost per Visit")
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
