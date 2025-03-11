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
    
    # Check if necessary columns exist
    required_columns = {'solID', 'rsq_train', 'decomp.rssd', 'dep_var', 'depVarHat'}
    if not required_columns.issubset(df.columns):
        st.error(f"Missing required columns: {required_columns - set(df.columns)}")
    else:
        # Load the model performance data
        model_performance = df.groupby('solID').agg(
            rsq_train_avg=('rsq_train', 'mean'),
            decomp_rssd_avg=('decomp.rssd', 'mean')
        ).reset_index()
        
        # Find the best model: highest rsq_train, breaking ties with lowest decomp_rssd
        best_model = model_performance.sort_values(by=['rsq_train_avg', 'decomp_rssd_avg'], 
                                                   ascending=[False, True]).iloc[0]['solID']
        
        # User input for selecting solID
        selected_solID = st.text_input("Enter Model Number (solID) or leave blank to use the best model:", "")
        
        if not selected_solID:
            selected_solID = best_model
            st.write(f"Automatically selecting the best model: {selected_solID}")
        
        # Filter data for the selected solID
        filtered_df = df[df['solID'] == selected_solID]
        
        # Reshape data for Plotly (long format) and rename legend values
        melted_df = filtered_df.melt(id_vars=['ds'], value_vars=['dep_var', 'depVarHat'],
                                     var_name='Type', value_name='Value')
        melted_df['Type'] = melted_df['Type'].replace({'dep_var': 'Actual', 'depVarHat': 'Predicted'})
        
        # Create a Plotly line chart with markers
        fig = px.line(melted_df, x='ds', y='Value', color='Type',
                      labels={'ds': 'Date', 'Value': 'Values', 'Type': 'Legend'},
                      title=f"Actual vs Predicted for Model {selected_solID}", markers=True)
        
        # Update layout for better visualization
        fig.update_layout(xaxis_title="Date", yaxis_title="Values",
                          xaxis_tickangle=-45)
        
        # Display the plot
        st.plotly_chart(fig)
