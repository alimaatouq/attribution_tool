def main():
    st.title("Website Visits Aggregation by Channel")
    st.write("Upload a CSV file, filter by model, and aggregate website visits by channel.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Load and display data
        df = load_data(uploaded_file)
        st.write("Data Preview:", df.head())

        # Model (solID) selection
        models = df['solID'].unique()
        selected_model = st.selectbox("Select Model (solID)", options=models)

        # Filter data by selected model
        filtered_df = filter_by_model(df, selected_model)
        st.write(f"Data for Model {selected_model}:", filtered_df)

        # Aggregate website visits by channel, including the Total row
        channel_visits_df_with_total = aggregate_website_visits(filtered_df)
        st.subheader("Aggregated Website Visits by Channel with Total")
        st.write(channel_visits_df_with_total)

        # Exclude the Total row for the downloadable file
        channel_visits_df_without_total = channel_visits_df_with_total[channel_visits_df_with_total['Channel'] != 'Total']

        # Download aggregated data as Excel, without the Total row
        excel_data = download_excel(channel_visits_df_without_total, sheet_name='Channel Visits')
        st.download_button(
            label="Download Channel Visits as Excel (without Total)",
            data=excel_data,
            file_name="channel_visits_aggregation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
