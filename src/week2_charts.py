import os
import pandas as pd

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    print("\n[ERROR] Matplotlib or Seaborn is not installed. Please run:")
    print("  pip install matplotlib seaborn")
    print("to install them and run this script successfully.\n")
    exit(1)

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "WEEK 2 SOURCE OF TRUTH.xlsx")
CHARTS_DIR = os.path.join(BASE_DIR, "data", "processed", "charts")

# Ensure charts directory exists
os.makedirs(CHARTS_DIR, exist_ok=True)

# Month sorting helper
MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June', 
    'July', 'August', 'September', 'October', 'November', 'December'
]
MONTH_MAP = {i+1: name for i, name in enumerate(MONTH_NAMES)}

def save_yearly_trend(prop_df, prop_name, prop_code, color):
    """Generates a premium line chart for yearly trends (excluding 2026 as it's partial)."""
    yearly_df = prop_df.groupby('Year').size().reset_index(name='Work Orders')
    
    # Exclude 2026 since it is a partial year and would show a misleading dip
    yearly_df = yearly_df[yearly_df['Year'] < 2026]
    
    plt.figure(figsize=(10, 5), dpi=300)
    sns.set_theme(style="whitegrid")
    
    # Plot line and markers
    plt.plot(
        yearly_df['Year'], 
        yearly_df['Work Orders'], 
        marker='o', 
        color=color, 
        linewidth=2.5, 
        markersize=7,
        label='Work Orders'
    )
    
    # Styling
    plt.title(f"Yearly Work Order Trend — {prop_name} (2009–2025)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Year", fontsize=11, labelpad=10)
    plt.ylabel("Number of Work Orders", fontsize=11, labelpad=10)
    plt.xticks(yearly_df['Year'], rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Annotate final year value
    if not yearly_df.empty:
        last_row = yearly_df.iloc[-1]
        plt.annotate(
            f"{int(last_row['Work Orders'])}",
            (last_row['Year'], last_row['Work Orders']),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center',
            fontweight='bold',
            color=color
        )
    
    plt.tight_layout()
    file_path = os.path.join(CHARTS_DIR, f"{prop_code}_yearly_trend.png")
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {file_path}")

def save_seasonal_trends(prop_df, prop_name, prop_code, color):
    """Generates a side-by-side seasonal bar comparison: Historical vs 2025 Only."""
    # 1. Calculate overall monthly average / counts
    monthly_all = prop_df.groupby('Month_Num').size().rename('Work Orders').reindex(range(1, 13)).fillna(0)
    monthly_all.index = monthly_all.index.map(MONTH_MAP)
    
    # Convert to average per month (since we have ~17 years of data)
    years_count = len(prop_df['Year'].dropna().unique())
    monthly_avg = (monthly_all / years_count).round(1)
    
    # 2. Calculate 2025 monthly counts
    df_2025 = prop_df[prop_df['Year'] == 2025]
    monthly_2025 = df_2025.groupby('Month_Num').size().rename('Work Orders').reindex(range(1, 13)).fillna(0)
    monthly_2025.index = monthly_2025.index.map(MONTH_MAP)
    
    # Create a combined dataframe for plotting
    plot_df = pd.DataFrame({
        'Month': MONTH_NAMES,
        'Historical Avg (Annual)': monthly_avg.values,
        '2025 Total': monthly_2025.values
    })
    
    # Melt dataframe for seaborn barplot
    melted_df = pd.melt(plot_df, id_vars=['Month'], value_vars=['Historical Avg (Annual)', '2025 Total'], 
                        var_name='Timeframe', value_name='Work Orders')
    
    plt.figure(figsize=(12, 6), dpi=300)
    sns.set_theme(style="whitegrid")
    
    # Curated premium colors: main theme color and a lighter tint
    palette = [color, sns.light_palette(color, n_colors=3)[1]]
    
    sns.barplot(
        data=melted_df, 
        x='Month', 
        y='Work Orders', 
        hue='Timeframe', 
        palette=palette,
        edgecolor='black',
        linewidth=0.5
    )
    
    # Styling
    plt.title(f"Seasonal Work Order Trends — {prop_name}\n(Historical Annual Average vs. 2025)", 
              fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Month", fontsize=11, labelpad=10)
    plt.ylabel("Work Orders", fontsize=11, labelpad=10)
    plt.xticks(rotation=30)
    plt.legend(frameon=True, facecolor='white', edgecolor='none')
    
    plt.tight_layout()
    file_path = os.path.join(CHARTS_DIR, f"{prop_code}_seasonal_trends.png")
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {file_path}")

def main():
    print(f"Loading data from {DATA_PATH}...")
    try:
        df = pd.read_excel(DATA_PATH)
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return
        
    # Standardize types
    df['call_date'] = pd.to_datetime(df['call_date'], errors='coerce')
    df['Year'] = df['call_date'].dt.year.astype('Int64')
    df['Month_Num'] = df['call_date'].dt.month
    
    properties = {
        'rheingold_gardens': ('Rheingold', '#4F46E5'),  # Indigo
        'gates_plaza': ('Gates Plaza', '#0D9488')      # Teal
    }
    
    for prop_code, (prop_name, color) in properties.items():
        print(f"\nProcessing charts for {prop_name}...")
        prop_df = df[df['source_property'].astype(str).str.lower() == prop_code].copy()
        
        if prop_df.empty:
            print(f"  No records found for {prop_code}!")
            continue
            
        save_yearly_trend(prop_df, prop_name, prop_code, color)
        save_seasonal_trends(prop_df, prop_name, prop_code, color)
        
    print(f"\n[SUCCESS] All charts successfully generated in: {CHARTS_DIR}\n")

if __name__ == "__main__":
    main()
