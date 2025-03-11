import streamlit as st
import pandas as pd
from io import BytesIO

def load_data(spend_file, conversions_file):
    spend_df = pd.read_excel(spend_file)
    conversions_df = pd.read_excel(conversions_file)
    return spend_df, conversions_df

def clean_and_merge(spend_df, conversions_df):
    merged_df = pd.merge(spend_df, conversions_df, on="Channel", how="inner")

    merged_df['Spend'] = pd.to_numeric(merged_df['Spend'], errors='coerce').fillna(0)
    merged_df['Conversions'] = pd.to_numeric(merged_df['Conversions'], errors='coerce').fillna(0)

    merged_df['Cost per Conversion'] = merged_df.apply(
        lambda row: round(row['Spend'] / row['Conversions'], 2) if row['Conversions'] > 0 else 0, axis=1
    )

    total_spend = merged_df['Spend'].sum()
    total_conversions = merged_df['Conversions'].sum()
    avg_cost_per_conversion = round(total_spend / total_conversions, 2) if total_conversions > 0 else 0

    total_row = pd.DataFrame([{
        'Channel': 'TOTAL',
        'Spend': total_spend,
        'Conversions': total_conversions,
        'Cost per Conversion': avg_cost_per_conversion
    }])

    merged_df = pd.concat([merged_df, total_row], ignore_index=True)
    merged_df_no_total = merged_df[merged_df['Channel'] != 'TOTAL']
    total_row_df = merged_df[merged_df['Channel'] == 'TOTAL']
    
    merged_df_sorted = pd.concat([merged_df_no_total.sort_values(by="Cost per Conversion"), total_row_df], ignore_index=True)

    return merged_df_sorted

def download_excel(df, sheet_name='Merged Data'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def main():
    st.title("Channel Spend and Conversions Summary with Cost per Conversion")
    st.write("Upload the Spend and Conversions Excel files to merge them based on the channel, calculate Cost per Conversion, and sort by Cost per Conversion.")

    spend_file = st.file_uploader("Upload Aggregated Spend Data by Channel", type="xlsx")
    conversions_file = st.file_uploader("Upload Channel Conversions Aggregation", type="xlsx")
    
    if spend_file and conversions_file:
        spend_df, conversions_df = load_data(spend_file, conversions_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Spend Data (First 5 Rows)")
            st.write(spend_df.head())
        
        with col2:
            st.subheader("Conversions Data (First 5 Rows)")
            st.write(conversions_df.head())

        merged_df = clean_and_merge(spend_df, conversions_df)
        
        st.subheader("Merged Data with Total Spend, Conversions, and Average Cost per Conversion")
        st.write(merged_df.style.format({
            "Spend": "${:,.0f}",
            "Conversions": "{:,.0f}",
            "Cost per Conversion": "${:,.2f}"
        }))

        excel_data = download_excel(merged_df, sheet_name='Merged Data')
        st.download_button(
            label="Download Merged Data as Excel",
            data=excel_data,
            file_name="merged_channel_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
