import streamlit as st
import pandas as pd
import re
from io import BytesIO

def load_data(uploaded_file):
    # Load the uploaded CSV file
    return pd.read_csv(uploaded_file)

def filter_by_model(df, selected_model):
    # Filter the DataFrame based on the selected model
    return df[df['solID'] == selected_model]

def aggregate_website_visits(df):
    # Initialize dictionary to store visits by each channel and creative combination
    channel_creative_data = {}
    
    # Display column names for debugging
    st.write("Columns in DataFrame:", df.columns.tolist())
    
    # Iterate through columns, aggregating by channel and creative for "spend" columns
    for col in df.columns:
        # Skip columns that do not contain "spend" and the KPI_Website_Sessions column
        if 'spend' not in col.lower() or col == 'KPI_Website_Sessions':
            continue
            
        # Adjust regex to capture multi-word channels and creatives, and remove trailing numbers (e.g., YouTube_Generic_1_Spend)
        match = re.match(r'([A-Za-z\s]+)_(.*?)(?:_\d+)?_Spend', col)
        if match:
            # Standardize channel and creative names by stripping spaces, numbers, and converting to lowercase
            channel_name = match.group(1).strip().lower()
            creative_name = match.group(2).strip().lower()
            
            # Form the consolidated key without trailing numbers
            key = f"{channel_name}_{creative_name}"
            if key not in channel_creative_data:
                channel_creative_data[key] = 0

            # Show column data type and sample values for debugging
            st.write(f"Column '{col}' - Data Type: {df[col].dtype}")
            st.write(f"Sample data from '{col}':", df[col].head())
            
            # Convert column to numeric, forcing non-numeric values to NaN, then sum, treating NaNs as zero
            column_sum = pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
            channel_creative_data[key] += column_sum
    
    # Convert channel_creative_data dictionary to a DataFrame for display
    channel_creative_df = pd.DataFrame(
        [{'Channel': key.split('_')[0].title(), 'Creative': key.split('_')[1].title(), 'Visits': visits}
         for key, visits in channel_creative_data.items()]
    )
    
    # Convert Visits to whole numbers (integers)
    channel_creative_df['Visits'] = channel_creative_df['Visits'].round(0).astype(int)
    
    # Calculate the total visits across all channels and creatives
    total_visits = channel_creative_df['Visits'].sum()
    
    # Append a row for total visits to the DataFrame
    total_row = pd.DataFrame([{'Channel': 'Total', 'Creative': '', 'Visits': total_visits}])
    channel_creative_df = pd.concat([channel_creative_df, total_row], ignore_index=True)
    
    return channel_creative_df

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def main():
    st.title("Website Visits Aggregation by Channel and Creative")
    st.write("Upload a CSV file, filter by model, and aggregate website visits by channel and creative.")

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

        # Aggregate website visits by channel and creative, including the Total row
        channel_creative_visits_df_with_total = aggregate_website_visits(filtered_df)
        st.subheader("Aggregated Website Visits by Channel and Creative with Total")
        st.write(channel_creative_visits_df_with_total)

        # Exclude the Total row for the downloadable file
        channel_creative_visits_df_without_total = channel_creative_visits_df_with_total[channel_creative_visits_df_with_total['Channel'] != 'Total']

        # Download aggregated data as Excel, without the Total row
        excel_data = download_excel(channel_creative_visits_df_without_total, sheet_name='Channel_Creative Visits')
        st.download_button(
            label="Download Channel and Creative Visits as Excel (without Total)",
            data=excel_data,
            file_name="channel_creative_visits_aggregation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
