import streamlit as st
import requests
import pandas as pd

# Basic layout settings
st.set_page_config(page_title="Nobel Prize Trends", page_icon="🏅", layout="wide")

st.title("🏅 Nobel Prize Data & Trends")
st.subheader("Group Assignment: From Data to App")

# Section 1: Target Audience & Issue
with st.expander("📌 Project Context: Target Audience & Question", expanded=True):
    st.markdown("""
    * **Target Audience:** High school students, educators, and history enthusiasts.
    * **Why it matters:** Tracking Nobel Prize distributions over time illustrates how scientific research and global recognition have evolved over the last century.
    * **Research Question:** How has the distribution of Nobel Laureates evolved across time and categories?
    """)

# Sidebar control
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

# Fetch Nobel data directly from API v2.1
@st.cache_data(ttl=3600)
def fetch_nobel_data():
    # Fetching up to 1000 prize entries covers all historical awards across categories
    url = "https://api.nobelprize.org/2.1/nobelPrizes?limit=1000"
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

prizes_data = fetch_nobel_data()

# Handle network or data errors
if prizes_data is None:
    st.error("⚠️ API Unavailable: Unable to fetch data from the [Nobel Prize API](https://www.nobelprize.org/about/developer-zone-2/).")
elif len(prizes_data) == 0:
    st.warning("⚠️ No Data Found: The API returned no results.")
else:
    # Process API payload into clean records
    records = []
    for prize in prizes_data:
        year = int(prize.get("nobelPrizeYear", 0))
        decade = (year // 10) * 10
        category_name = prize.get("category", {}).get("en", "Unknown")
        category_code = prize.get("category", {}).get("key", "")
        
        laureates = prize.get("laureates", [])
        
        if laureates:
            for laureate in laureates:
                name = laureate.get("knownName", {}).get("en") or laureate.get("orgName", {}).get("en") or "Unknown"
                records.append({
                    "Year": year,
                    "Decade": decade,
                    "Category": category_name,
                    "Category_Code": category_code,
                    "Winner": name
                })

    # Create main DataFrame
    df = pd.DataFrame(records)

    # Sort entire dataset chronologically
    df = df.sort_values(by="Year", ascending=True)

    # Filter by user category selection if specific category chosen
    if selected_code != "all":
        df_filtered = df[df["Category_Code"] == selected_code]
    else:
        df_filtered = df.copy()

    # Section 3: Visualizations
    st.markdown(f"### 📊 Analysis for: **{selected_category_name}**")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Winner Distribution by Decade")
        # Aggregate by decade
        decade_counts = df_filtered.groupby("Decade").size().reset_index(name="Total Winners")
        # Sort chronologically
        decade_counts = decade_counts.sort_values(by="Decade", ascending=True)
        decade_counts["Decade Label"] = decade_counts["Decade"].astype(str) + "s"
        
        # Bar chart for decade counts
        st.bar_chart(data=decade_counts, x="Decade Label", y="Total Winners", use_container_width=True)

    with col2:
        st.subheader("2. Total Spread Across Categories")
        # Histogram showing distribution across categories
        category_counts = df.groupby("Category").size().reset_index(name="Total Winners")
        category_counts = category_counts.sort_values(by="Total Winners", ascending=False)
        
        st.bar_chart(data=category_counts, x="Category", y="Total Winners", use_container_width=True)

    # Line Chart: Changes Over Time
    st.subheader("📈 Timeline: Change in Winner Volume Over Time (Year-by-Year)")
    yearly_counts = df_filtered.groupby("Year").size().reset_index(name="Winners")
    yearly_counts = yearly_counts.sort_values(by="Year", ascending=True)

    # Line chart showing timeline progression
    st.line_chart(data=yearly_counts, x="Year", y="Winners", use_container_width=True)

    # Section 4: Explanation & Limitations
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        st.info("""
        **💡 What these visualizations show:**  
        - **Decade & Line Charts:** Highlight how the number of individual winners increased in the modern era as joint prize-sharing became standard. Notice dips during World Wars I and II.
        - **Category Distribution Histogram:** Compares the total volume of laureates across categories. Economic Sciences has fewer total winners because it was introduced later (1969).
        """)

    with exp_col2:
        st.warning("""
        **⚠️ Data Limitations:**  
        - Nobel Prizes were paused in certain years during World Wars (1914–1918 and 1939–1945), causing zero values in timeline charts.
        - The API returns data up to current records; minor updates or spelling variations in historical records can affect grouping.
        """)

    # Section 5: Raw Cleaned Data
    with st.expander("🔍 Inspect Raw Cleaned Data"):
        st.dataframe(df_filtered, use_container_width=True)
