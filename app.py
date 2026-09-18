import streamlit as st
import requests
import pandas as pd

# Basic layout settings
st.set_page_config(page_title="Nobel Prize Trends", page_icon="🏅", layout="wide")

st.title("🏅 Nobel Prize Data & Trends")
st.subheader("Group Assignment: From Data to App")

# Section 1: Target Audience & Context
with st.expander("📌 Project Context: Target Audience & Question", expanded=True):
    st.markdown("""
    * **Target Audience:** High school students, educators, and history enthusiasts.
    * **Why it matters:** Tracking Nobel Prize distributions over time illustrates how scientific research and global recognition have evolved over the last century.
    * **Research Question:** How has the distribution of Nobel Laureates evolved across time and categories?
    """)

# Sidebar controls
st.sidebar.header("Interactive Filters")

categories = {
    "All Categories": "all",
    "Physics": "phy",
    "Chemistry": "che",
    "Physiology or Medicine": "med",
    "Literature": "lit",
    "Peace": "pea",
    "Economic Sciences": "eco"
}

selected_category_name = st.sidebar.selectbox(
    "Choose a Nobel Prize Category:",
    options=list(categories.keys())
)

selected_code = categories[selected_category_name]

# Helper function to fetch data directly from the official Nobel Prize API
@st.cache_data(ttl=3600)
def fetch_nobel_data(category_code):
    if category_code == "all":
        url = "https://api.nobelprize.org/2.1/nobelPrizes?limit=1000"
    else:
        url = f"https://api.nobelprize.org/2.1/nobelPrizes?nobelPrizeCategory={category_code}&limit=500"
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("nobelPrizes", [])
    except requests.exceptions.RequestException:
        return None

prizes_data = fetch_nobel_data(selected_code)

# Error handling
if prizes_data is None:
    st.error("⚠️ API Unavailable: Unable to fetch data from the [Nobel Prize API](https://www.nobelprize.org/about/developer-zone-2/). Please check your internet connection or try again later.")
elif len(prizes_data) == 0:
    st.warning("⚠️ No Data Found: The API returned an empty dataset for this selection.")
else:
    # Extract records cleanly
    records = []
    for prize in prizes_data:
        year = int(prize.get("nobelPrizeYear", 0))
        decade = (year // 10) * 10
        category_name = prize.get("category", {}).get("en", "Unknown Category")
        
        laureates = prize.get("laureates", [])
        
        if laureates:
            for laureate in laureates:
                name = laureate.get("knownName", {}).get("en") or laureate.get("orgName", {}).get("en") or "Unknown Winner"
                records.append({
                    "Year": year,
                    "Decade": decade,
                    "Category": category_name,
                    "Winner": name
                })
        else:
            records.append({
                "Year": year,
                "Decade": decade,
                "Category": category_name,
                "Winner": "Not Awarded"
            })

    # Create main DataFrame
    df = pd.DataFrame(records)

    # Filter out unawarded entries for clean counts
    df_winners = df[df["Winner"] != "Not Awarded"]

    # Section 3: Visualizations
    st.markdown(f"### 📊 Analysis for: **{selected_category_name}**")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Winners by Decade (Chronological)")
        # Aggregate and sort decades numerically
        decade_counts = df_winners.groupby("Decade").size().reset_index(name="Total Winners")
        decade_counts = decade_counts.sort_values(by="Decade", ascending=True)
        decade_counts["Decade Label"] = decade_counts["Decade"].astype(str) + "s"
        
        st.bar_chart(data=decade_counts, x="Decade Label", y="Total Winners", use_container_width=True)

    with col2:
        st.subheader("2. Winners Spread Across Categories")
        # Category breakdown chart
        category_counts = df_winners.groupby("Category").size().reset_index(name="Total Winners")
        category_counts = category_counts.sort_values(by="Total Winners", ascending=False)
        
        st.bar_chart(data=category_counts, x="Category", y="Total Winners", use_container_width=True)

    # Line Chart: Year-by-Year Timeline Progression
    st.subheader("📈 Timeline: Winner Volume Over Time (Year-by-Year)")
    yearly_counts = df_winners.groupby("Year").size().reset_index(name="Winners")
    yearly_counts = yearly_counts.sort_values(by="Year", ascending=True)

    st.line_chart(data=yearly_counts, x="Year", y="Winners", use_container_width=True)

    # Section 4: Explanation & Limitations
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        st.info("""
        **💡 What these visualizations show:**  
        - **Decade & Line Charts:** Show historical progression. Notice the increase in winners sharing prizes in modern decades, along with drops during World War I and World War II.
        - **Category Distribution:** Displays the total recipient counts. Economic Sciences has fewer total laureates because it was added later in 1969.
        """)

    with exp_col2:
        st.warning("""
        **⚠️ Data Limitations:**  
        - World Wars (1914–1918 and 1939–1945) caused Nobel Prizes to be canceled in some years, resulting in temporary zeroes in timeline data.
        - The official [Nobel Prize API](https://www.nobelprize.org/about/developer-zone-2/) caps single request sizes; parameters are set to retrieve all available historical prizes.
        """)

    # Section 5: Inspect Cleaned Data Table
    with st.expander("🔍 View Raw Cleaned Data"):
        st.dataframe(df, use_container_width=True)
