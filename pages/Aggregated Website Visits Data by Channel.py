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
    
    # Iterate through columns, aggregating by channel
    for col in df.columns:
        # Skip the `solID` and `KPI_Website_Sessions` columns
        if col in ['solID', 'KPI_Website_Sessions']:
            continue
            
        # Extract the channel name (e.g., "TikTok" from "TikTok_Spend")
        channel = re.match(r'([A-Za-z]+)', col)
        if channel:
            channel_name = channel.group(1)
            
            # Initialize channel sum if not already in dictionary
            if channel_name not in channel_data:
                channel_data[channel_name] = 0
                
            # Sum up the values for this column into the corresponding channel total
            channel_data[channel_name] += df[col].sum()
    
    # Convert channel_data dictionary to a DataFrame for display
    channel_df = pd.DataFrame(list(channel_data.items()), columns=['Channel', 'Total Visits'])
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

        # Aggregate website visits by channel
        channel_visits_df = aggregate_website_visits(filtered_df)
        st.subheader("Aggregated Website Visits by Channel")
        st.write(channel_visits_df)

        # Download aggregated data as Excel
        excel_data = download_excel(channel_visits_df, sheet_name='Channel Visits')
        st.download_button(
            label="Download Channel Visits as Excel",
            data=excel_data,
            file_name="channel_visits_aggregation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        writer.close()
    output.seek(0)
    return output

if __name__ == "__main__":
    main()
