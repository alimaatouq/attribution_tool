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

    # Create a Plotly scatter plot
    fig = px.scatter(filtered_df, x='ds', y=['dep_var', 'depVarHat'],
                     labels={'ds': 'Date', 'value': 'Values'},
                     title=f"Actual vs Predicted for Model {selected_solID}",
                     markers=True)

    # Update layout for better visualization
    fig.update_traces(marker=dict(size=8))
    fig.update_layout(xaxis_title="Date", yaxis_title="Values",
                      legend_title="Legend", xaxis_tickangle=-45)

    # Display the plot
    st.plotly_chart(fig)
