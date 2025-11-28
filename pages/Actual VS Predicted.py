import streamlit as st
import pandas as pd
import plotly.express as px
import io

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

    # Reshape data for Plotly (long format) and rename legend values
    melted_df = filtered_df.melt(id_vars=['ds'], value_vars=['dep_var', 'depVarHat'],
                                 var_name='Type', value_name='Value')
    melted_df['Type'] = melted_df['Type'].replace({'dep_var': 'Actual', 'depVarHat': 'Predicted'})

    # Create a Plotly line chart with markers
    plot_title = f"Actual vs Predicted for Model {selected_solID}"
    fig = px.line(melted_df, x='ds', y='Value', color='Type',
                  labels={'ds': 'Date', 'Value': 'Values', 'Type': 'Legend'},
                  title=plot_title, markers=True)

    # Update layout for better visualization
    fig.update_layout(xaxis_title="Date", yaxis_title="Values",
                      xaxis_tickangle=-45)

    # Display the plot
    st.plotly_chart(fig)
    
    # --- Interactive Plot Download Section ---
    
    # 1. Convert the Plotly figure to an interactive HTML string
    html_bytes = fig.to_html(full_html=True, include_plotlyjs='cdn').encode('utf-8')
    
    # 2. Define the download file name
    file_name = f"{plot_title}.html".replace(" ", "_")
    
    # 3. Provide the download button for the interactive HTML
    st.download_button(
        label="Download Interactive Plot (HTML)", 
        data=html_bytes, 
        file_name=file_name, 
        mime="text/html"
    )

    st.info("The downloaded HTML file will open in a web browser and retain the interactive hover features.")
