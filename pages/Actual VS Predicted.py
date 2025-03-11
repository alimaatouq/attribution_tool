import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
def load_data():
    file_path = "pareto_alldecomp_matrix.csv"  # Update if the path changes
    df = pd.read_csv(file_path)
    df['ds'] = pd.to_datetime(df['ds'])  # Ensure ds column is datetime
    return df

df = load_data()

# Streamlit App Title
st.title("Actual vs Predicted Values")

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
