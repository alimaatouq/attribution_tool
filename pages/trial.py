import streamlit as st
import pandas as pd
import io

def consolidate_and_aggregate(data_df, mapping_df, channels):
    # Create a mapping for consolidated columns
    column_map = mapping_df.set_index('Original Column Name')['Consolidated Column Name'].to_dict()
    data_df = data_df.rename(columns=column_map)

    # Initialize a dictionary to store spend sums for each channel
    aggregated_data = {}

    # Aggregate each channel's spend once
    for channel in channels:
        # Identify spend columns specific to the current channel after consolidation
        channel_spend_columns = [col for col in data_df.columns if f"{channel}_Spend" in col]
        
        # Sum up the spends across all consolidated columns for the channel
        if channel_spend_columns:
            aggregated_data[channel] = data_df[channel_spend_columns].sum(axis=1)

    # Create a DataFrame for aggregated spends with a single column per channel
    aggregated_df = pd.DataFrame(aggregated_data)
    aggregated_df['Date'] = data_df['Date']

    return aggregated_df

# Streamlit UI for file upload and processing
st.title("Channel Spend Aggregation")
st.write("Upload your data file and column mapping file to aggregate spend by channel.")

data_file = st.file_uploader("Upload Data File", type=["xlsx"])
mapping_file = st.file_uploader("Upload Mapping File", type=["csv"])

if data_file and mapping_file:
    data_df = pd.read_excel(data_file)
    mapping_df = pd.read_csv(mapping_file)
    channels = ["Tiktok", "LinkedIn", "MMS", "Youtube", "SeedTag", "Snap"]
    aggregated_spend_df = consolidate_and_aggregate(data_df, mapping_df, channels)

    # Save aggregated data to Excel and provide a download link
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        aggregated_spend_df.to_excel(writer, index=False, sheet_name='Aggregated Spend')
    buffer.seek(0)

    st.download_button(
        label="Download Aggregated Spend Data",
        data=buffer,
        file_name="Aggregated_Spend_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
