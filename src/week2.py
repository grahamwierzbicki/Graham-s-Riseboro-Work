import os
import pandas as pd

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "WEEK 2 SOURCE OF TRUTH.xlsx")

def main():
    print(f"Loading data from {DATA_PATH}...")
    
    # Read the first sheet by default
    try:
        df = pd.read_excel(DATA_PATH)
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return
    
    print("\nColumns in dataset:", list(df.columns))
    
    # We expect 'source_property' and 'call_date' (standardized from week 1)
    if 'source_property' not in df.columns:
        print("\n'source_property' column not found! Check columns above.")
        return
        
    if 'call_date' not in df.columns:
        print("\n'call_date' column not found! Check columns above.")
        return

    # Convert call_date to datetime
    df['call_date'] = pd.to_datetime(df['call_date'], errors='coerce')

    # Filter for Rheingold (rheingold_gardens) and Gates Plaza (gates_plaza)
    properties = {
        'rheingold_gardens': 'Rheingold',
        'gates_plaza': 'Gates Plaza'
    }
    
    for prop_code, prop_name in properties.items():
        print(f"\n========================================================")
        print(f" Trends for {prop_name} ({prop_code})")
        print(f"========================================================")
        
        # Filter (case-insensitive for safety)
        prop_df = df[df['source_property'].astype(str).str.lower() == prop_code.lower()].copy()
        
        if prop_df.empty:
            print(f"No records found for property code '{prop_code}'")
            continue
            
        print(f"Total work orders: {len(prop_df):,}")
        
        # 1. Yearly trends (Long term)
        prop_df['Year'] = prop_df['call_date'].dt.year
        # Group and drop NaNs
        yearly = prop_df.groupby('Year').size().rename('Work Orders')
        print("\n--- Long Term Trends (By Year) ---")
        print(yearly.to_string())
        
        # 2. Monthly trends (Seasonal)
        prop_df['Month_Num'] = prop_df['call_date'].dt.month
        monthly = prop_df.groupby('Month_Num').size().rename('Work Orders')
        
        # Map month numbers to names
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        monthly.index = monthly.index.map(month_names)
        
        # Sort by month number (not alphabetically)
        # Reindexing to guarantee correct chronological calendar order
        monthly = monthly.reindex(list(month_names.values())).dropna().astype(int)
        
        print("\n--- Seasonal Trends (By Month) ---")
        print(monthly.to_string())
        print()

if __name__ == "__main__":
    main()
