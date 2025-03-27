import streamlit as st
import pandas as pd

# Main app configuration
st.set_page_config(page_title="Robyn Data Processor", layout="wide")

# Initialize session state for uploaded file
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# Main app title
st.title("Robyn Data Processing Toolkit")

# File uploader - shared across all tabs
uploaded_file = st.file_uploader("📤 Upload your Processed Data Excel file", type=["xlsx"])
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["📅 Date Range Finder", "💰 Paid Media Vars", "⚙️ Hyperparameters"])

with tab1:
    st.header("Date Range Finder")
    if st.session_state.uploaded_file:
        try:
            data = pd.read_excel(st.session_state.uploaded_file)
            
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                data = data.dropna(subset=['Date'])
                
                window_start = data['Date'].min().strftime('%Y-%m-%d')
                window_end = data['Date'].max().strftime('%Y-%m-%d')

                st.code(f'window_start = "{window_start}"\nwindow_end = "{window_end}"', language='r')
            else:
                st.error("❌ The uploaded file does not contain a 'Date' column.")
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        st.info("ℹ️ Please upload an Excel file to proceed.")

with tab2:
    st.header("Paid Media Variables Extractor")
    if st.session_state.uploaded_file:
        try:
            df = pd.read_excel(st.session_state.uploaded_file)
            
            spend_columns = [col for col in df.columns if 'Spend' in col]
            impression_columns = [col for col in df.columns if 'Impressions' in col]

            spend_output = 'paid_media_spends = c(\n    "' + '",\n    "'.join(spend_columns) + '")'
            impression_output = 'paid_media_vars = c(\n    "' + '",\n    "'.join(impression_columns) + '")'

            st.code(spend_output, language='r')
            st.code(impression_output, language='r')
            
            # Show column summary
            with st.expander("📊 Column Summary"):
                st.write(f"Found {len(spend_columns)} spend columns and {len(impression_columns)} impression columns")
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        st.info("ℹ️ Please upload an Excel file to proceed.")

with tab3:
    st.header("Hyperparameters Generator")
    if st.session_state.uploaded_file:
        try:
            df = pd.read_excel(st.session_state.uploaded_file)
            spend_variables = [col for col in df.columns if "Spend" in col]

            # Configuration options
            with st.expander("⚙️ Hyperparameter Ranges"):
                alpha_min, alpha_max = st.slider("Alpha range", 0.1, 5.0, (0.5, 3.0), 0.1)
                gamma_min, gamma_max = st.slider("Gamma range", 0.01, 2.0, (0.15, 1.0), 0.01)
                theta_min, theta_max = st.slider("Theta range", 0.0, 1.0, (0.01, 0.9), 0.01)

            alpha_range = f"c({alpha_min},{alpha_max})"
            gamma_range = f"c({gamma_min},{gamma_max})"
            theta_range = f"c({theta_min},{theta_max})"

            hyperparameters = "hyperparameters <- list(\n"
            lines = []
            for var in spend_variables:
                lines.append(f"  {var}_alphas = {alpha_range},")
                lines.append(f"  {var}_gammas = {gamma_range},")
                lines.append(f"  {var}_thetas = {theta_range},")

            hyperparameters += "\n".join(lines).rstrip(",") + "\n)"
            
            st.code(hyperparameters, language='r')
            
            # Show quick copy button
            st.download_button(
                label="📋 Copy Hyperparameters",
                data=hyperparameters,
                file_name="hyperparameters.R",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        st.info("ℹ️ Please upload an Excel file to proceed.")

# Add some styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 4px 4px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)
