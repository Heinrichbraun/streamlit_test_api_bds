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

# Helper function to fetch data directly from the official Nobel Prize API.
# NOTE: this paginates with offset/limit instead of trusting a single large
# "limit" value. Some public APIs silently cap how many records they return
# per request even if you ask for more (e.g. capping at 25 or 100 despite a
# limit=1000 param) -- looping until a page comes back short protects us from
# quietly ending up with a tiny, misleading slice of the data.
@st.cache_data(ttl=3600)
def fetch_nobel_data(category_code):
    base_url = "https://api.nobelprize.org/2.1/nobelPrizes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }

    page_size = 100
    offset = 0
    max_records = 2000  # safety cap so a bug can't loop forever
    all_prizes = []

    while offset < max_records:
        params = {"limit": page_size, "offset": offset}
        if category_code != "all":
            params["nobelPrizeCategory"] = category_code

        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            batch = response.json().get("nobelPrizes", [])
        except requests.exceptions.RequestException:
            # If even the very first request fails, there is no data at all.
            # If a later page fails, keep whatever we already gathered.
            return None if offset == 0 else all_prizes

        if not batch:
            break

        all_prizes.extend(batch)

        if len(batch) < page_size:
            break  # last page was shorter than requested -> no more data

        offset += page_size

    return all_prizes

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
        # FIX: the API returns the year under "awardYear", not "nobelPrizeYear".
        # "nobelPrizeYear" is only the query-parameter name used for filtering,
        # it is never a key in the response JSON, so the old code always fell
        # back to 0 here and grouped every record into decade "0s".
        year = int(prize.get("awardYear", 0))
        # Align decade grouping to the same 1901-1910, 1911-1920, ... grid
        # used by the "Quick Jump to a Decade" preset, instead of a plain
        # year // 10 * 10 grouping (which would split e.g. 1971-1980 into
        # two separate "1970s"/"1980s" buckets and look inconsistent with
        # the preset the user just picked).
        decade = 1901 + ((year - 1901) // 10) * 10 if year >= 1901 else (year // 10) * 10
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

    # Base pool of real winners (excludes "Not Awarded" placeholder rows and
    # any record we couldn't assign a valid year to)
    df_winners_all = df[(df["Winner"] != "Not Awarded") & (df["Year"] > 0)]

    if df_winners_all.empty:
        st.warning("⚠️ No laureate data available to filter or chart for this selection.")
    else:
        # --- New filter: Time Period ------------------------------------
        st.sidebar.subheader("Refine Results")

        min_year = int(df_winners_all["Year"].min())
        max_year = int(df_winners_all["Year"].max())

        if min_year == max_year:
            selected_year_range = (min_year, max_year)
            st.sidebar.caption(f"Only one award year ({min_year}) available for this selection.")
        else:
            # Quick-jump decade presets aligned to the standard Nobel decade
            # grid (1901-1910, 1911-1920, ...), clipped to whatever years are
            # actually available for the currently selected category (e.g.
            # Economic Sciences only goes back to the late 1960s).
            presets = []
            grid_start = 1901
            start = min_year - ((min_year - grid_start) % 10)
            while start <= max_year:
                end = start + 9
                clipped_start = max(start, min_year)
                clipped_end = min(end, max_year)
                if clipped_start <= clipped_end:
                    presets.append((f"{clipped_start}–{clipped_end}", (clipped_start, clipped_end)))
                start += 10

            preset_map = dict(presets)
            # Keyed per category so switching categories doesn't leave a
            # stale year range that falls outside the new category's bounds.
            slider_key = f"year_range_{selected_code}"
            quick_key = f"quick_pick_{selected_code}"

            def apply_preset():
                picked = st.session_state[quick_key]
                if picked in preset_map:
                    st.session_state[slider_key] = preset_map[picked]

            st.sidebar.selectbox(
                "Quick Jump to a Decade",
                options=["Custom / All Years"] + [label for label, _ in presets],
                key=quick_key,
                on_change=apply_preset
            )

            if slider_key not in st.session_state:
                st.session_state[slider_key] = (min_year, max_year)

            selected_year_range = st.sidebar.slider(
                "Filter by Time Period (Award Year)",
                min_value=min_year,
                max_value=max_year,
                key=slider_key
            )

        df_winners = df_winners_all[
            (df_winners_all["Year"] >= selected_year_range[0]) &
            (df_winners_all["Year"] <= selected_year_range[1])
        ]
        # -----------------------------------------------------------------

        # Debug helper: lets you confirm whether the API actually returned the
        # full dataset or something suspiciously small.
        st.caption(f"Fetched {len(prizes_data)} prize record(s); {len(df_winners)} laureate entries match your current filters.")

        # Quick stat cards summarizing the current filtered selection
        if not df_winners.empty:
            stat1, stat2, stat3 = st.columns(3)

            with stat1:
                st.metric("Total Laureates", f"{len(df_winners):,}")

            with stat2:
                top_category = df_winners["Category"].value_counts().idxmax()
                st.metric("Top Category", top_category if selected_code == "all" else selected_category_name)

            with stat3:
                top_decade = df_winners["Decade"].value_counts().idxmax()
                st.metric("Most Awarded Decade", f"{int(top_decade)}–{int(top_decade) + 9}")

            # CSV download of exactly what's currently filtered/shown
            csv_bytes = df_winners.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download filtered data as CSV",
                data=csv_bytes,
                file_name=f"nobel_laureates_{selected_code}_{selected_year_range[0]}-{selected_year_range[1]}.csv",
                mime="text/csv"
            )

        # Section 3: Visualizations
        st.markdown(f"### 📊 Analysis for: **{selected_category_name}**")

        if df_winners.empty:
            st.warning("⚠️ No data matches the current Time Period filter. Try widening it in the sidebar.")
        elif selected_code == "all":
            # The category comparison chart only makes sense when we actually
            # have more than one category to compare -- which is only the case
            # in "All Categories" mode. Filtering to a single category first,
            # then charting "categories", would just draw one lonely bar.
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("1. Winners by Decade (Chronological)")
                decade_counts = df_winners.groupby("Decade").size().reset_index(name="Total Winners")
                decade_counts = decade_counts.sort_values(by="Decade", ascending=True)
                # Clip the displayed label to the data's actual bounds so the
                # final, partial decade reads e.g. "2021–2025" (matching the
                # Quick Jump preset) instead of a misleading "2021–2030".
                decade_counts["Decade Label"] = (
                    decade_counts["Decade"].clip(lower=min_year).astype(str)
                    + "–"
                    + (decade_counts["Decade"] + 9).clip(upper=max_year).astype(str)
                )
                st.bar_chart(data=decade_counts, x="Decade Label", y="Total Winners", use_container_width=True)

            with col2:
                st.subheader("2. Winners Spread Across Categories")
                category_counts = df_winners.groupby("Category").size().reset_index(name="Total Winners")
                category_counts = category_counts.sort_values(by="Total Winners", ascending=False)
                st.bar_chart(data=category_counts, x="Category", y="Total Winners", use_container_width=True)
                st.caption(f"Showing category totals for **{selected_year_range[0]}–{selected_year_range[1]}**.")
        else:
            st.subheader("1. Winners by Decade (Chronological)")
            decade_counts = df_winners.groupby("Decade").size().reset_index(name="Total Winners")
            decade_counts = decade_counts.sort_values(by="Decade", ascending=True)
            decade_counts["Decade Label"] = (
                decade_counts["Decade"].clip(lower=min_year).astype(str)
                + "–"
                + (decade_counts["Decade"] + 9).clip(upper=max_year).astype(str)
            )
            st.bar_chart(data=decade_counts, x="Decade Label", y="Total Winners", use_container_width=True)
            st.caption(
                f"Category comparison is hidden here because you've filtered to **{selected_category_name}** only "
                "— switch to 'All Categories' in the sidebar to compare across fields."
            )

        if not df_winners.empty:
            # Line Chart: Year-by-Year Timeline Progression
            st.subheader("📈 Timeline: Winner Volume Over Time (Year-by-Year)")
            yearly_counts = df_winners.groupby("Year").size().reset_index(name="Winners")
            yearly_counts = yearly_counts.sort_values(by="Year", ascending=True)
            st.line_chart(data=yearly_counts, x="Year", y="Winners", use_container_width=True)

            st.subheader("🏆 Repeat Winners")
            repeat_counts = df_winners["Winner"].value_counts()
            repeat_counts = repeat_counts[repeat_counts > 1].reset_index()
            repeat_counts.columns = ["Winner", "Prizes Won"]
            if repeat_counts.empty:
                st.info("No repeat winners in the current selection.")
            else:
                st.dataframe(repeat_counts, use_container_width=True, hide_index=True)
                st.caption("Laureates or organizations who won more than once within your current filters.")

        # Section 4: Explanation & Limitations
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            st.info("""
            **💡 What these visualizations show:**  
            - **Decade & Line Charts:** Show historical progression. Notice the increase in winners sharing prizes in modern decades, along with drops during World War I and World War II.
            - **Category Distribution:** Displays the total recipient counts. Economic Sciences has fewer total laureates because it was added later in 1969.
            - **Repeat Winners:** Highlights laureates or organizations awarded more than once within your current filters (e.g. Marie Curie, the ICRC).
            - **Time Period filter:** Narrow every chart above down to a specific award-year range.
            """)

        with exp_col2:
            st.warning("""
            **⚠️ Data Limitations:**  
            - World Wars (1914–1918 and 1939–1945) caused Nobel Prizes to be canceled in some years, resulting in temporary zeroes in timeline data.
            - The official [Nobel Prize API](https://www.nobelprize.org/about/developer-zone-2/) caps single request sizes; the app pages through results to retrieve all available historical prizes.
            - Repeat-winner stats only reflect whatever category/time filters are currently applied, not the full historical dataset.
            """)

        # Section 5: Inspect Cleaned Data Table
        with st.expander("🔍 View Raw Cleaned Data"):
            st.dataframe(df, use_container_width=True)
