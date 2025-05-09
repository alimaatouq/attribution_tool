import streamlit as st
import pandas as pd
import re
from io import BytesIO

def load_conversions(file, solID_value):
    df = pd.read_csv(file)
    if 'solID' not in df.columns:
        raise ValueError("Missing 'solID' column in conversions file.")
    df = df[df['solID'] == solID_value]
    channel_data = {}
    for col in df.columns:
        if 'spend' not in col.lower() or col == 'KPI_Website_Conversions':
            continue
        match = re.match(r'([A-Za-z]+)', col)
        if match:
            channel = match.group(1)
            channel_data[channel] = channel_data.get(channel, 0) + pd.to_numeric(df[col], errors='coerce').sum()
    return pd.DataFrame(list(channel_data.items()), columns=['channel', 'old_response'])

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
    return pd.DataFrame(list(channel_data.items()), columns=['channel', 'old_budget'])

def load_preprocessed(file):
    df = pd.read_csv(file)
    df['period_number'] = df['periods'].apply(lambda x: int(re.search(r'\d+', str(x)).group()) if pd.notnull(x) else None)
    channel_split = df['channels'].str.extract(r'([^_]+)_([^_]+)_(.+)')
    channel_split.columns = ['channel', 'channel_type', 'channel_metric']
    df = pd.concat([df, channel_split], axis=1)
    grouped = df.groupby('channel').agg({
        'optmSpendUnit': 'sum',
        'optmResponseUnit': 'sum',
        'period_number': 'mean'
    }).reset_index()
    grouped['new_budget'] = (grouped['optmSpendUnit'] * grouped['period_number']).round(1)
    grouped['new_response'] = (grouped['optmResponseUnit'] * grouped['period_number']).round(1)
    return grouped[['channel', 'new_budget', 'new_response']]

def merge_data(conversions_df, spends_df, pre_df):
    df = pd.merge(conversions_df, spends_df, on='channel', how='outer')
    df = pd.merge(df, pre_df, on='channel', how='outer')

    df['budget change'] = ((df['new_budget'] - df['old_budget']) / df['old_budget']) * 100
    df['resp change'] = ((df['new_response'] - df['old_response']) / df['old_response']) * 100
    df['abs budg change'] = (df['new_budget'] - df['old_budget'])

    df = df[['channel', 'old_budget', 'new_budget', 'old_response', 'new_response',
             'budget change', 'resp change', 'abs budg change']].round(1)
    
    # Formatting like image
    df['old_budget'] = df['old_budget'].map('${:,.0f}'.format)
    df['new_budget'] = df['new_budget'].map('${:,.0f}'.format)
    df['budget change'] = df['budget change'].map('{:.2f}%'.format)
    df['resp change'] = df['resp change'].map(lambda x: '{:.3f}'.format(x) if pd.notnull(x) else 'nan')
    df['abs budg change'] = df['abs budg change'].map(lambda x: f"(${abs(x):,.0f})" if x < 0 else f"${x:,.0f}")

    return df

def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='KPI_Results')
    output.seek(0)
    return output

# Streamlit App
def main():
    st.title("📊 Attribution Optimization Report")
    st.markdown("Upload all 3 files and enter the **solID** to see your optimization summary.")

    col1, col2 = st.columns(2)
    with col1:
        conversions_file = st.file_uploader("🔹 Upload pareto_alldecomp_matrix CSV", type="csv")
        preprocessed_file = st.file_uploader("🔹 Upload Reallocation CSV", type="csv")
    with col2:
        spends_file = st.file_uploader("🔹 Upload Raw Data Excel", type="xlsx")
        solID_value = st.text_input("🔸 Enter solID (e.g., 4_9407_1)")

    if conversions_file and spends_file and preprocessed_file and solID_value:
        try:
            conversions_df = load_conversions(conversions_file, solID_value)
            spends_df = load_spends(spends_file)
            preprocessed_df = load_preprocessed(preprocessed_file)

            final_df = merge_data(conversions_df, spends_df, preprocessed_df)

            st.subheader("✅ Optimization Summary Table")
            st.dataframe(final_df, use_container_width=True)

            st.download_button(
                label="📥 Download Optimization Report as Excel",
                data=to_excel_bytes(final_df),
                file_name="optimization_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
