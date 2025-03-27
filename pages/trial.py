import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Shared utility functions
def load_data(uploaded_file):
    return pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

def filter_by_model(df, selected_model):
    return df[df['solID'] == selected_model]

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

def format_currency(df, columns):
    return df.style.format({col: "${:,.2f}" for col in columns})

# Tab 1: Visits by Channel
def visits_by_channel_tab(df):
    st.subheader("Aggregated Website Visits by Channel")
    
    channel_data = {}
    for col in df.columns:
        if 'spend' not in col.lower() or col == 'KPI_Website_Sessions':
            continue
            
        channel = re.match(r'([A-Za-z]+)', col)
        if channel:
            channel_name = channel.group(1)
            if channel_name not in channel_data:
                channel_data[channel_name] = 0
            column_sum = pd.to_numeric(df[col], errors='coerce').sum()
            channel_data[channel_name] += column_sum
    
    channel_df = pd.DataFrame(list(channel_data.items()), columns=['Channel', 'Visits'])
    channel_df['Visits'] = channel_df['Visits'].round(0).astype(int)
    
    total_visits = channel_df['Visits'].sum()
    total_row = pd.DataFrame([{'Channel': 'Total', 'Visits': total_visits}])
    display_df = pd.concat([channel_df, total_row], ignore_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Channels", len(channel_df))
    with col2:
        st.metric("Total Visits", f"{total_visits:,}")
    
    st.dataframe(display_df)
    
    st.download_button(
        label="📥 Download Channel Visits",
        data=download_excel(channel_df),
        file_name="channel_visits.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Tab 2: Visits by Channel & Creative
def visits_by_creative_tab(df):
    st.subheader("Website Visits by Channel and Creative")
    
    channel_creative_data = {}
    for col in df.columns:
        if 'spend' not in col.lower() or col == 'KPI_Website_Sessions':
            continue
            
        match = re.match(r'([A-Za-z\s]+)_(.*?)(?:_\d+)?_Spend', col)
        if match:
            channel = match.group(1).strip().lower()
            creative = match.group(2).strip().lower()
            key = f"{channel}_{creative}"
            if key not in channel_creative_data:
                channel_creative_data[key] = 0
            column_sum = pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
            channel_creative_data[key] += column_sum
    
    visits_df = pd.DataFrame(
        [{'Channel': k.split('_')[0].title(), 'Creative': k.split('_')[1].title(), 'Visits': v} 
         for k, v in channel_creative_data.items()]
    )
    visits_df['Visits'] = visits_df['Visits'].round(0).astype(int)
    
    total_visits = visits_df['Visits'].sum()
    total_row = pd.DataFrame([{'Channel': 'Total', 'Creative': '', 'Visits': total_visits}])
    display_df = pd.concat([visits_df, total_row], ignore_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Unique Combinations", len(visits_df))
    with col2:
        st.metric("Total Visits", f"{total_visits:,}")
    
    st.dataframe(display_df)
    
    st.download_button(
        label="📥 Download Channel-Creative Visits",
        data=download_excel(visits_df),
        file_name="channel_creative_visits.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Tab 3: CPV by Channel
def cpv_by_channel_tab():
    st.subheader("Cost Per Visit by Channel")
    
    spend_file = st.file_uploader("Upload Channel Spend Data", type="xlsx", key="spend_channel")
    visits_file = st.file_uploader("Upload Channel Visits Data", type="xlsx", key="visits_channel")
    
    if spend_file and visits_file:
        spend_df = pd.read_excel(spend_file)
        visits_df = pd.read_excel(visits_file)
        
        merged_df = pd.merge(spend_df, visits_df, on="Channel", how="inner")
        merged_df['Spend'] = pd.to_numeric(merged_df['Spend'], errors='coerce').fillna(0)
        merged_df['Visits'] = pd.to_numeric(merged_df['Visits'], errors='coerce').fillna(0)
        
        merged_df['CPV'] = merged_df.apply(
            lambda row: round(row['Spend'] / row['Visits'], 2) if row['Visits'] > 0 else 0, axis=1
        )
        
        total_spend = merged_df['Spend'].sum()
        total_visits = merged_df['Visits'].sum()
        avg_cpv = round(total_spend / total_visits, 2) if total_visits > 0 else 0
        
        total_row = pd.DataFrame([{
            'Channel': 'TOTAL',
            'Spend': total_spend,
            'Visits': total_visits,
            'CPV': avg_cpv
        }])
        
        display_df = pd.concat([merged_df, total_row], ignore_index=True)
        
        st.dataframe(format_currency(display_df, ['Spend', 'CPV']))
        
        st.download_button(
            label="📥 Download CPV by Channel",
            data=download_excel(display_df, 'CPV by Channel'),
            file_name="cpv_by_channel.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# Tab 4: CPV by Channel & Creative
def cpv_by_creative_tab():
    st.subheader("Cost Per Visit by Channel and Creative")
    
    spend_file = st.file_uploader("Upload Channel-Creative Spend Data", type="xlsx", key="spend_creative")
    visits_file = st.file_uploader("Upload Channel-Creative Visits Data", type="xlsx", key="visits_creative")
    
    if spend_file and visits_file:
        spend_df = pd.read_excel(spend_file)
        visits_df = pd.read_excel(visits_file)
        
        spend_df['Channel'] = spend_df['Channel'].str.lower().str.strip()
        spend_df['Creative'] = spend_df['Creative'].str.lower().str.strip()
        visits_df['Channel'] = visits_df['Channel'].str.lower().str.strip()
        visits_df['Creative'] = visits_df['Creative'].str.lower().str.strip()
        
        merged_df = pd.merge(spend_df, visits_df, on=["Channel", "Creative"], how="outer")
        merged_df['Spend'] = pd.to_numeric(merged_df['Spend'], errors='coerce').fillna(0)
        merged_df['Visits'] = pd.to_numeric(merged_df['Visits'], errors='coerce').fillna(0)
        
        merged_df['CPV'] = merged_df.apply(
            lambda row: round(row['Spend'] / row['Visits'], 2) if row['Visits'] > 0 else 0, axis=1
        )
        
        # Add channel totals
        total_rows = []
        for channel in merged_df['Channel'].unique():
            channel_data = merged_df[merged_df['Channel'] == channel]
            total_spend = channel_data['Spend'].sum()
            total_visits = channel_data['Visits'].sum()
            avg_cpv = round(total_spend / total_visits, 2) if total_visits > 0 else 0
            total_rows.append({
                'Channel': channel.title(), 
                'Creative': 'Total', 
                'Spend': total_spend, 
                'Visits': total_visits, 
                'CPV': avg_cpv
            })
        
        # Add overall total
        overall_spend = merged_df['Spend'].sum()
        overall_visits = merged_df['Visits'].sum()
        overall_cpv = round(overall_spend / overall_visits, 2) if overall_visits > 0 else 0
        total_rows.append({
            'Channel': 'Total', 
            'Creative': '-', 
            'Spend': overall_spend, 
            'Visits': overall_visits, 
            'CPV': overall_cpv
        })
        
        display_df = pd.concat([merged_df, pd.DataFrame(total_rows)], ignore_index=True)
        
        st.dataframe(format_currency(display_df, ['Spend', 'CPV']))
        
        st.download_button(
            label="📥 Download CPV by Channel-Creative",
            data=download_excel(display_df, 'CPV by Channel-Creative'),
            file_name="cpv_by_channel_creative.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# Main app
def main():
    st.title("Website Visits Analysis Dashboard")
    
    # File upload and model selection (shared across first two tabs)
    uploaded_file = st.file_uploader("📤 Upload your marketing data (CSV/Excel)", type=["csv", "xlsx"])
    selected_model = None
    
    if uploaded_file:
        df = load_data(uploaded_file)
        models = df['solID'].unique()
        selected_model = st.selectbox("Select Model (solID)", options=models)
        filtered_df = filter_by_model(df, selected_model)
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Visits by Channel", 
            "🎨 Visits by Creative", 
            "💰 CPV by Channel", 
            "🖌️ CPV by Creative"
        ])
        
        with tab1:
            visits_by_channel_tab(filtered_df)
            
        with tab2:
            visits_by_creative_tab(filtered_df)
            
        with tab3:
            cpv_by_channel_tab()
            
        with tab4:
            cpv_by_creative_tab()
    else:
        st.info("Please upload a data file to begin analysis")

if __name__ == "__main__":
    main()
