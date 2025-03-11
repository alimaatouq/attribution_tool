import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Helper function to consolidate columns
def consolidate_columns(df):
    filtered_columns = [col for col in df.columns if "spend" in col.lower()]
    
    consolidated_columns = []
    seen_columns = set()
    ordered_unique_columns = []
    
    for col in filtered_columns:
        new_col = re.sub(r'([_-]\d+)', '', col)
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

# Function to aggregate visits data
def aggregate_visits(df, consolidated_df):
    visits_data = []
    
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        match = re.match(r'([A-Za-z]+)_(.*)', consolidated_name)
        if match:
            channel = match.group(1)
            creative = match.group(2)
            
            # Standardize creative names by removing numeric identifiers
            creative = re.sub(r'\d+', '', creative)
            
            matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            visits_sum = df[matching_columns].sum(axis=1).sum()
            visits_data.append({'Channel': channel, 'Creative': creative, 'Visits': visits_sum})
    
    visits_df = pd.DataFrame(visits_data).groupby(['Channel', 'Creative'], as_index=False).sum()
    return visits_df

# Function to summarize channel visits
def summarize_channel_visits(visits_df):
    channel_summary = visits_df.groupby('Channel')['Visits'].sum().reset_index()
    total_visits = channel_summary['Visits'].sum()
    channel_summary['Percentage Contribution'] = ((channel_summary['Visits'] / total_visits) * 100).round(0).astype(int)
    total_row = pd.DataFrame([{'Channel': 'Total', 'Visits': total_visits, 'Percentage Contribution': 100}])
    channel_summary = pd.concat([channel_summary, total_row], ignore_index=True)
    return channel_summary

# Function to create the final output table
def create_final_output_table(visits_df, channel_summary_df):
    final_df = visits_df.copy()
    final_df['Channel - Contribution'] = final_df['Channel']
    
    for _, row in channel_summary_df.iterrows():
        channel = row['Channel']
        if channel != 'Total':
            contribution_percentage = int(row['Percentage Contribution'])
            final_df.loc[final_df['Channel'] == channel, 'Channel - Contribution'] = f"{channel} - {contribution_percentage}%"
    
    final_df['Visits'] = final_df['Visits'].astype(int)
    final_df = final_df[['Channel - Contribution', 'Creative', 'Visits']]
    return final_df

# Function to create a downloadable Excel file
def download_excel(df, sheet_name='Sheet1'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

# Main function for single-page app
def main():
    st.title("Aggregation App for the Dependent Variable by Channel")
    st.write("Upload the pareto_alldecomp_matrix CSV or Excel file to consolidate and analyze visits data for a selected model.")

    uploaded_file = st.file_uploader("Choose pareto_alldecomp_matrix Excel or CSV file", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)

        if 'solID' in df.columns:
            unique_sol_ids = df['solID'].unique()
            selected_model = st.selectbox("Select Model (solID) to Analyze", options=unique_sol_ids)
            df = df[df['solID'] == selected_model]
        else:
            st.warning("The uploaded file does not contain a 'solID' column.")

        consolidated_df, unique_columns_df = consolidate_columns(df)
        visits_df = aggregate_visits(df, consolidated_df)
        channel_summary_df = summarize_channel_visits(visits_df)
        final_output_df = create_final_output_table(visits_df, channel_summary_df)

        st.subheader("Final Output Table")
        st.write(final_output_df)

        excel_data_final_output = download_excel(final_output_df, sheet_name='Final Output')
        st.download_button(
            label="Download Final Output Table as Excel",
            data=excel_data_final_output,
            file_name="final_output_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
