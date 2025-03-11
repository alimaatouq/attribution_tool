import streamlit as st
import pandas as pd
import plotly.express as px

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

    # Reshape data for Plotly (long format)
    melted_df = filtered_df.melt(id_vars=['ds'], value_vars=['dep_var', 'depVarHat'],
                                 var_name='Type', value_name='Value')

    # Create a Plotly scatter plot with markers
    fig = px.scatter(melted_df, x='ds', y='Value', color='Type',
                     labels={'ds': 'Date', 'Value': 'Values', 'Type': 'Legend'},
                     title=f"Actual vs Predicted for Model {selected_solID}")

    # Update layout for better visualization
    fig.update_traces(marker=dict(size=8))
    fig.update_layout(xaxis_title="Date", yaxis_title="Values",
                      xaxis_tickangle=-45)

    # Display the plot
    st.plotly_chart(fig)
