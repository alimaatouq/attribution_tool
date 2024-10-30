import streamlit as st
import pandas as pd

# Streamlit app
st.title("Hyperparameters Generator")

# Use the uploaded file from session state if available
if st.session_state["uploaded_file"] is None:
    uploaded_file = st.file_uploader("Upload your Processed Data Excel file", type=["xlsx"])
    if uploaded_file:
        st.session_state["uploaded_file"] = uploaded_file
else:
    st.success("Using previously uploaded file.")

# Access the uploaded file from session state
uploaded_file = st.session_state["uploaded_file"]

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write(df.head())  # Example to display data

if uploaded_file:
    try:
        # Read Excel file
        data = pd.read_excel(uploaded_file)

        # Extract relevant spend variable names (columns containing 'Spend')
        spend_variables = [col for col in data.columns if "Spend" in col]

        # Define hyperparameter ranges
        alpha_range = "c(0.5,3)"
        gamma_range = "c(0.15,1)"
        theta_range = "c(0.01, 0.9)"

        # Build hyperparameters list
        hyperparameters = "hyperparameters <- list(\n"
        lines = []

        for var in spend_variables:
            lines.append(f"  {var}_alphas = {alpha_range},")
            lines.append(f"  {var}_gammas = {gamma_range},")
            lines.append(f"  {var}_thetas = {theta_range},")

        # Combine all lines into a single string
        hyperparameters += "\n".join(lines).rstrip(",")  # Remove trailing comma
        hyperparameters += "\n)"

        # Display the generated code block
        st.code(hyperparameters, language='r')

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload an Excel file to proceed.")
