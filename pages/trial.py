import streamlit as st
import pandas as pd
import re
from openpyxl import load_workbook
from io import BytesIO
import numpy as np

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

    # [previous code remains the same until the CPA check]

    print(f"[Inside to_excel BEFORE isnan/isinf] CPA Change Type: {type(cpa_kpi)}, Value: {cpa_kpi}")

    if isinstance(cpa_kpi, (int, float)):
        if pd.isna(cpa_kpi) or np.isinf(cpa_kpi):  # Changed pd.isinf to np.isinf
            worksheet.write_string(last_row + 3, 1, 'nan') # Or some other placeholder
        else:
            try:
                worksheet.write_number(last_row + 3, 1, cpa_kpi / 100, percentage_format)
                print("[Inside to_excel AFTER writing CPA] CPA Change written successfully.")
            except Exception as e:
                print(f"[Inside to_excel ERROR writing CPA]: {e}")
                worksheet.write_string(last_row + 3, 1, 'Error')
    else:
        worksheet.write_string(last_row + 3, 1, str(cpa_kpi)) # Write the non-numeric value as a string

    writer.close()
    processed_data = output.getvalue()
    return processed_data

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

                print(f"[MAIN] total_new_budget: {total_new_budget}, type: {type(total_new_budget)}")
                print(f"[MAIN] total_new_response: {total_new_response}, type: {type(total_new_response)}")
                print(f"[MAIN] total_old_budget: {total_old_budget}, type: {type(total_old_budget)}")
                print(f"[MAIN] total_old_response: {total_old_response}, type: {type(total_old_response)}")

                response_change_kpi = ((total_new_response / total_old_response) - 1) * 100 if total_old_response != 0 else 0
                budget_change_kpi = ((total_new_budget - total_old_budget) / total_old_budget) * 100 if total_old_budget != 0 else 0
                cpa_change = ((total_new_budget / total_new_response) / (total_old_budget / total_old_response) - 1) * 100 if total_new_response != 0 and total_old_response != 0 and total_old_budget != 0 else 0

                print(f"[MAIN] cpa_change: {cpa_change}, type: {type(cpa_change)}") # Existing print

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

                display_dashboard(final_df, budget_change_kpi, response_change_kpi, cpa_change)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
