import streamlit as st
import pandas as pd
from io import BytesIO

def load_data(file):
    return pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)

def calculate_cpv(spend_df, visits_df, by_creative=False):
    merge_cols = ['Channel'] if not by_creative else ['Channel', 'Creative']
    
    # Standardize column names and merge
    merged = pd.merge(
        spend_df.rename(columns={'Visits': 'Spend'} if 'Visits' in spend_df.columns else {}),
        visits_df,
        on=merge_cols,
        how='outer'
    ).fillna(0)
    
    # Calculate CPV
    merged['CPV'] = merged.apply(
        lambda r: round(r['Spend']/r['Visits'], 2) if r['Visits'] > 0 else 0, 
        axis=1
    )
    
    # Add totals
    if by_creative:
        # Channel totals
        channel_totals = merged.groupby('Channel').agg({
            'Spend': 'sum',
            'Visits': 'sum'
        }).reset_index()
        channel_totals['CPV'] = channel_totals.apply(
            lambda r: round(r['Spend']/r['Visits'], 2) if r['Visits'] > 0 else 0,
            axis=1
        )
        channel_totals['Creative'] = 'Channel Total'
        
        # Grand total
        grand_total = pd.DataFrame([{
            'Channel': 'TOTAL',
            'Creative': '',
            'Spend': merged['Spend'].sum(),
            'Visits': merged['Visits'].sum(),
            'CPV': round(merged['Spend'].sum()/merged['Visits'].sum(), 2) if merged['Visits'].sum() > 0 else 0
        }])
        
        return pd.concat([merged, channel_totals, grand_total], ignore_index=True)
    else:
        # Just add grand total
        total = pd.DataFrame([{
            'Channel': 'TOTAL',
            'Spend': merged['Spend'].sum(),
            'Visits': merged['Visits'].sum(),
            'CPV': round(merged['Spend'].sum()/merged['Visits'].sum(), 2) if merged['Visits'].sum() > 0 else 0
        }])
        return pd.concat([merged, total], ignore_index=True)

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        # Add formatting for currency
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Format currency columns
        money_fmt = workbook.add_format({'num_format': '$#,##0.00'})
        if 'Spend' in df.columns:
            worksheet.set_column('C:C', None, money_fmt)
        if 'CPV' in df.columns:
            cpv_col = df.columns.get_loc('CPV')  # Get column index
            worksheet.set_column(cpv_col, cpv_col, None, money_fmt)
        
        # Format total rows
        total_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFF2CC'})
        if 'Channel' in df.columns:
            for row_num, value in enumerate(df['Channel']):
                if value == 'TOTAL':
                    worksheet.set_row(row_num + 1, None, total_fmt)
    
    output.seek(0)
    return output

def main():
    st.title("Cost Per Visit Analysis")
    
    tab1, tab2 = st.tabs(["By Channel", "By Channel & Creative"])
    
    with tab1:
        st.subheader("CPV by Channel")
        st.info("Upload your channel-level spend and visits data")
        
        col1, col2 = st.columns(2)
        with col1:
            spend_file = st.file_uploader("Spend Data", type=["csv", "xlsx"], key="spend_channel")
        with col2:
            visits_file = st.file_uploader("Visits Data", type=["csv", "xlsx"], key="visits_channel")
        
        if spend_file and visits_file:
            spend_df = load_data(spend_file)
            visits_df = load_data(visits_file)
            
            result = calculate_cpv(spend_df, visits_df, by_creative=False)
            st.dataframe(result.style.format({
                'Spend': '${:,.0f}',
                'Visits': '{:,.0f}',
                'CPV': '${:,.2f}'
            }))
            
            # Download button
            excel_data = download_excel(result, sheet_name='CPV by Channel')
            st.download_button(
                label="📥 Download CPV by Channel",
                data=excel_data,
                file_name="cpv_by_channel.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    
    with tab2:
        st.subheader("CPV by Channel & Creative")
        st.info("Upload your channel-creative spend and visits data")
        
        col1, col2 = st.columns(2)
        with col1:
            spend_file = st.file_uploader("Spend Data", type=["csv", "xlsx"], key="spend_creative")
        with col2:
            visits_file = st.file_uploader("Visits Data", type=["csv", "xlsx"], key="visits_creative")
        
        if spend_file and visits_file:
            spend_df = load_data(spend_file)
            visits_df = load_data(visits_file)
            
            result = calculate_cpv(spend_df, visits_df, by_creative=True)
            st.dataframe(result.style.format({
                'Spend': '${:,.0f}',
                'Visits': '{:,.0f}',
                'CPV': '${:,.2f}'
            }))
            
            # Download button
            excel_data = download_excel(result, sheet_name='CPV by Channel-Creative')
            st.download_button(
                label="📥 Download CPV by Channel-Creative",
                data=excel_data,
                file_name="cpv_by_channel_creative.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

if __name__ == "__main__":
    main()
