import streamlit as st
import requests
import pandas as pd

# Set up the basic page layout and title
st.set_page_config(page_title="Nobel Prize Trends", page_icon="🏅", layout="wide")

st.title("🏅 Nobel Prize Data & Trends")
st.subheader("Group Assignment: From Data to App")

# Section 1: Explain the target audience, why it matters, and the question asked
with st.expander("📌 Project Context: Target Audience & Question", expanded=True):
    st.markdown("""
    * **Target Audience:** High school students, educators, and science history enthusiasts.
    * **Why it matters:** Understanding how Nobel Prizes are awarded across different decades highlights scientific trends over time.
    * **Research Question:** How has the distribution of Nobel Prizes evolved across decades for a specific category?
    """)

# Sidebar control to let the user pick a category
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

# Function to fetch data from the API safely with browser headers
@st.cache_data(ttl=3600)
def fetch_nobel_data(category_code):
    url = f"https://api.nobelprize.org/2.1/nobelPrizes?nobelPrizeCategory={category_code}&limit=500"
    
    # Headers make the API treat the Python script like a normal web browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("nobelPrizes", [])
    except requests.exceptions.RequestException:
        return None

# Fetch data for the category selected by the user
prizes_data = fetch_nobel_data(selected_code)

# Handle API errors or empty data gracefully
if prizes_data is None:
    st.error("⚠️ API Unavailable: Unable to fetch data from the Nobel Prize API. Please check your internet connection or try again later.")
elif len(prizes_data) == 0:
    st.warning("⚠️ No Data Found: The API returned an empty dataset for this selection.")
else:
    # Format raw API data into clean rows for analysis
    records = []
    for item in prizes_data:
        year = int(item.get("nobelPrizeYear", 0))
        # Calculate decade (e.g., 1984 becomes 1980s)
        decade = f"{(year // 10) * 10}s"
        
        records.append({
            "Year": year,
            "Decade": decade,
            "Prize_Amount": item.get("prizeAmount", 0)
        })

    # Create a pandas table/dataframe
    df = pd.DataFrame(records)

    # Section 3: Visualization
    st.markdown(f"### 📊 Total Nobel Prizes Awarded in **{selected_category_name}** by Decade")
    
    # Count how many prizes were given per decade
    decade_counts = df.groupby("Decade").size().reset_index(name="Total Prizes")
    decade_counts = decade_counts.sort_values(by="Decade")

    # Display an interactive bar chart in Streamlit
    st.bar_chart(data=decade_counts, x="Decade", y="Total Prizes", use_container_width=True)

    # Section 4: Explanation & Limitations
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **💡 What this visualization shows:**  
        This chart tracks the number of Nobel Prizes awarded in the selected category across different decades. Drops in prizes during certain decades (such as the 1940s) typically reflect major historical events like World War II.
        """)

    with col2:
        st.warning("""
        **⚠️ Data Limitations:**  
        - The API returns data capped at a limit per query, requiring multiple network calls to gather full historical archives.
        - Nobel Prizes were cancelled or postponed in certain years, leaving natural data gaps in the timeline.
        """)

    # Option for the user to inspect raw tabular data
    with st.expander("🔍 View Raw API Data"):
        st.dataframe(df, use_container_width=True)
