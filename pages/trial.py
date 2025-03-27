import streamlit as st
import pandas as pd
import re
from io import BytesIO

def standardize_column_name(col_name):
    """
    Generic function to standardize column names by:
    1. Removing trailing numbers (with optional underscore/dash)
    2. Removing '_Spend' suffix
    3. Converting to title case
    """
    # Remove _Spend suffix if present
    col_name = re.sub(r'_Spend$', '', col_name, flags=re.IGNORECASE)
    
    # Remove any trailing numbers with optional prefix (_, -)
    col_name = re.sub(r'([_-]?\d+)$', '', col_name)
    
    # Remove any numbers in the middle of words (e.g., Banner1 → Banner)
    col_name = re.sub(r'(\D)\d+(\D)', r'\1\2', col_name)
    col_name = re.sub(r'(\D)\d+$', r'\1', col_name)
    col_name = re.sub(r'^\d+(\D)', r'\1', col_name)
    
    # Replace underscores with spaces and title case
    col_name = col_name.replace('_', ' ').title()
    
    return col_name.strip()

def aggregate_website_visits(df):
    channel_creative_data = {}
    
    for col in df.columns:
        if 'spend' not in col.lower() or col == 'KPI_Website_Sessions':
            continue
            
        # Standardize the column name
        standardized = standardize_column_name(col)
        
        # Split into channel and creative parts
        parts = standardized.split()
        if len(parts) >= 2:
            channel = parts[0]
            creative = ' '.join(parts[1:])
            key = (channel, creative)
            
            if key not in channel_creative_data:
                channel_creative_data[key] = 0
            
            column_sum = pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
            channel_creative_data[key] += column_sum
    
    # Convert to DataFrame
    channel_creative_df = pd.DataFrame(
        [{'Channel': channel, 'Creative': creative, 'Visits': int(round(visits))}
         for (channel, creative), visits in channel_creative_data.items()]
    )
    
    # Add total row
    total_visits = channel_creative_df['Visits'].sum()
    total_row = pd.DataFrame([{'Channel': 'Total', 'Creative': '', 'Visits': total_visits}])
    channel_creative_df = pd.concat([channel_creative_df, total_row], ignore_index=True)
    
    return channel_creative_df

def main():
    st.title("Website Visits Aggregator")
    
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Show raw column names for debugging
        with st.expander("Show original columns"):
            st.write(list(df.columns))
        
        # Process and show results
        result_df = aggregate_website_visits(df)
        st.dataframe(result_df)
        
        # Show standardized names
        with st.expander("Show standardized column mapping"):
            st.write({
                col: standardize_column_name(col) 
                for col in df.columns 
                if 'spend' in col.lower()
            })

if __name__ == "__main__":
    main()
