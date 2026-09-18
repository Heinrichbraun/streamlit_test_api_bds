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
    * **Why it matters:** Seeing how Nobel Prize recipient numbers change across decades highlights global scientific collaboration and historical events.
    * **Research Question:** How has the total number of Nobel Laureates (winners) evolved by decade in a specific category?
    """)

# Sidebar control
st.sidebar.header("Interactive Filters")

# Map display names to official category codes used by API v2.1
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

# Fetch category data directly from API v2.1
@st.cache_data(ttl=3600)
def fetch_nobel_data(category_code):
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

# Handle network or data errors
if prizes_data is None:
    st.error("⚠️ API Unavailable: Unable to fetch data from the Nobel Prize API.")
elif len(prizes_data) == 0:
    st.warning("⚠️ No Data Found: The API returned no results for this category.")
else:
    # Extract records cleanly, capturing each laureate (winner)
    records = []
    for prize in prizes_data:
        year = int(prize.get("nobelPrizeYear", 0))
        decade = (year // 10) * 10  # Compute integer decade (e.g. 1980)
        
        laureates = prize.get("laureates", [])
        
        if laureates:
            for laureate in laureates:
                # Capture English name or organization name
                name = laureate.get("knownName", {}).get("en") or laureate.get("orgName", {}).get("en") or "Unknown"
                records.append({
                    "Year": year,
                    "Decade": decade,
                    "Winner": name
                })
        else:
            # Handle years where prize was not awarded or declined
            records.append({
                "Year": year,
                "Decade": decade,
                "Winner": "Not Awarded"
            })

    # Create a Pandas DataFrame
    df = pd.DataFrame(records)

    # Filter out "Not Awarded" years for accurate winner counts
    df_winners = df[df["Winner"] != "Not Awarded"]

    # Section 3: Corrected Visualization
    st.markdown(f"### 📊 Total Nobel Laureates (Winners) in **{selected_category_name}** by Decade")

    # Group by integer decade and count winners
    decade_counts = df_winners.groupby("Decade").size().reset_index(name="Total Winners")
    
    # Sort chronologically (e.g., 1900, 1910, 1920)
    decade_counts = decade_counts.sort_values(by="Decade")
    
    # Format decade names as text for clear X-axis labels
    decade_counts["Decade Label"] = decade_counts["Decade"].astype(str) + "s"

    # Display clean Streamlit bar chart
    st.bar_chart(data=decade_counts, x="Decade Label", y="Total Winners", use_container_width=True)

    # Section 4: Explanation & Limitations
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **💡 What this visualization shows:**  
        This chart shows the total number of individuals or organizations awarded a Nobel Prize per decade. Notice how joint awards (multiple winners sharing one prize) become much more common in scientific fields in recent decades.
        """)

    with col2:
        st.warning("""
        **⚠️ Data Limitations:**  
        - World Wars (1914–1918 and 1939–1945) caused several Nobel Prizes to be skipped entirely, creating temporary drops.
        - The `limit=500` API parameter fetches up to 500 prize records, which covers all historical prizes for any single category.
        """)

    # Display clean tabular data for verification
    with st.expander("🔍 Inspect Raw Cleaned Data"):
        st.dataframe(df, use_container_width=True)
