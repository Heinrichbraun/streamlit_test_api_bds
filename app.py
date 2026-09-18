import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Nobel Prize Trends", page_icon="🏅", layout="wide")

st.title("🏅 Nobel Prize Data & Trends")
st.subheader("Group Assignment: From Data to App")

# ---------------------------------------------------------
# 1. Target Audience & Issue
# ---------------------------------------------------------
with st.expander("📌 Project Context: Target Audience & Question", expanded=True):
    st.markdown("""
    * **Target Audience:** High school students, educators, and science enthusiasts interested in the history of scientific and societal achievements.
    * **Why it matters:** Understanding how Nobel Prizes have been awarded across different decades highlights trends in academic research and global peace efforts over time.
    * **Research Question:** How has the distribution of Nobel Prizes evolved across decades for a specific category?
    """)

# ---------------------------------------------------------
# API Helper Function with Caching
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_nobel_data(category_code):
    """
    Fetches Nobel Prize data from the public API for a given category.
    """
    url = f"https://api.nobelprize.org/2.1/nobelPrizes?nobelPrizeCategory={category_code}&limit=500"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("nobelPrizes", [])
    except requests.exceptions.RequestException:
        return None

# ---------------------------------------------------------
# 2. Interactive Controls
# ---------------------------------------------------------
st.sidebar.header("Interactive Filters")

categories = {
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

# ---------------------------------------------------------
# Data Fetching & Error Handling
# ---------------------------------------------------------
prizes_data = fetch_nobel_data(selected_code)

if prizes_data is None:
    st.error("⚠️ **API Unavailable:** Unable to fetch data from the Nobel Prize API. Please check your internet connection or try again later.")
elif len(prizes_data) == 0:
    st.warning("⚠️ **No Data Found:** The API returned an empty dataset for this selection.")
else:
    # Transform JSON into a DataFrame
    records = []
    for item in prizes_data:
        year = int(item.get("nobelPrizeYear", 0))
        # Compute decade
        decade = f"{(year // 10) * 10}s"
        
        laureates = item.get("laureates", [])
        num_laureates = len(laureates)
        
        records.append({
            "Year": year,
            "Decade": decade,
            "Laureate_Count": num_laureates,
            "Prize_Amount": item.get("prizeAmount", 0)
        })

    df = pd.DataFrame(records)

    # ---------------------------------------------------------
    # 3. Visualization
    # ---------------------------------------------------------
    st.markdown(f"### 📊 Total Nobel Prizes Awarded in **{selected_category_name}** by Decade")
    
    # Aggregate data by decade
    decade_counts = df.groupby("Decade").size().reset_index(name="Total Prizes")
    decade_counts = decade_counts.sort_values(by="Decade")

    # Interactive Streamlit Bar Chart
    st.bar_chart(data=decade_counts, x="Decade", y="Total Prizes", use_container_width=True)

    # ---------------------------------------------------------
    # 4. Explanation & Limitations
    # ---------------------------------------------------------
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **💡 What this visualization shows:**  
        This chart tracks the number of Nobel Prizes awarded in the selected category across different decades. Drops in prizes during certain decades (e.g., the 1940s) typically reflect global disruptions like WWII.
        """)

    with col2:
        st.warning("""
        **⚠️ Data Limitations:**  
        - The API limits returned results per query (capped at `limit=500`), meaning extremely old or recent records might require paginated API calls.
        - Nobel Prizes were not awarded in every category in every year (notably during World Wars), creating natural gaps in the dataset.
        """)

    # Show raw data view option
    with st.expander("🔍 View Raw API Data"):
        st.dataframe(df, use_container_width=True)
