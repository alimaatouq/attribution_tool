import streamlit as st
import pandas as pd
from io import BytesIO

def load_data(spend_file, visits_file):
    # Load the first sheet in each uploaded Excel file
    spend_df = pd.read_excel(spend_file)  # Load first sheet by default
    visits_df = pd.read_excel(visits_file)  # Load first sheet by default
    return spend_df, visits_df

def merge_and_calculate(spend_df, visits_df):
    # Merge the two DataFrames on the "Channel" column
    merged_df = pd.merge(spend_df, visits_df, on="Channel", how="inner")

    # Calculate Cost per Visit
    merged_df['Cost per Visit'] = merged_df['Spend'] / merged_df['Visits']
    
    # Format Spend and Visits as integers and Cost per Visit as a float with 2 decimal places
    merged_df['Spend'] = merged_df['Spend'].astype(int)
    merged_df['Visits'] = merged_df['Visits'].astype(int)
    merged_df['Cost per Visit'] = merged_df['Cost per Visit'].round(2)
    
    return merged_df

def download_excel(df, sheet_name='Merged Data'):
    # Convert the DataFrame to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        writer.close()
    output.seek(0)
    return output

def main():
    st.title("Combine Spend and Visits Data by Channel")
    st.write("Upload the Spend and Visits Excel files to merge them based on the channel and calculate Cost per Visit.")

    # File uploaders for the two Excel files
    spend_file = st.file_uploader("Upload Aggregated Spend Data by Channel", type="xlsx")
    visits_file = st.file_uploader("Upload Channel Visits Aggregation", type="xlsx")
    
    if spend_file and visits_file:
        # Load the data from both files
        spend_df, visits_df = load_data(spend_file, visits_file)
        
        # Show previews of both DataFrames
        st.subheader("Spend Data")
        st.write(spend_df)
        
        st.subheader("Visits Data")
        st.write(visits_df)

        # Merge data and calculate Cost per Visit
        merged_df = merge_and_calculate(spend_df, visits_df)
        
        # Display the merged DataFrame with Cost per Visit
        st.subheader("Merged Data with Cost per Visit")
        st.write(merged_df)

        # Download button for the merged Excel file
        excel_data = download_excel(merged_df, sheet_name='Merged Data')
        st.download_button(
            label="Download Merged Data as Excel",
            data=excel_data,
            file_name="merged_channel_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
