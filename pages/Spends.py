import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Shared utility functions
def consolidate_columns(df, by_channel_only=False):
    columns = df.columns
    filtered_columns = [col for col in columns if "spend" in col.lower()]
    
    consolidated_columns = []
    seen_columns = set()
    ordered_unique_columns = []
    
    for col in filtered_columns:
        if by_channel_only:
            new_col = re.sub(r'([_-]\d+)', '', col)
        else:
            new_col = re.sub(r'([_-]\d+|_Spend|^\d+_)', '', col, flags=re.IGNORECASE)
        consolidated_columns.append(new_col)
        if new_col not in seen_columns:
            ordered_unique_columns.append(new_col)
            seen_columns.add(new_col)
    
    consolidated_df = pd.DataFrame({
        'Original Column Name': filtered_columns,
        'Consolidated Column Name': consolidated_columns
    })
    
    unique_columns_df = pd.DataFrame({'Consolidated Column Names': ordered_unique_columns})
    return consolidated_df, unique_columns_df

def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

# Tab 1: By Channel Only
def channel_tab(df):
    st.subheader("Aggregated Spend Data by Channel")
    
    consolidated_df, unique_columns_df = consolidate_columns(df, by_channel_only=True)
    
    with st.expander("🔍 View Column Consolidation Mapping"):
        st.write(consolidated_df)
    
    # Aggregate spend by channel
    spend_data = []
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        match = re.match(r'([A-Za-z]+)', consolidated_name)
        if match:
            channel = match.group(1)
            matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            spend_sum = df[matching_columns].sum(axis=1).sum()
            spend_data.append({'Channel': channel, 'Spend': spend_sum})
    
    spend_df = pd.DataFrame(spend_data).groupby('Channel', as_index=False).sum()
    
    # Add total row
    total_spend = spend_df['Spend'].sum()
    display_df = pd.concat([spend_df, pd.DataFrame([{'Channel': 'Total', 'Spend': total_spend}])], ignore_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Channels", len(spend_df))
    with col2:
        st.metric("Total Spend", f"${total_spend:,.2f}")
    
    st.dataframe(display_df.style.format({'Spend': '${:,.2f}'}))
    
    st.download_button(
        label="📥 Download Channel Spend Data",
        data=download_excel(spend_df, sheet_name='Channel Spend'),
        file_name="channel_spend.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Tab 2: By Channel and Creative
def creative_tab(df):
    st.subheader("Spend Data by Channel and Creative")
    
    consolidated_df, unique_columns_df = consolidate_columns(df)
    
    with st.expander("🔍 View Column Consolidation Mapping"):
        st.write(consolidated_df)
    
    # Aggregate spend by channel and creative
    spend_data = []
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        match = re.match(r'([A-Za-z]+)_(.*)', consolidated_name)
        if match:
            channel = match.group(1)
            creative = match.group(2) if match.group(2) else "General"
            creative = re.sub(r'\d+', '', creative)
            
            matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+|_Spend|^\d+_)', '', col, flags=re.IGNORECASE) == consolidated_name]
            spend_sum = df[matching_columns].sum(axis=1).sum()
            spend_data.append({'Channel': channel, 'Creative': creative, 'Spend': spend_sum})
    
    spend_df = pd.DataFrame(spend_data).groupby(['Channel', 'Creative'], as_index=False).sum()
    
    # Add total row
    total_spend = spend_df['Spend'].sum()
    display_df = pd.concat([spend_df, pd.DataFrame([{'Channel': 'Total', 'Creative': '', 'Spend': total_spend}])], ignore_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Unique Channel-Creative Pairs", len(spend_df))
    with col2:
        st.metric("Total Spend", f"${total_spend:,.2f}")
    
    st.dataframe(display_df.style.format({'Spend': '${:,.2f}'}))
    
    st.download_button(
        label="📥 Download Channel-Creative Spend Data",
        data=download_excel(spend_df, sheet_name='Channel-Creative Spend'),
        file_name="channel_creative_spend.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Main app
def main():
    st.title("Marketing Spend Analysis Dashboard")
    st.write("Analyze your marketing spend by channel and creative type.")
    
    uploaded_file = st.file_uploader("📤 Upload your raw marketing data (Excel)", type=["xlsx"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("File successfully loaded!")
            
            tab1, tab2 = st.tabs(["By Channel", "By Channel & Creative"])
            
            with tab1:
                channel_tab(df)
                
            with tab2:
                creative_tab(df)
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    else:
        st.info("Please upload an Excel file to begin analysis")

if __name__ == "__main__":
    main()
