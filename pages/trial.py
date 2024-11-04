import streamlit as st
import pandas as pd
from io import BytesIO

def load_csv_data(uploaded_file):
    # Load data from an uploaded CSV file
    return pd.read_csv(uploaded_file)

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
        # Process only columns containing "spend" (assumed spend columns)
        if 'spend' in col.lower():
            # Extract channel name (e.g., "TikTok" from "TikTok_Spend")
            channel = col.split('_')[0]
            
            # Initialize channel entry if not already present
            if channel not in channel_data:
                channel_data[channel] = {'Spend': 0, 'Visits': 0}
                
            # Sum up the spend data for the channel
            channel_data[channel]['Spend'] += pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
    
    # Convert channel data to a DataFrame
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
    st.write("Upload the necessary CSV and Excel files to aggregate data by channel.")

    # File uploaders for CSV and Excel files
    csv_file = st.file_uploader("Upload Channel Data (CSV)", type="csv")
    excel_file = st.file_uploader("Upload Additional Channel Data (Excel)", type="xlsx")
    
    if csv_file and excel_file:
        # Load data
        csv_data = load_csv_data(csv_file)
        excel_data = load_excel_data(excel_file)
        
        # Display preview of each file
        st.subheader("CSV Data Preview")
        st.write(csv_data.head())
        
        st.subheader("Excel Data Preview")
        st.write(excel_data.head())

        # Check for model filtering if 'solID' column exists in CSV data
        if 'solID' in csv_data.columns:
            models = csv_data['solID'].unique()
            selected_model = st.selectbox("Select Model (solID)", options=models)
            csv_data = filter_by_model(csv_data, selected_model)
            st.write(f"Filtered CSV Data for Model {selected_model}")
            st.write(csv_data)
        
        # Combine data from both files if necessary
        combined_data = pd.concat([csv_data, excel_data], ignore_index=True)

        # Aggregate data by channel
        aggregated_data = aggregate_data_by_channel(combined_data)
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
