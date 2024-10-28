import streamlit as st

st.set_page_config(
    page_title="R Path Editor",
    layout='wide'
)

def double_backslashes(path):
    # Handle both backslashes and forward slashes
    path = path.replace('\\', '\\\\')  # Double backslashes
    path = path.replace('/', '\\\\')   # Replace forward slashes with double backslashes
    return path

# Streamlit UI
st.title("Path Editor - Double Backslashes")
st.write("Paste your folder path below:")

# User input for the folder path
user_input = st.text_input("Enter the path:")

# Process and display the modified path
if user_input:
    edited_path = double_backslashes(user_input)
    st.write("**Edited Path:**")
    st.code(edited_path, language="text")
