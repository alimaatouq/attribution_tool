import streamlit as st
import pandas as pd
from io import BytesIO

def load_excel_data(uploaded_file):
    # Load data from an uploaded Excel file
    return pd.read_excel(uploaded_file)

def filter_by_model(df, selected_model):
    # Filter data by selected model (e.g., solID)
    return df[df['solID'] == selected_model]

def aggregate_data_by_channel(df):
    # Initialize dictionary to store total visits and spend per channel
    channel_data = {}

    for col in df.columns:
        # Only process columns that contain "spend" (assumed spend columns)
        if 'spend' in col.lower():
            # Extract channel name from column (e.g., "TikTok" from "TikTok_Spend")
            channel = col.split('_')[0]
            
            # Initialize channel entry if not already present
            if channel not in channel_data:
                channel_data[channel] = {'Spend': 0, 'Visits': 0}
                
            # Sum up the spend data for the channel
            channel_data[channel]['Spend'] += pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
    
    # Convert channel data to a DataFrame for easier manipulation
    channel_df = pd.DataFrame([
        {'Channel': channel, 'Spend': data['Spend'], 'Visits': data['Visits']}
        for channel, data in channel_data.items()
    ])
    
    # Calculate cost per visit and add a TOTAL row with sums
    channel_df['Cost per Visit'] = channel_df.apply(
        lambda row: round(row['Spend'] / row['Visits'], 2) if row['Visits'] > 0 else 0, axis=1
    )
    total_row = pd.DataFrame([{
        'Channel': 'TOTAL',
        'Spend': channel_df['Spend'].sum(),
        'Visits': channel_df['Visits'].sum(),
        'Cost per Visit': round(channel_df['Spend'].sum() / channel_df['Visits'].sum(), 2)
    }])
    
    # Append TOTAL row for display
    channel_df_with_total = pd.concat([channel_df, total_row], ignore_index=True)
    return channel_df_with_total

def download_excel(df, sheet_name='Channel Data'):
    # Prepare the DataFrame for download
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        writer.close()
    output.seek(0)
    return output

def main():
    st.title("Channel Spend and Visits Aggregation Tool")
    st.write("Upload the necessary files to aggregate data by channel.")

    # File uploader
    spend_file = st.file_uploader("Upload Channel Spend and Visits Data", type="xlsx")
    
    if spend_file:
        # Load data
        df = load_excel_data(spend_file)
        st.write("Data Preview:", df.head())

        # Select model (solID) if applicable
        models = df['solID'].unique() if 'solID' in df.columns else []
        selected_model = st.selectbox("Select Model (solID)", options=models) if models else None

        # Filter data by selected model if applicable
        if selected_model:
            df = filter_by_model(df, selected_model)
            st.write(f"Data for Model {selected_model}:", df)

        # Aggregate data by channel
        aggregated_data = aggregate_data_by_channel(df)
        st.subheader("Aggregated Data by Channel with Total")
        st.write(aggregated_data)

        # Prepare download data (excluding Total row)
        download_df = aggregated_data[aggregated_data['Channel'] != 'TOTAL']
        excel_data = download_excel(download_df)

        # Download button for final output without Total row
        st.download_button(
            label="Download Aggregated Data (without Total)",
            data=excel_data,
            file_name="aggregated_channel_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
