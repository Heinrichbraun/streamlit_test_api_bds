import requests

def fetch_nobel_prizes(year=None, category=None, limit=5):
    """
    Fetches Nobel Prize data from the public v2.1 API.
    
    Categories: 'phy' (Physics), 'che' (Chemistry), 'med' (Medicine),
                 'lit' (Literature), 'pea' (Peace), 'eco' (Economics)
    """
    base_url = "https://api.nobelprize.org/2.1/nobelPrizes"
    
    # Build query parameters
    params = {
        "limit": limit
    }
    if year:
        params["nobelPrizeYear"] = year
    if category:
        params["nobelPrizeCategory"] = category

    try:
        response = requests.get(base_url, params=params)
        
        # Raise an exception if the HTTP request returned an error status code
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        return data.get("nobelPrizes", [])

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return []

if __name__ == "__main__":
    # Example: Fetch Physics prizes from 2023
    prizes = fetch_nobel_prizes(year=2023, category="phy")
    
    for prize in prizes:
        year = prize.get("nobelPrizeYear")
        category_name = prize.get("category", {}).get("en")
        print(f"--- {year} Nobel Prize in {category_name} ---")
        
        for laureate in prize.get("laureates", []):
            name = laureate.get("knownName", {}).get("en") or laureate.get("orgName", {}).get("en")
            motivation = laureate.get("motivation", {}).get("en")
            print(f"Winner: {name}")
            print(f"Motivation: {motivation}\n")