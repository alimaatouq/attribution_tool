import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
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
    
    # Save the figure using Matplotlib
    file_name = f"{plot_title}.png".replace(" ", "_")
    img_bytes = io.BytesIO()
    plt.figure(figsize=(10, 5))
    for label, data in melted_df.groupby("Type"):
        plt.plot(data["ds"], data["Value"], marker='o', label=label)
    plt.xlabel("Date")
    plt.ylabel("Values")
    plt.title(plot_title)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(img_bytes, format="png")
    img_bytes.seek(0)
    
    # Provide download button
    st.download_button(label="Download Plot", 
                       data=img_bytes, 
                       file_name=file_name, 
                       mime="image/png")
