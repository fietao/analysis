# main.py
import pandas as pd
import time 
from src.config import TICKERS, start_date, end_date
from src.data_loader import download_stock_data, get_stock_info
from src.config import DEV_MODE, DEV_TICKERS_LIMIT
from src.analytics import analyze_stock_data
from pathlib import Path

def main():
    all_data = []
    failed_tickers = []
    
    # Selection of tickers to run
    tickers_to_run = TICKERS
    if DEV_MODE:
        tickers_to_run = TICKERS[:DEV_TICKERS_LIMIT]
        print(f"Running in dev mode with {len(tickers_to_run)} tickers")
        
    Path("ticker_data").mkdir(exist_ok=True)
    
    # Metadata cache
    stock_info = {}
    
    for ticker in tickers_to_run:
        print(f"Processing {ticker}...")
        
        # Fetch metadata
        info = get_stock_info(ticker)
        if info:
            stock_info[ticker] = info
            
        csv_path = f"ticker_data/{ticker}.csv"
        
        if Path(csv_path).exists():
            print(f"  Loading existing data...")
            df = pd.read_csv(csv_path)
            all_data.append(df)
            continue
            
        df = download_stock_data(ticker, start_date, end_date)
        
        if df is not None: 
            df.to_csv(csv_path, index=False)
            all_data.append(df)
        else:
            print(f"  Failed to download data.")
            failed_tickers.append(ticker)
            
    if failed_tickers:
        print(f"Failed to download data for {failed_tickers}")    
        with open("failed_tickers.txt", "w") as f:
            f.write("\n".join(failed_tickers))
            
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values(by=["ticker", "Date"])
        combined_df.to_csv("all_stocks.csv", index=False)
        print("\nData saved to all_stocks.csv\n")
        
        # --- PHASE 2: CORE ANALYTICS REPORT ---
        print("="*60)
        print(f"{'STOCK ANALYSIS REPORT':^60}")
        print("="*60)
        
        for ticker in tickers_to_run:
            ticker_df = combined_df[combined_df['ticker'] == ticker]
            
            if not ticker_df.empty:
                metrics = analyze_stock_data(ticker_df)
                
                # Add market cap to metrics for printing
                if ticker in stock_info:
                    info = stock_info[ticker]
                    print(f"\n{info.get('name', ticker)} ({ticker})")
                    market_cap = info.get('market_cap')
                    if market_cap:
                        # Format market cap in Billions
                        metrics['Market Cap (B)'] = market_cap / 1e9
                else:
                    print(f"\n{ticker}:")
                
                # Separate insights from raw metrics for cleaner printing
                insights = metrics.pop('insights', [])
                
                for key, val in metrics.items():
                    if val is not None:
                        # Format logic
                        if 'return' in key or key in ['volatility', 'max_drawdown']:
                            print(f"  {key:25}: {val:.2%}")
                        elif 'Market Cap' in key:
                            print(f"  {key:25}: ${val:,.2f}B")
                        else:
                            print(f"  {key:25}: {val:.2f}")
                
                if insights:
                    print(f"\n  Analyst Notes:")
                    for note in insights:
                        print(f"  - {note}")
        print("\n" + "="*60)
    else:
        print("No data downloaded")

if __name__ == "__main__":
    main()
