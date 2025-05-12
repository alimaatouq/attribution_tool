import streamlit as st
import pandas as pd
import re

# Your data loading and transformation functions would be imported here
# from your_module import load_conversions, load_spends, load_preprocessed, merge_data

def kpi_summary_app():
    st.set_page_config(page_title="KPI Summary", layout="wide")
    st.title("Budget Optimization Summary")

    # File inputs
    conversions_file = st.file_uploader("Upload Conversions CSV", type="csv", key="conversions")
    spends_file = st.file_uploader("Upload Spends Excel", type="xlsx", key="spends")
    preprocessed_file = st.file_uploader("Upload Preprocessed CSV", type="csv", key="preprocessed")
    sol_id_to_filter = st.text_input("Enter solID to filter", value="4_722_10")

    if conversions_file and spends_file and preprocessed_file:
        conversions_df = load_conversions(conversions_file, sol_id_to_filter)
        spends_df = load_spends(spends_file)
        preprocessed_df = load_preprocessed(preprocessed_file)

        final_df = merge_data(conversions_df, spends_df, preprocessed_df)

        # Compute metrics
        final_df['New Response'] = final_df['Conversions'] * final_df['Response_Change']
        final_df['Budget Change'] = ((final_df['Sum_optmSpendUnit'] - final_df['Spend']) / final_df['Spend'])
        final_df['Absolute Budget Change'] = (final_df['Sum_optmSpendUnit'] - final_df['Spend']).round(1)

        # Compute overall KPIs
        total_new_response = final_df['New Response'].sum()
        total_old_response = final_df['Conversions'].sum()
        total_new_budget = final_df['Sum_optmSpendUnit'].sum()
        total_old_budget = final_df['Spend'].sum()

        response_change_kpi = ((total_new_response / total_old_response) - 1) * 100
        budget_change_kpi = ((total_new_budget - total_old_budget) / total_old_budget) * 100
        cpa_change = ((total_new_budget / total_new_response) / (total_old_budget / total_old_response) - 1) * 100

        # Format columns
        final_df = final_df.rename(columns={
            'Channel': 'channel',
            'Spend': 'old_budget',
            'Sum_optmSpendUnit': 'new_budget',
            'Conversions': 'old_response',
            'New Response': 'new_response',
            'Change': 'budget change',
            'Response_Change': 'resp change',
            'Absolute Budget Change': 'abs budg change'
        })

        final_df = final_df[[
            'channel', 'old_budget', 'new_budget', 'old_response', 'new_response',
            'budget change', 'resp change', 'abs budg change'
        ]]

        # Fill NaNs and format
        final_df['old_response'] = final_df['old_response'].fillna(0).map('{:,.0f}'.format)
        final_df['new_response'] = final_df['new_response'].fillna(0).map('{:,.0f}'.format)
        final_df['old_budget'] = final_df['old_budget'].map('${:,.0f}'.format)
        final_df['new_budget'] = final_df['new_budget'].map('${:,.0f}'.format)
        final_df['abs budg change'] = final_df['abs budg change'].map('${:,.0f}'.format)
        final_df['budget change'] = final_df['budget change'].map('{:.1%}'.format)
        final_df['resp change'] = final_df['resp change'].map('{:.3f}'.format)

        st.dataframe(final_df.style.format({
            "old_budget": "${:,.0f}",
            "new_budget": "${:,.0f}",
            "old_response": "{:,.0f}",
            "new_response": "{:,.0f}",
            "budget change": "{:.1%}",
            "resp change": "{:.3f}",
            "abs budg change": "${:,.0f}"
        }), use_container_width=True)

        # Show Overall KPIs
        st.markdown("### Overall KPIs")
        col1, col2, col3 = st.columns(3)
        col1.metric("Budget Change", f"{budget_change_kpi:.1f}%")
        col2.metric("Response Change", f"{response_change_kpi:.1f}%")
        col3.metric("CPA Change", f"{cpa_change:.1f}%")

    else:
        st.info("Please upload all required files to proceed.")

