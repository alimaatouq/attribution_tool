import streamlit as st
import pandas as pd
import re
from io import BytesIO

def load_data(uploaded_file):
    # Load the uploaded file
    return pd.read_csv(uploaded_file)

def filter_by_model(df, selected_model):
    # Filter the DataFrame based on the selected model
    return df[df['solID'] == selected_model]

def aggregate_website_visits(df):
    # Initialize dictionary to store the total visits by each channel
    channel_data = {}
    
    # Iterate through columns, aggregating by channel only for "spend" columns
    for col in df.columns:
        # Skip columns that do not contain "spend" and the KPI_Website_Sessions column
        if 'spend' not in col.lower() or col == 'KPI_Website_Sessions':
            continue
            
        # Extract the channel name (e.g., "TikTok" from "TikTok_Spend")
        channel = re.match(r'([A-Za-z]+)', col)
        if channel:
            channel_name = channel.group(1)
            
            # Initialize channel sum if not already in dictionary
            if channel_name not in channel_data:
                channel_data[channel_name] = 0
                
            # Convert column to numeric, forcing non-numeric values to NaN, then sum
            column_sum = pd.to_numeric(df[col], errors='coerce').sum()
            channel_data[channel_name] += column_sum
    
    # Convert channel_data dictionary to a DataFrame for display
    channel_df = pd.DataFrame(list(channel_data.items()), columns=['Channel', 'Visits'])
    
    # Convert Visits to whole numbers (integers)
    channel_df['Visits'] = channel_df['Visits'].round(0).astype(int)
    
    # Calculate the total visits across all channels
    total_visits = channel_df['Visits'].sum()
    
    # Append a row for total visits to the DataFrame
    total_row = pd.DataFrame([{'Channel': 'Total', 'Visits': total_visits}])
    channel_df = pd.concat([channel_df, total_row], ignore_index=True)
    
    return channel_df


def main():
    st.title("Website Visits Aggregation by Channel")
    st.write("Upload a CSV file, filter by model, and aggregate website visits by channel.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Load and display data
        df = load_data(uploaded_file)
        st.write("Data Preview:", df.head())

        # Model (solID) selection
        models = df['solID'].unique()
        selected_model = st.selectbox("Select Model (solID)", options=models)

        # Filter data by selected model
        filtered_df = filter_by_model(df, selected_model)
        st.write(f"Data for Model {selected_model}:", filtered_df)

        # Aggregate website visits by channel, including the Total row
        channel_visits_df_with_total = aggregate_website_visits(filtered_df)
        st.subheader("Aggregated Website Visits by Channel with Total")
        st.write(channel_visits_df_with_total)

        # Exclude the Total row for the downloadable file
        channel_visits_df_without_total = channel_visits_df_with_total[channel_visits_df_with_total['Channel'] != 'Total']

        # Download aggregated data as Excel, without the Total row
        excel_data = download_excel(channel_visits_df_without_total, sheet_name='Channel Visits')
        st.download_button(
            label="Download Channel Visits as Excel (without Total)",
            data=excel_data,
            file_name="channel_visits_aggregation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
