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

if __name__ == "__main__":
    main()
