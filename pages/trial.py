import streamlit as st
import pandas as pd
import re
from io import BytesIO

def load_data(uploaded_file):
    return pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

def filter_by_model(df, selected_model):
    return df[df['solID'] == selected_model]

def standardize_column_name(col_name):
    col_name = re.sub(r'_Spend$', '', col_name, flags=re.IGNORECASE)
    col_name = re.sub(r'([_-]?\d+)$', '', col_name)
    col_name = re.sub(r'(\D)\d+(\D)', r'\1\2', col_name)
    col_name = col_name.replace('_', ' ').title()
    return col_name.strip()

def aggregate_visits(df, by_channel_only=False):
    results = {}
    
    for col in df.columns:
        if 'spend' not in col.lower() or col == 'KPI_Website_Sessions':
            continue
            
        standardized = standardize_column_name(col)
        parts = standardized.split()
        
        if by_channel_only:
            key = parts[0]  # Just use channel name
        else:
            key = (parts[0], ' '.join(parts[1:])) if len(parts) >= 2 else (parts[0], 'General')
        
        if key not in results:
            results[key] = 0
            
        results[key] += pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
    
    return results

def create_visits_df(results, include_total=True):
    if isinstance(next(iter(results.keys())), tuple):
        # Channel-Creative view
        df = pd.DataFrame(
            [{'Channel': k[0], 'Creative': k[1], 'Visits': int(round(v))} 
             for k, v in results.items()]
        )
        if include_total:
            total = pd.DataFrame([{
                'Channel': 'Total', 
                'Creative': '', 
                'Visits': df['Visits'].sum()
            }])
            df = pd.concat([df, total], ignore_index=True)
    else:
        # Channel-only view
        df = pd.DataFrame(
            [{'Channel': k, 'Visits': int(round(v))} 
             for k, v in results.items()]
        )
        if include_total:
            total = pd.DataFrame([{
                'Channel': 'Total', 
                'Visits': df['Visits'].sum()
            }])
            df = pd.concat([df, total], ignore_index=True)
    
    return df

def main():
    st.set_page_config(page_title="Website Visits Analysis", layout="wide")
    st.title("Website Visits Analysis")
    
    uploaded_file = st.file_uploader("📤 Upload your marketing data", type=["csv", "xlsx"])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        models = df['solID'].unique()
        selected_model = st.selectbox("Select Model (solID)", options=models)
        filtered_df = filter_by_model(df, selected_model)
        
        tab1, tab2 = st.tabs(["By Channel", "By Channel & Creative"])
        
        with tab1:
            st.subheader("Aggregated Visits by Channel")
            channel_results = aggregate_visits(filtered_df, by_channel_only=True)
            channel_df = create_visits_df(channel_results)
            st.dataframe(channel_df)
            
        with tab2:
            st.subheader("Aggregated Visits by Channel & Creative")
            creative_results = aggregate_visits(filtered_df, by_channel_only=False)
            creative_df = create_visits_df(creative_results)
            st.dataframe(creative_df)

if __name__ == "__main__":
    main()
