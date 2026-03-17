import pandas as pd
from src.analytics import analyze_stock_data
from pathlib import Path

def test_analysis():
    # Pick a ticker that is likely to have data
    ticker = "AAPL"
    csv_path = Path(f"ticker_data/{ticker}.csv")
    
    if not csv_path.exists():
        print(f"Error: No data found for {ticker}. Please run main.py first.")
        return
        
    print(f"Loading data for {ticker}...")
    df = pd.read_csv(csv_path)
    
    print(f"Running analysis...")
    metrics = analyze_stock_data(df)
    
    print(f"\nResults for {ticker}:")
    for key, value in metrics.items():
        if value is not None:
            if 'return' in key:
                print(f"{key}: {value:.2%}")
            else:
                print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: N/A")

if __name__ == "__main__":
    test_analysis()
