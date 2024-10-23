import streamlit as st

def double_backslashes(path):
    return path.replace('\\', '\\\\')

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

#edit footer
page_style= """
    <style>
    footer{
        visibility: visible;
        }
    footer:after{
        content: 'Developed by Ali Maatouk - Analytics @ Data Sciences';
        display:block;
        position:relative;
        color:#1e54e4;
    }
    </style>"""

st.markdown(page_style, unsafe_allow_html=True)
