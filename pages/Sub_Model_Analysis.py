import pandas as pd
import streamlit as st

# Load the uploaded file
uploaded_file = st.file_uploader("Upload your dataset", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file
    data = pd.read_csv(uploaded_file)

    # Display the data
    st.write("Uploaded Data:", data.head())

    # Submodel analysis - Aggregating 'rsq_train' by 'solID'
    submodel_analysis = data.groupby('solID').agg(
        rsq_train_avg=('rsq_train', 'mean'),  # You can also use 'max' if preferred
        rsq_train_max=('rsq_train', 'max'),   # Just in case you need both average and max
        # Add any other aggregations or columns you need
    ).reset_index()

    # Display the aggregated analysis
    st.write("Submodel Analysis with Aggregated rsq_train:", submodel_analysis)

    # Optionally visualize results
    st.bar_chart(submodel_analysis[['solID', 'rsq_train_avg']])

# Optional: Add logic to highlight cases with negative R² values
st.write("Models with Negative R² Values:")
negative_rsq = submodel_analysis[submodel_analysis['rsq_train_avg'] < 0]
st.write(negative_rsq)
