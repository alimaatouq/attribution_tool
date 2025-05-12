import streamlit as st
import pandas as pd
import re
from openpyxl import load_workbook
from io import BytesIO

def load_conversions(file_path, solID_value):
    """Load and process the conversions data filtered by solID."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: Conversion file not found at {file_path}")
        return None

    if 'solID' not in df.columns:
        st.error("Error: The 'solID' column is missing from the conversion file.")
        return None

    df = df[df['solID'] == solID_value]  # Filter by solID

    channel_data = {}
    for col in df.columns:
        if 'spend' not in col.lower() or col == 'KPI_Website_Conversions':
            continue
        match = re.match(r'([A-Za-z]+)', col)
        if match:
            channel = match.group(1)
            channel_data[channel] = channel_data.get(channel, 0) + pd.to_numeric(df[col], errors='coerce').sum()

    conversions_df = pd.DataFrame(list(channel_data.items()), columns=['Channel', 'Conversions'])
    return conversions_df


def load_spends(file_path):
    """Load and process the spends data."""
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        st.error(f"Error: Spends file not found at {file_path}")
        return None

    spend_columns = [col for col in df.columns if "spend" in col.lower()]
    consolidated_columns = [re.sub(r'([_-]\d+)', '', col) for col in spend_columns]
    channel_data = {}
    for original_col, consolidated_col in zip(spend_columns, consolidated_columns):
        match = re.match(r'([A-Za-z]+)', consolidated_col)
        if match:
            channel = match.group(1)
            channel_data[channel] = channel_data.get(channel, 0) + pd.to_numeric(df[original_col], errors='coerce').sum()
    spends_df = pd.DataFrame(list(channel_data.items()), columns=['Channel', 'Spend'])
    return spends_df

def load_preprocessed(file_path):
    """Load and process the preprocessed data."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: Preprocessed file not found at {file_path}")
        return None

    df['period_number'] = df['periods'].apply(lambda x: int(re.search(r'\d+', str(x)).group()) if pd.notnull(x) else None)
    channel_split = df['channels'].str.extract(r'([^_]+)_([^_]+)_(.+)')
    channel_split.columns = ['Channel', 'channel_type', 'channel_metric']
    df = pd.concat([df, channel_split], axis=1)
    groupby_fields = ['Channel']
    aggregation_dict = {
        'initSpendUnit': 'sum',
        'optmSpendUnit': 'sum',
        'initResponseTotal': 'min',
        'optmResponseTotal': 'min',
        'initResponseUnit': 'sum',
        'optmResponseUnit': 'sum',
        'period_number': 'mean'
    }
    grouped_df = df.groupby(groupby_fields).agg(aggregation_dict).reset_index()
    if 'initSpendUnit' in grouped_df.columns and 'period_number' in grouped_df.columns:
        grouped_df['Sum_initSpendUnit'] = (grouped_df['initSpendUnit'] * grouped_df['period_number']).round(1)
    if 'optmSpendUnit' in grouped_df.columns and 'period_number' in grouped_df.columns:
        grouped_df['Sum_optmSpendUnit'] = (grouped_df['optmSpendUnit'] * grouped_df['period_number']).round(1)
    if 'initResponseUnit' in grouped_df.columns and 'period_number' in grouped_df.columns:
        grouped_df['Sum_initResponseUnit'] = (grouped_df['initResponseUnit'] * grouped_df['period_number']).round(1)
    if 'optmResponseUnit' in grouped_df.columns and 'period_number' in grouped_df.columns:
        grouped_df['Sum_optmResponseUnit'] = (grouped_df['optmResponseUnit'] * grouped_df['period_number']).round(1)
    if 'Sum_optmSpendUnit' in grouped_df.columns and 'Sum_initSpendUnit' in grouped_df.columns:
        grouped_df['Change'] = round((grouped_df['Sum_optmSpendUnit'] - grouped_df['Sum_initSpendUnit']) / grouped_df['Sum_initSpendUnit'], 3)
    if 'Sum_optmResponseUnit' in grouped_df.columns and 'Sum_initResponseUnit' in grouped_df.columns:
        grouped_df['Response_Change'] = round(grouped_df['Sum_optmResponseUnit'] / grouped_df['Sum_initResponseUnit'], 3)
    columns_to_drop = ['initSpendUnit', 'optmSpendUnit', 'initResponseUnit', 'optmResponseUnit']
    grouped_df = grouped_df.drop(columns=[col for col in columns_to_drop if col in grouped_df.columns])
    return grouped_df

def merge_data(conversions_df, spends_df, preprocessed_df):
    """Merge the three DataFrames on the 'Channel' column."""
    merged_df = pd.merge(conversions_df, spends_df, on='Channel', how='outer')
    merged_df = pd.merge(merged_df, preprocessed_df, on='Channel', how='outer')
    return merged_df

def format_number(number, is_currency=False, is_percentage=False, decimals=0):
    """Format a number as currency, percentage, or with specified decimals."""
    if pd.isna(number):
        return "nan"
    if is_currency:
        return f"${number:,.{decimals}f}"
    elif is_percentage:
        return f"{number:.{decimals}%}"
    else:
        return f"{number:,.{decimals}f}"

def to_excel(df, budget_kpi, response_kpi, cpa_kpi):
    """Convert DataFrame and KPIs to Excel in memory with formatting."""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Data', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Data']

    # Define formatting
    currency_format = workbook.add_format({'num_format': '#,##0'})
    percentage_format = workbook.add_format({'num_format': '0.0%'})
    number_format = workbook.add_format({'num_format': '#,##0'})
    number_3decimal_format = workbook.add_format({'num_format': '0.000'})
    currency_negative_format = workbook.add_format({'num_format': '#,##0', 'color': 'red'})

    # Apply formatting to the DataFrame columns
    worksheet.set_column('B:C', None, currency_format)  # old_budget, new_budget
    worksheet.set_column('D:E', None, number_format)    # old_response, new_response
    worksheet.set_column('F:F', None, percentage_format) # budget change
    worksheet.set_column('G:G', None, number_3decimal_format) # resp change
    worksheet.set_column('H:H', None, currency_format) # abs budg change

    # Apply red color to negative absolute budget change
    for row_num, abs_change in enumerate(df['abs budg change'], start=1):
        if abs_change < 0:
            worksheet.write_number(row_num, 7, abs_change, currency_negative_format)

    # Write Overall KPIs
    last_row = len(df) + 2
    worksheet.write_string(last_row, 0, 'Overall KPIs:')
    worksheet.write_string(last_row + 1, 0, 'Budget Change:')
    worksheet.write_number(last_row + 1, 1, budget_kpi / 100, percentage_format)
    worksheet.write_string(last_row + 2, 0, 'Response Change:')
    worksheet.write_number(last_row + 2, 1, response_kpi / 100, percentage_format)
    worksheet.write_string(last_row + 3, 0, 'CPA Change:')
    if pd.isna(cpa_change) or pd.isinf(cpa_change):
        worksheet.write_string(last_row + 3, 1, 'nan') # Or some other placeholder
    else:
        worksheet.write_number(last_row + 3, 1, cpa_change / 100, percentage_format)

    writer.close()
    processed_data = output.getvalue()
    return processed_data
def display_dashboard(final_df, budget_change_kpi, response_change_kpi, cpa_change):
    """Display the dashboard in Streamlit."""
    st.subheader("Channel Performance Analysis")
    formatted_df = final_df.copy()
    formatted_df['old_budget'] = formatted_df['old_budget'].map('${:,.0f}'.format)
    formatted_df['new_budget'] = formatted_df['new_budget'].map('${:,.0f}'.format)
    formatted_df['old_response'] = formatted_df['old_response'].map('{:,.0f}'.format)
    formatted_df['new_response'] = formatted_df['new_response'].map('{:,.0f}'.format)
    formatted_df['budget change'] = formatted_df['budget change'].map('{:.1%}'.format)
    formatted_df['resp change'] = formatted_df['resp change'].map('{:.3f}'.format)
    formatted_df['abs budg change'] = formatted_df['abs budg change'].map('${:,.0f}'.format)

    st.dataframe(formatted_df, use_container_width=True)

    st.subheader("Overall KPIs:")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Budget Change:", format_number(budget_change_kpi / 100, is_percentage=True, decimals=1))
        st.metric("CPA Change:", format_number(cpa_change / 100, is_percentage=True, decimals=1))
    with col2:
        st.metric("Response Change:", format_number(response_change_kpi / 100, is_percentage=True, decimals=1))

    excel_file = to_excel(final_df, budget_change_kpi, response_change_kpi, cpa_change)

    st.download_button(
        label="Download as Excel",
        data=excel_file,
        file_name="marketing_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def main():
    st.title("Marketing Budget and Response Analysis")

    # File uploaders
    conversions_file = st.file_uploader("Upload Conversions CSV File", type=["csv"])
    spends_file = st.file_uploader("Upload Spends Excel File", type=["xlsx"])
    preprocessed_file = st.file_uploader("Upload Preprocessed CSV File", type=["csv"])

    sol_id_to_filter = st.text_input("Enter solID to filter:", "4_722_10")

    if conversions_file and spends_file and preprocessed_file and sol_id_to_filter:
        with st.spinner("Loading and processing data..."):
            # Load and process the data
            conversions_df = load_conversions(conversions_file, sol_id_to_filter)
            spends_df = load_spends(spends_file)
            preprocessed_df = load_preprocessed(preprocessed_file)

            if conversions_df is not None and spends_df is not None and preprocessed_df is not None:
                # Merge dataframes
                final_df = merge_data(conversions_df, spends_df, preprocessed_df)

                # Compute new metrics
                final_df['New Response'] = final_df['Conversions'] * final_df['Response_Change']
                final_df['Budget Change'] = ((final_df['Sum_optmSpendUnit'] - final_df['Spend']) / final_df['Spend'])
                final_df['Absolute Budget Change'] = (final_df['Sum_optmSpendUnit'] - final_df['Spend']).round(1)

                # Compute overall KPIs
                total_new_response = final_df['New Response'].sum()
                total_old_response = final_df['Conversions'].sum()
                total_new_budget = final_df['Sum_optmSpendUnit'].sum()
                total_old_budget = final_df['Spend'].sum()

                # Avoid division by zero
                response_change_kpi = ((total_new_response / total_old_response) - 1) * 100 if total_old_response != 0 else 0
                budget_change_kpi = ((total_new_budget - total_old_budget) / total_old_budget) * 100 if total_old_budget != 0 else 0
                cpa_change = ((total_new_budget / total_new_response) / (total_old_budget / total_old_response) - 1) * 100 if total_new_response != 0 and total_old_response != 0 and total_old_budget != 0 else 0

                # Rename and select desired columns
                final_df = final_df.rename(columns={
                    'Channel': 'channel',
                    'Spend': 'old_budget',
                    'Sum_optmSpendUnit': 'new_budget',
                    'Conversions': 'old_response',
                    'New Response': 'new_response',
                    'Change': 'budget change',
                    'Response_Change': 'resp change',
                    'Absolute Budget Change': 'abs budg change'
                })

                final_df = final_df[[
                    'channel', 'old_budget', 'new_budget', 'old_response', 'new_response',
                    'budget change', 'resp change', 'abs budg change'
                ]]

                # Fill NaN values with 0 before converting to integer
                final_df['old_response'] = final_df['old_response'].fillna(0)
                final_df['new_response'] = final_df['new_response'].fillna(0)

                print(f"CPA Change: {cpa_change}") # Add this line

                display_dashboard(final_df, budget_change_kpi, response_change_kpi, cpa_change)

if __name__ == "__main__":
    main()
