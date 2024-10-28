import streamlit as st

st.set_page_config(page_title="Path Editor", layout="wide")

def double_backslashes(path):
    path = path.replace('\\', '\\\\')
    path = path.replace('/', '\\\\')
    return path

st.title("Path Editor - Double Backslashes")
st.write("Paste your folder path below:")

user_input = st.text_input("Enter the path:")

if user_input:
    edited_path = double_backslashes(user_input)
    st.write("**Edited Path:**")
    st.code(edited_path, language="text")
