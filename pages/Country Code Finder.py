import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape the country codes
def scrape_country_codes():
    url = "https://github.com/vacanza/holidays"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    heading = soup.find("h2", string="Available Countries")

    if not heading:
        st.error("Could not find 'Available Countries' section.")
        return pd.DataFrame()

    table = heading.find_next("table")
    if not table:
        st.error("Table not found after 'Available Countries' heading.")
        return pd.DataFrame()

    # Extract data from the table
    rows = table.find_all("tr")
    countries = []
    codes = []

    for row in rows[1:]:
        columns = row.find_all("td")
        if len(columns) >= 2:
            country = columns[0].get_text(strip=True)
            code = columns[1].get_text(strip=True)
            countries.append(country)
            codes.append(code)

    # Create a DataFrame
    return pd.DataFrame({"Country": countries, "Code": codes})

# Page Configuration
st.set_page_config(page_title="Country Code Finder", layout="centered")

# Title and Description
st.title("🌍 Country Code Finder")
st.write("This app dynamically fetches the ISO 3166-1 alpha-2 country codes. Enter a country name to filter the results.")

# Scrape the data
with st.spinner("Fetching country codes..."):
    df = scrape_country_codes()

# Check if the DataFrame is empty
if df.empty:
    st.warning("No data available. Please try again later.")
else:
    # Search Input
    query = st.text_input("🔍 Enter Country Name", "").strip().lower()

    # Filter the DataFrame based on user input
    if query:
        filtered_df = df[df["Country"].str.lower().str.contains(query)]
    else:
        filtered_df = df

    # Display the filtered DataFrame
    st.write(f"Showing {len(filtered_df)} result(s):")
    st.dataframe(filtered_df)

    # Optionally, add a download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Results as CSV",
        data=csv,
        file_name="filtered_country_codes.csv",
        mime="text/csv",
    )
