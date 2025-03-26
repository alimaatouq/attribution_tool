import streamlit as st
import pandas as pd
import re
from io import BytesIO

def consolidate_columns(df):
    # Filter columns to include only "spend" variables
    filtered_columns = [col for col in df.columns if "spend" in col.lower()]
    
    # Create a mapping of original columns to consolidated names
    column_mapping = {}
    base_names = set()
    
    for col in filtered_columns:
        # Remove any trailing numbers (with optional underscore/dash prefix)
        # Also handles cases where number is in the middle (DisplayBanner1)
        base_name = re.sub(r'(\d+)(?=_Spend|$)', '', col)
        base_name = re.sub(r'([_-]\d+)(?=_Spend|$)', '', base_name)
        
        # Standardize the name format
        base_name = base_name.rstrip('_').lower()
        column_mapping[col] = base_name
        base_names.add(base_name)
    
    # Create consolidated dataframe
    consolidated_df = pd.DataFrame({
        'Original Column Name': list(column_mapping.keys()),
        'Consolidated Column Name': list(column_mapping.values())
    })
    
    return consolidated_df

def aggregate_spend(df, consolidated_df):
    spend_data = []
    
    # Create a mapping from original to consolidated names
    column_map = dict(zip(
        consolidated_df['Original Column Name'],
        consolidated_df['Consolidated Column Name']
    ))
    
    # Group by consolidated names and sum
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        # Get all original columns that map to this consolidated name
        original_columns = [col for col, name in column_map.items() 
                          if name == consolidated_name]
        
        # Calculate total spend
        total_spend = df[original_columns].sum().sum()
        
        # Parse channel and creative from consolidated name
        parts = re.split(r'_|(?<=[a-z])(?=[A-Z])', consolidated_name)
        if len(parts) >= 2:
            channel = parts[0].title()  # Capitalize first letter
            creative = '_'.join(parts[1:-1]) if len(parts) > 2 else parts[1]
            creative = creative.title()
            
            spend_data.append({
                'Channel': channel,
                'Creative': creative,
                'Spend': total_spend
            })
    
    spend_df = pd.DataFrame(spend_data)
    return spend_df

def summarize_channel_spend(spend_df):
    # Calculate total spend by channel
    channel_summary = spend_df.groupby('Channel')['Spend'].sum().reset_index()
    total_spend = channel_summary['Spend'].sum()
    
    # Calculate percentage contribution for each channel, rounded to nearest whole number
    channel_summary['Percentage Contribution'] = ((channel_summary['Spend'] / total_spend) * 100).round(0).astype(int)

    # Add a row for the total spend
    total_row = pd.DataFrame([{
        'Channel': 'Total',
        'Spend': total_spend,
        'Percentage Contribution': 100
    }])
    channel_summary = pd.concat([channel_summary, total_row], ignore_index=True)

    return channel_summary

def create_final_output_table(spend_df, channel_summary_df):
    final_df = spend_df.copy()
    final_df['Channel - Contribution'] = final_df['Channel']
    
    for _, row in channel_summary_df.iterrows():
        channel = row['Channel']
        if channel != 'Total':
            contribution_percentage = int(row['Percentage Contribution'])
            final_df.loc[final_df['Channel'] == channel, 'Channel - Contribution'] = f"{channel} - {contribution_percentage}%"

    # Format the Spend column as numbers
    final_df['Spend'] = final_df['Spend'].apply(lambda x: f"{x:,.0f}")

    final_df = final_df[['Channel - Contribution', 'Creative', 'Spend']]
    return final_df

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def main():
    st.title("Share of Spends by Placements App")
    st.write("Upload the Processed Data Excel file to consolidate and analyze spend data by channel and creative.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)

        # Consolidate columns with spend data only
        consolidated_df = consolidate_columns(df)

        # Aggregate and summarize spend data
        spend_df = aggregate_spend(df, consolidated_df)
        channel_summary_df = summarize_channel_spend(spend_df)
        final_output_df = create_final_output_table(spend_df, channel_summary_df)

        # Display the final output table
        st.subheader("Final Output Table")
        st.write(final_output_df)

        # Provide download option for the final output table
        excel_data_final_output = download_excel(final_output_df, sheet_name='Final Output')
        st.download_button(
            label="Download Final Output Table as Excel",
            data=excel_data_final_output,
            file_name="Share of spends by placements.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
