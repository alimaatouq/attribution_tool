import streamlit as st
import pandas as pd
import re
from io import BytesIO

def load_data(uploaded_file):
    return pd.read_csv(uploaded_file)

def filter_by_model(df, selected_model):
    return df[df['solID'] == selected_model]

def aggregate_website_metrics(df, selected_kpi):
    channel_data = {}
    
    for col in df.columns:
        if 'spend' not in col.lower() or col == selected_kpi:
            continue
            
        channel = re.match(r'([A-Za-z]+)', col)
        if channel:
            channel_name = channel.group(1)
            
            if channel_name not in channel_data:
                channel_data[channel_name] = 0
            
            column_sum = pd.to_numeric(df[col], errors='coerce').sum()
            channel_data[channel_name] += column_sum
    
    channel_df = pd.DataFrame(list(channel_data.items()), columns=['Channel', 'Metric'])
    channel_df['Metric'] = channel_df['Metric'].round(0).astype(int)
    
    total_metric = channel_df['Metric'].sum()
    total_row = pd.DataFrame([{'Channel': 'Total', 'Metric': total_metric}])
    channel_df = pd.concat([channel_df, total_row], ignore_index=True)
    
    return channel_df

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def main():
    st.title("Website Metrics Aggregation by Channel")
    st.write("Upload the pareto_alldecomp_matrix CSV file, filter by model, and aggregate website metrics by channel.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)

        models = df['solID'].unique()
        selected_model = st.selectbox("Select Model (solID)", options=models)

        filtered_df = filter_by_model(df, selected_model)
        st.write(f"Data for Model {selected_model}:", filtered_df)

        selected_kpi = st.selectbox("Select KPI", options=['KPI_Website_Sessions', 'KPI_Website_Conversions'])
        
        channel_metrics_df_with_total = aggregate_website_metrics(filtered_df, selected_kpi)
        st.subheader(f"Aggregated {selected_kpi} by Channel with Total")
        st.write(channel_metrics_df_with_total)

        channel_metrics_df_without_total = channel_metrics_df_with_total[channel_metrics_df_with_total['Channel'] != 'Total']

        excel_data = download_excel(channel_metrics_df_without_total, sheet_name='Channel Metrics')
        st.download_button(
            label=f"Download {selected_kpi} Data as Excel (without Total)",
            data=excel_data,
            file_name="channel_metrics_aggregation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
