pip install -U kaleido

import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.title("Actual vs Predicted Values (interactive + SVG download)")

uploaded_file = st.file_uploader("Upload the pareto_alldecomp_matrix.csv file", type=["csv"])
if uploaded_file is None:
    st.info("Please upload a CSV with columns: ds, solID, dep_var, depVarHat")
else:
    df = pd.read_csv(uploaded_file)
    df['ds'] = pd.to_datetime(df['ds'])  # ensure datetime

    solID_list = df['solID'].unique()
    selected_solID = st.selectbox("Select Model Number (solID):", solID_list)

    filtered_df = df[df['solID'] == selected_solID].copy()
    melted_df = filtered_df.melt(id_vars=['ds'], value_vars=['dep_var', 'depVarHat'],
                                 var_name='Type', value_name='Value')
    melted_df['Type'] = melted_df['Type'].replace({'dep_var': 'Actual', 'depVarHat': 'Predicted'})

    plot_title = f"Actual vs Predicted for Model {selected_solID}"

    # Create interactive Plotly figure with markers and hover template
    fig = px.line(
        melted_df,
        x='ds',
        y='Value',
        color='Type',
        title=plot_title,
        markers=True,
        labels={'ds': 'Date', 'Value': 'Values', 'Type': 'Legend'}
    )

    # show both lines and markers, custom hover to show date and value clearly
    fig.update_traces(mode='lines+markers',
                      hovertemplate='<b>%{fullData.name}</b><br>Date: %{x|%Y-%m-%d}<br>Value: %{y}<extra></extra>')

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Values",
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend_title_text="",
        margin=dict(l=40, r=20, t=60, b=40)
    )

    # add a range slider to make exploring long series easier
    fig.update_xaxes(rangeslider_visible=True)

    # Display interactive plot
    st.plotly_chart(fig, use_container_width=True)

    # Prepare file names
    safe_title = plot_title.replace(" ", "_").replace("/", "_")
    svg_filename = f"{safe_title}.svg"
    png_filename = f"{safe_title}.png"

    # Try to produce SVG using Kaleido. Provide helpful message if not available.
    try:
        # fig.to_image returns bytes
        svg_bytes = fig.to_image(format="svg")
        # also produce PNG bytes as backup (optional)
        png_bytes = fig.to_image(format="png", width=1200, height=600)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download SVG (vector)",
                data=svg_bytes,
                file_name=svg_filename,
                mime="image/svg+xml"
            )
        with col2:
            st.download_button(
                label="Download PNG (raster)",
                data=png_bytes,
                file_name=png_filename,
                mime="image/png"
            )

    except Exception as e:
        st.warning(
            "SVG export failed. If you want SVG download, install Kaleido in your environment:\n\n"
            "`pip install -U kaleido`\n\n"
            f"Error: {e}"
        )
        # Fallback: let user download JSON of the figure so they can export locally
        fig_json = fig.to_json().encode("utf-8")
        st.download_button(
            "Download plot JSON (fallback) — open in Plotly to export",
            data=fig_json,
            file_name=f"{safe_title}.json",
            mime="application/json"
        )
