import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Streamlit App Title
st.title("📊 Actual vs Predicted Values")

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload the pareto_alldecomp_matrix.csv file", type=["csv"])

if uploaded_file is not None:
    # --- Data Loading and Preprocessing ---
    
    # Load the dataset
    df = pd.read_csv(uploaded_file)
    # Ensure ds column is datetime
    df['ds'] = pd.to_datetime(df['ds'])  

    # --- User Input ---
    
    # Get unique solID values for the dropdown
    solID_list = df['solID'].unique()
    selected_solID = st.selectbox("Select Model Number (solID):", solID_list)

    # Filter data for the selected solID
    filtered_df = df[df['solID'] == selected_solID]

    # Reshape data for Plotly (long format) and rename legend values
    melted_df = filtered_df.melt(id_vars=['ds'], value_vars=['dep_var', 'depVarHat'],
                                 var_name='Type', value_name='Value')
    # Rename for clearer legend labels
    melted_df['Type'] = melted_df['Type'].replace({'dep_var': 'Actual', 'depVarHat': 'Predicted'})

    # --- Plot Generation (Plotly Express) ---
    
    plot_title = f"Actual vs Predicted for Model {selected_solID}"
    fig = px.line(melted_df, x='ds', y='Value', color='Type',
                  labels={'ds': 'Date', 'Value': 'Values', 'Type': 'Legend'},
                  title=plot_title, markers=True)

    # Update layout for better visualization
    fig.update_layout(xaxis_title="Date", yaxis_title="Values",
                      xaxis_tickangle=-45)

    # Display the plot in the Streamlit app
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Interactive Plot Download (HTML) ---
    
    st.markdown("### Download Options")
    
    # 1. Convert the Plotly figure to an interactive HTML string.
    #    'include_plotlyjs="require"' embeds the necessary JS for full local interactivity (fixing the color issue).
    html_bytes = fig.to_html(
        full_html=True, 
        include_plotlyjs='require'
    ).encode('utf-8')
    
    # 2. Define the download file name
    file_name_html = f"{plot_title}.html".replace(" ", "_")
    
    # 3. Provide the download button for the interactive HTML
    st.download_button(
        label="Download Interactive Plot (.html)", 
        data=html_bytes, 
        file_name=file_name_html, 
        mime="text/html"
    )

    st.caption("The HTML file preserves interactivity (hover, zoom) and can be opened in any web browser.")
