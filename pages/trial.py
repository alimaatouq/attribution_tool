import streamlit as st
import pandas as pd
import re
from io import BytesIO

def load_data(uploaded_file):
    return pd.read_csv(uploaded_file)

def filter_by_model(df, selected_model):
    return df[df['solID'] == selected_model]

def aggregate_website_metric(df, selected_kpi):
    channel_creative_data = {}
    
    for col in df.columns:
        if 'spend' not in col.lower() or col == selected_kpi:
            continue
            
        match = re.match(r'([A-Za-z\s]+)_(.*?)(?:_\d+)?_Spend', col)
        if match:
            channel_name = match.group(1).strip().lower()
            creative_name = match.group(2).strip().lower()
            
            key = f"{channel_name}_{creative_name}"
            if key not in channel_creative_data:
                channel_creative_data[key] = 0

            column_sum = pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
            channel_creative_data[key] += column_sum
    
    channel_creative_df = pd.DataFrame(
        [{'Channel': key.split('_')[0].title(), 'Creative': key.split('_')[1].title(), 'Metric': visits}
         for key, visits in channel_creative_data.items()]
    )
    
    channel_creative_df['Metric'] = channel_creative_df['Metric'].round(0).astype(int)
    
    total_metric = channel_creative_df['Metric'].sum()
    total_row = pd.DataFrame([{'Channel': 'Total', 'Creative': '', 'Metric': total_metric}])
    channel_creative_df = pd.concat([channel_creative_df, total_row], ignore_index=True)
    
    return channel_creative_df

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def main():
    st.title("Website KPI Aggregation by Channel and Creative")
    st.write("Upload a CSV file, filter by model, and aggregate website KPIs by channel and creative.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.write("Data Preview:", df.head())

        models = df['solID'].unique()
        selected_model = st.selectbox("Select Model (solID)", options=models)

        filtered_df = filter_by_model(df, selected_model)
        st.write(f"Data for Model {selected_model}:", filtered_df)

        selected_kpi = st.selectbox("Select KPI", options=['KPI_Website_Sessions', 'KPI_Website_Conversions'])
        
        channel_creative_metric_df_with_total = aggregate_website_metric(filtered_df, selected_kpi)
        st.subheader("Aggregated Website KPI by Channel and Creative with Total")
        st.write(channel_creative_metric_df_with_total)

        channel_creative_metric_df_without_total = channel_creative_metric_df_with_total[channel_creative_metric_df_with_total['Channel'] != 'Total']

        excel_data = download_excel(channel_creative_metric_df_without_total, sheet_name='Channel_Creative KPI')
        st.download_button(
            label="Download Channel and Creative KPI as Excel (without Total)",
            data=excel_data,
            file_name="channel_creative_kpi_aggregation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
