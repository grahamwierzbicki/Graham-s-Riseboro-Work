import pandas as pd
import requests

# 1. Use the optimized public resource endpoint for the 311 dataset
url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

# Add a limit to grab just 10 rows from the API directly
params = {"$limit": 10}

# Fake a browser user-agent so the firewall doesn't block you
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

try:
    # 2. Send the request with headers and limit params
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    # 3. Parse JSON data
    json_data = response.json()

    # The resource endpoint always returns a clean list of rows
    df = pd.DataFrame(json_data)

    # 4. Display the results
    print(f"Total columns found: {len(df.columns)}")
    print("\n--- Displaying the first 10 rows ---")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)

    print(df.head(10))

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching data from the API: {e}")
except Exception as e:
    print(f"An error occurred while processing the data: {e}")