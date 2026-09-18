# 🏅 Nobel Prize Data & Trends

A Streamlit app that turns the [official Nobel Prize API](https://www.nobelprize.org/about/developer-zone-2/) into an interactive, explorable view of how Nobel laureates and prize categories have shifted over the past century.

Built for the **From Data to App** group assignment (Session 4 & 5).

## Target audience & why it matters

**Audience:** High school students, educators, and history enthusiasts.

Tracking Nobel Prize distributions over time shows how scientific research and global recognition have evolved — which fields have grown, which have stayed niche, and how world events (like the World Wars) show up directly in the data.

## Research question

**How has the distribution of Nobel Laureates evolved across time and categories?**

## Data source

- **API:** [Nobel Prize API v2.1](https://www.nobelprize.org/about/developer-zone-2/) — free, public, no API key required
- **Endpoint used:** `https://api.nobelprize.org/2.1/nobelPrizes`

## Features

- **Visualizations:**
  - Winners by decade (bar chart), grouped on the standard 1901–1910, 1911–1920, ... Nobel decade grid
  - Winners spread across categories (bar chart, shown when "All Categories" is selected)
  - Year-by-year timeline of winner volume (line chart)
- **Highlights:**
  - Quick stat cards (total laureates, top category, most awarded decade) for the current filter selection
  - Repeat winners table (laureates/organizations awarded more than once within the current filters)
- **Interactive controls:**
  - Filter by Nobel Prize category (Physics, Chemistry, Medicine, Literature, Peace, Economic Sciences, or all)
  - Filter by time period, either by dragging a year-range slider or using the **"Quick Jump to a Decade"** dropdown (1901–1910 through 2021–2025), which snaps the slider to that exact decade and can still be fine-tuned afterward
- **Export:** download the currently filtered data as a CSV
- **Explanations & limitations:** shown directly in the app under the charts
- **Graceful error handling:** the app shows a clear message if the API is unavailable or returns no data for the current filters, instead of crashing

## Known data limitations

- World Wars (1914–1918 and 1939–1945) caused Nobel Prizes to be canceled in some years, which shows up as gaps in the timeline.
- The official API paginates results; the app loops through pages automatically to retrieve the full historical dataset for the current filter selection rather than trusting a single request.
- Repeat-winner stats only reflect whatever category/time filters are currently applied, not the full historical dataset.
- Decade presets and labels are clipped to whichever years are actually available for the selected category (e.g. Economic Sciences was first awarded in 1969, so its earliest bucket reads "1969–1970" rather than a misleading "1961–1970").

## Running it locally

```bash
pip install -r requirements.txt
streamlit run nobel_app.py
```

## Live app

https://apptestapibds-pvmuytpc7dz5dup4vvxasq.streamlit.app/

## Repository

- Repository: https://github.com/Heinrichbraun/streamlit_test_api_bds


## AI tools used

Claude (Anthropic) was used to:
- Debug the original data-parsing logic against the real Nobel Prize API schema (the year field is `awardYear`, not `nobelPrizeYear` as originally written)
- Add pagination so the app reliably fetches the full dataset instead of relying on an unverified single-request `limit`
- Add the time-period filter and rework the category chart so it only renders when it's meaningful (i.e. when comparing across categories)
- Add the repeat-winners table, summary stat cards, and CSV export
- Add the "Quick Jump to a Decade" preset dropdown and align decade grouping/labels to the standard Nobel decade grid

## Notes

- No API key or credentials are required or stored anywhere in this repository.
