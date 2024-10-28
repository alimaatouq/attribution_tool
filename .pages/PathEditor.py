import streamlit as st

def path_editor_page():
    st.title("Path Editor - Double Backslashes")
    st.write("Paste your folder path below:")

    user_input = st.text_input("Enter the path:")

    def double_backslashes(path):
        path = path.replace('\\', '\\\\')
        path = path.replace('/', '\\\\')
        return path

    if user_input:
        edited_path = double_backslashes(user_input)
        st.write("**Edited Path:**")
        st.code(edited_path, language="text")
