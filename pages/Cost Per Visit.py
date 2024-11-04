import streamlit as st
import pandas as pd
from io import BytesIO

def load_data(spend_file, visits_file):
    # Load the first sheet in each uploaded Excel file
    spend_df = pd.read_excel(spend_file)  # Load first sheet by default
    visits_df = pd.read_excel(visits_file)  # Load first sheet by default
    return spend_df, visits_df

def merge_and_calculate(spend_df, visits_df):
    # Merge the two DataFrames on the "Channel" column
    merged_df = pd.merge(spend_df, visits_df, on="Channel", how="inner")

    # Ensure Spend and Visits columns are numeric, converting non-numeric to NaN and filling NaN with 0
    merged_df['Spend'] = pd.to_numeric(merged_df['Spend'], errors='coerce').fillna(0)
    merged_df['Visits'] = pd.to_numeric(merged_df['Visits'], errors='coerce').fillna(0)

    # Calculate Cost per Visit and handle division by zero
    merged_df['Cost per Visit'] = merged_df.apply(
        lambda row: row['Spend'] / row['Visits'] if row['Visits'] > 0 else 0, axis=1
    )
    
    # Format Spend and Visits as integers and Cost per Visit as a float with 2 decimal places
    merged_df['Spend'] = merged_df['Spend'].astype(int)
    merged_df['Visits'] = merged_df['Visits'].astype(int)
    merged_df['Cost per Visit'] = merged_df['Cost per Visit'].round(2)
    
    return merged_df

def download_excel(df, sheet_name='Merged Data'):
    # Convert the DataFrame to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        writer.close()
    output.seek(0)
    return output

# Function definitions here (load_data, clean_and_merge, download_excel)

def clean_and_merge(spend_df, visits_df):
    # Merge the two DataFrames on the "Channel" column
    merged_df = pd.merge(spend_df, visits_df, on="Channel", how="inner")

    # Ensure Spend and Visits columns are numeric; convert non-numeric to NaN
    merged_df['Spend'] = pd.to_numeric(merged_df['Spend'], errors='coerce').fillna(0)
    merged_df['Visits'] = pd.to_numeric(merged_df['Visits'], errors='coerce').fillna(0)

    # Calculate Cost per Visit only where Visits > 0 to avoid division by zero
    merged_df['Cost per Visit'] = merged_df.apply(
        lambda row: row['Spend'] / row['Visits'] if row['Visits'] > 0 else 0, axis=1
    )

    # Format Spend and Visits as integers, round Cost per Visit to 2 decimals
    merged_df['Spend'] = merged_df['Spend'].astype(int)
    merged_df['Visits'] = merged_df['Visits'].astype(int)
    merged_df['Cost per Visit'] = merged_df['Cost per Visit'].round(2)
    
    # Calculate Totals for Spend and Visits, and Average for Cost per Visit
    total_spend = merged_df['Spend'].sum()
    total_visits = merged_df['Visits'].sum()
    avg_cost_per_visit = round(total_spend / total_visits, 2) if total_visits > 0 else 0

    # Add a total row to the DataFrame
    total_row = pd.DataFrame([{
        'Channel': 'TOTAL',
        'Spend': total_spend,
        'Visits': total_visits,
        'Cost per Visit': avg_cost_per_visit
    }])
    merged_df = pd.concat([merged_df, total_row], ignore_index=True)
    
    return merged_df


def main():
    st.title("Channel Spend and Visits Summary with Cost per Visit")
    st.write("Upload the Spend and Visits Excel files to merge them based on the channel and calculate Cost per Visit.")

    # File uploaders for the two Excel files
    spend_file = st.file_uploader("Upload Aggregated Spend Data by Channel", type="xlsx")
    visits_file = st.file_uploader("Upload Channel Visits Aggregation", type="xlsx")
    
    if spend_file and visits_file:
        # Load the data from both files
        spend_df, visits_df = load_data(spend_file, visits_file)
        
        # Merge, clean data, and calculate Cost per Visit
        merged_df = clean_and_merge(spend_df, visits_df)
        
        # Display the merged DataFrame with Cost per Visit in styled format
        st.subheader("Merged Data with Total Spend, Visits, and Average Cost per Visit")
        st.write(merged_df.style.format({"Spend": "${:,.0f}", "Visits": "{:,.0f}", "Cost per Visit": "${:,.2f}"}))

        # Download button for the merged Excel file
        excel_data = download_excel(merged_df, sheet_name='Merged Data')
        st.download_button(
            label="Download Merged Data as Excel",
            data=excel_data,
            file_name="merged_channel_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
