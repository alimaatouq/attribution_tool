import streamlit as st
import pandas as pd
import re

# ===============================
# Utility Functions
# ===============================

def load_conversions(file, solID_value):
    df = pd.read_csv(file)
    if 'solID' not in df.columns:
        st.error("The 'solID' column is missing in the uploaded conversions file.")
        return pd.DataFrame()

    df = df[df['solID'] == solID_value]
    channel_data = {}
    for col in df.columns:
        if 'spend' not in col.lower() or col == 'KPI_Website_Conversions':
            continue
        match = re.match(r'([A-Za-z]+)', col)
        if match:
            channel = match.group(1)
            channel_data[channel] = channel_data.get(channel, 0) + pd.to_numeric(df[col], errors='coerce').sum()

    return pd.DataFrame(list(channel_data.items()), columns=['Channel', 'Conversions'])


def load_spends(file):
    df = pd.read_excel(file)
    spend_columns = [col for col in df.columns if "spend" in col.lower()]
    consolidated_columns = [re.sub(r'([_-]\d+)', '', col) for col in spend_columns]
    channel_data = {}
    for original_col, consolidated_col in zip(spend_columns, consolidated_columns):
        match = re.match(r'([A-Za-z]+)', consolidated_col)
        if match:
            channel = match.group(1)
            channel_data[channel] = channel_data.get(channel, 0) + pd.to_numeric(df[original_col], errors='coerce').sum()

    return pd.DataFrame(list(channel_data.items()), columns=['Channel', 'Spend'])


def load_preprocessed(file):
    df = pd.read_csv(file)
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
    grouped_df['Sum_initSpendUnit'] = grouped_df['initSpendUnit'] * grouped_df['period_number']
    grouped_df['Sum_optmSpendUnit'] = grouped_df['optmSpendUnit'] * grouped_df['period_number']
    grouped_df['Sum_initResponseUnit'] = grouped_df['initResponseUnit'] * grouped_df['period_number']
    grouped_df['Sum_optmResponseUnit'] = grouped_df['optmResponseUnit'] * grouped_df['period_number']

    grouped_df['Change'] = (grouped_df['Sum_optmSpendUnit'] - grouped_df['Sum_initSpendUnit']) / grouped_df['Sum_initSpendUnit']
    grouped_df['Response_Change'] = grouped_df['Sum_optmResponseUnit'] / grouped_df['Sum_initResponseUnit']

    columns_to_drop = ['initSpendUnit', 'optmSpendUnit', 'initResponseUnit', 'optmResponseUnit']
    grouped_df = grouped_df.drop(columns=[col for col in columns_to_drop if col in grouped_df.columns])

    return grouped_df


def merge_data(conversions_df, spends_df, preprocessed_df):
    merged_df = pd.merge(conversions_df, spends_df, on='Channel', how='outer')
    merged_df = pd.merge(merged_df, preprocessed_df, on='Channel', how='outer')
    return merged_df


# ===============================
# Streamlit App
# ===============================

st.title("📊 Optimization KPIs Calculator")

with st.sidebar:
    sol_id_to_filter = st.text_input("Enter solID to filter by:", value="4_9407_1")
    conversions_file = st.file_uploader("Upload Conversions CSV", type=["csv"])
    spends_file = st.file_uploader("Upload Spends Excel", type=["xlsx"])
    preprocessed_file = st.file_uploader("Upload Preprocessed CSV", type=["csv"])

if conversions_file and spends_file and preprocessed_file and sol_id_to_filter:

    # Load data
    conversions_df = load_conversions(conversions_file, sol_id_to_filter)
    spends_df = load_spends(spends_file)
    preprocessed_df = load_preprocessed(preprocessed_file)

    if not conversions_df.empty and not spends_df.empty and not preprocessed_df.empty:
        final_df = merge_data(conversions_df, spends_df, preprocessed_df)

        # Compute fields
        final_df['New Response'] = final_df['Conversions'] * final_df['Response_Change']
        final_df['Budget Change'] = ((final_df['Sum_optmSpendUnit'] - final_df['Spend']) / final_df['Spend']) * 100
        final_df['Absolute Budget Change'] = (final_df['Sum_optmSpendUnit'] - final_df['Spend'])

        # Rename and select
        final_df = final_df.rename(columns={
            'Channel': 'channel',
            'Spend': 'old_budget',
            'Sum_optmSpendUnit': 'new_budget',
            'Conversions': 'old_response',
            'New Response': 'new_response',
            'Budget Change': 'budget change',
            'Response_Change': 'resp change',
            'Absolute Budget Change': 'abs budg change'
        })

        final_df = final_df[[
            'channel', 'old_budget', 'new_budget', 'old_response', 'new_response',
            'budget change', 'resp change', 'abs budg change'
        ]]

        # Calculate global KPIs
        total_old_budget = final_df['old_budget'].sum()
        total_new_budget = final_df['new_budget'].sum()
        total_old_response = final_df['old_response'].sum()
        total_new_response = final_df['new_response'].sum()

        kpi_budget_change = ((total_new_budget - total_old_budget) / total_old_budget) * 100
        kpi_response_change = ((total_new_response / total_old_response) - 1) * 100
        kpi_cpa_change = ((total_new_budget / total_new_response) / (total_old_budget / total_old_response) - 1) * 100

        # Show KPIs
        st.metric("📉 Budget Change KPI", f"{kpi_budget_change:.1f}%")
        st.metric("📈 Response Change KPI", f"{kpi_response_change:.1f}%")
        st.metric("💰 CPA Change KPI", f"{kpi_cpa_change:.1f}%")

        # Show table
        st.subheader("Detailed Channel-Level Table")
        st.dataframe(final_df.style.format({
            'old_budget': '{:,.0f}',
            'new_budget': '{:,.0f}',
            'old_response': '{:,.0f}',
            'new_response': '{:,.0f}',
            'budget change': '{:.1f}%',
            'resp change': '{:.2f}',
            'abs budg change': '{:,.0f}'
        }), use_container_width=True)

        # Download button
        st.download_button(
            label="📥 Download as Excel",
            data=final_df.to_excel(index=False, engine='xlsxwriter'),
            file_name="optimization_kpi_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("One or more datasets could not be processed. Please check your files.")
