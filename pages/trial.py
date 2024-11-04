import streamlit as st
import pandas as pd
import re
from io import BytesIO

# (Other functions remain the same)

def create_final_output_table(spend_df):
    final_df = spend_df.copy()
    final_df['Spend'] = final_df['Spend'].apply(lambda x: f"${x:,.0f}")
    final_df = final_df[['Channel', 'Spend']]
    return final_df

def main():
    st.title("Channel Spend Aggregation App")
    st.write("Upload an Excel file to consolidate similar column names.")

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        filter_option = st.selectbox("Select Variable Type to Consolidate", 
                                     options=["All Variables", "Spend Variables", "Impression Variables"])

        consolidated_df, unique_columns_df = consolidate_columns(df, filter_option)

        st.subheader("Column Consolidation Mapping")
        st.write(consolidated_df)

        st.subheader("Ordered Consolidated Column Names")
        st.write(unique_columns_df)

        if filter_option == "Spend Variables":
            spend_df = aggregate_spend_by_channel(df, consolidated_df)

            st.subheader("Aggregated Spend Data by Channel")
            st.write(spend_df)

            final_output_df = create_final_output_table(spend_df)
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
