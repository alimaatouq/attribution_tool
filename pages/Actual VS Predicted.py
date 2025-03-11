import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit App Title
st.title("Actual vs Predicted Values")

# File uploader
uploaded_file = st.file_uploader("Upload the pareto_alldecomp_matrix.csv file", type=["csv"])

if uploaded_file is not None:
    # Load the dataset
    df = pd.read_csv(uploaded_file)
    df['ds'] = pd.to_datetime(df['ds'])  # Ensure ds column is datetime

    # User input for selecting solID
    solID_list = df['solID'].unique()
    selected_solID = st.selectbox("Select Model Number (solID):", solID_list)

    # Filter data for the selected solID
    filtered_df = df[df['solID'] == selected_solID]

    # Plot the actual vs predicted values
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(filtered_df['ds'], filtered_df['dep_var'], label="Actual", marker='o')
    ax.plot(filtered_df['ds'], filtered_df['depVarHat'], label="Predicted", marker='x')
    ax.set_xlabel("Date")
    ax.set_ylabel("Values")
    ax.set_title(f"Actual vs Predicted for Model {selected_solID}")
    ax.legend()
    plt.xticks(rotation=45)

    # Display the plot
    st.pyplot(fig)
