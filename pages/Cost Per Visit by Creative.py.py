import streamlit as st
import pandas as pd
from io import BytesIO

def load_data(spend_file, visits_file):
    # Load the uploaded files
    spend_df = pd.read_excel(spend_file)
    visits_df = pd.read_excel(visits_file)
    return spend_df, visits_df

def clean_and_merge(spend_df, visits_df):
    # Standardize channel and format names by converting to lowercase and stripping whitespace
    spend_df['Channel'] = spend_df['Channel'].str.lower().str.strip()
    spend_df['Creative'] = spend_df['Creative'].str.lower().str.strip()
    visits_df['Channel'] = visits_df['Channel'].str.lower().str.strip()
    visits_df['Creative'] = visits_df['Creative'].str.lower().str.strip()
    
    # Merge the two DataFrames on the standardized "Channel" and "Creative" columns
    merged_df = pd.merge(spend_df, visits_df, on=["Channel", "Creative"], how="outer")

    # Ensure Spend and Visits columns are numeric; convert non-numeric to NaN
    merged_df['Spend'] = pd.to_numeric(merged_df['Spend'], errors='coerce').fillna(0)
    merged_df['Visits'] = pd.to_numeric(merged_df['Visits'], errors='coerce').fillna(0)

    # Calculate Cost per Visit (CPV) for each row
    merged_df['CPV'] = merged_df.apply(
        lambda row: round(row['Spend'] / row['Visits'], 2) if row['Visits'] > 0 else 0, axis=1
    )

    # Calculate totals for each channel
    total_rows = []
    for channel in merged_df['Channel'].unique():
        channel_data = merged_df[merged_df['Channel'] == channel]
        total_spend = channel_data['Spend'].sum()
        total_visits = channel_data['Visits'].sum()
        avg_cpv = round(total_spend / total_visits, 2) if total_visits > 0 else 0
        total_rows.append({'Channel': channel.title(), 'Creative': 'Total', 'Spend': total_spend, 'Visits': total_visits, 'CPV': avg_cpv})
    
    # Add an overall total row
    overall_spend = merged_df['Spend'].sum()
    overall_visits = merged_df['Visits'].sum()
    overall_cpv = round(overall_spend / overall_visits, 2) if overall_visits > 0 else 0
    total_rows.append({'Channel': 'Total', 'Creative': '-', 'Spend': overall_spend, 'Visits': overall_visits, 'CPV': overall_cpv})
    
    # Combine the total rows with the original data
    merged_with_totals = pd.concat([merged_df, pd.DataFrame(total_rows)], ignore_index=True)
    
    return merged_with_totals

def download_excel_with_formatting(df, sheet_name='Formatted Data'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        # Apply formatting for totals
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Format for total rows
        total_format = workbook.add_format({'bold': True, 'bg_color': '#B8860B', 'font_color': '#FFFFFF'})
        for row_num, value in enumerate(df['Creative']):
            if value == 'Total':
                worksheet.set_row(row_num + 1, None, total_format)  # +1 to skip header row
        
        # Currency format for Spend and CPV
        currency_format = workbook.add_format({'num_format': '$#,##0.00'})
        worksheet.set_column('C:C', None, currency_format)
        worksheet.set_column('E:E', None, currency_format)
        
    output.seek(0)
    return output

def main():
    st.title("Channel and Creative Spend and Visits Summary with Cost per Visit")
    st.write("Upload the Spend and Visits Excel files to merge them based on Channel and Creative, calculate CPV, and add a summary with formatting.")

    # File uploaders for the two Excel files
    spend_file = st.file_uploader("Upload Aggregated Spend Data by Channel and Creative", type="xlsx")
    visits_file = st.file_uploader("Upload Channel and Creative Visits Aggregation", type="xlsx")
    
    if spend_file and visits_file:
        # Load the data from both files
        spend_df, visits_df = load_data(spend_file, visits_file)
        
        # Display the loaded DataFrames
        st.subheader("Spend Data (First 5 Rows)")
        st.write(spend_df.head())
        
        st.subheader("Visits Data (First 5 Rows)")
        st.write(visits_df.head())

        # Merge, clean data, and calculate CPV with totals
        formatted_df = clean_and_merge(spend_df, visits_df)
        
        # Display the formatted DataFrame in Streamlit
        st.subheader("Formatted Data with Totals and CPV")
        st.write(formatted_df.style.format({
            "Spend": "${:,.0f}",
            "Visits": "{:,.0f}",
            "CPV": "${:,.2f}"
        }))

        # Download button for the formatted Excel file
        excel_data = download_excel_with_formatting(formatted_df, sheet_name='Formatted Data')
        st.download_button(
            label="Download Formatted Data as Excel",
            data=excel_data,
            file_name="formatted_channel_creative_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
