import streamlit as st
import pandas as pd
from io import BytesIO

def load_data(spend_file, conversions_file):
    spend_df = pd.read_excel(spend_file)
    conversions_df = pd.read_excel(conversions_file)
    return spend_df, conversions_df

def clean_and_merge(spend_df, conversions_df):
    spend_df['Channel'] = spend_df['Channel'].str.lower().str.strip()
    spend_df['Creative'] = spend_df['Creative'].str.lower().str.strip()
    conversions_df['Channel'] = conversions_df['Channel'].str.lower().str.strip()
    conversions_df['Creative'] = conversions_df['Creative'].str.lower().str.strip()
    
    merged_df = pd.merge(spend_df, conversions_df, on=["Channel", "Creative"], how="outer")
    
    merged_df['Spend'] = pd.to_numeric(merged_df['Spend'], errors='coerce').fillna(0)
    merged_df['Conversions'] = pd.to_numeric(merged_df['Conversions'], errors='coerce').fillna(0)
    
    merged_df['Cost per Conversion'] = merged_df.apply(
        lambda row: round(row['Spend'] / row['Conversions'], 2) if row['Conversions'] > 0 else 0, axis=1
    )
    
    total_rows = []
    for channel in merged_df['Channel'].unique():
        channel_data = merged_df[merged_df['Channel'] == channel]
        total_spend = channel_data['Spend'].sum()
        total_conversions = channel_data['Conversions'].sum()
        avg_cost_per_conversion = round(total_spend / total_conversions, 2) if total_conversions > 0 else 0
        total_rows.append({'Channel': channel.title(), 'Creative': 'Total', 'Spend': total_spend, 'Conversions': total_conversions, 'Cost per Conversion': avg_cost_per_conversion})
    
    overall_spend = merged_df['Spend'].sum()
    overall_conversions = merged_df['Conversions'].sum()
    overall_cost_per_conversion = round(overall_spend / overall_conversions, 2) if overall_conversions > 0 else 0
    total_rows.append({'Channel': 'Total', 'Creative': '-', 'Spend': overall_spend, 'Conversions': overall_conversions, 'Cost per Conversion': overall_cost_per_conversion})
    
    merged_with_totals = pd.concat([merged_df, pd.DataFrame(total_rows)], ignore_index=True)
    
    return merged_with_totals

def download_excel_with_formatting(df, sheet_name='Formatted Data'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        total_format = workbook.add_format({'bold': True, 'bg_color': '#B8860B', 'font_color': '#FFFFFF'})
        for row_num, value in enumerate(df['Creative']):
            if value == 'Total':
                worksheet.set_row(row_num + 1, None, total_format)
        
        currency_format = workbook.add_format({'num_format': '$#,##0.00'})
        worksheet.set_column('C:C', None, currency_format)
        worksheet.set_column('E:E', None, currency_format)
        
    output.seek(0)
    return output

def main():
    st.title("Cost Per Conversion by Channel and Creative")
    st.write("Upload the Spend and Conversions Excel files to merge them based on Channel and Creative, calculate Cost per Conversion, and add a summary with formatting.")

    spend_file = st.file_uploader("Upload Aggregated Spend Data by Channel and Creative", type="xlsx")
    conversions_file = st.file_uploader("Upload Channel and Creative Conversions Aggregation", type="xlsx")
    
    if spend_file and conversions_file:
        spend_df, conversions_df = load_data(spend_file, conversions_file)
        
        formatted_df = clean_and_merge(spend_df, conversions_df)
        
        st.subheader("Formatted Data with Totals and Cost per Conversion")
        st.write(formatted_df.style.format({
            "Spend": "${:,.0f}",
            "Conversions": "{:,.0f}",
            "Cost per Conversion": "${:,.2f}"
        }))

        excel_data = download_excel_with_formatting(formatted_df, sheet_name='Formatted Data')
        st.download_button(
            label="Download Formatted Data as Excel",
            data=excel_data,
            file_name="formatted_channel_creative_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
