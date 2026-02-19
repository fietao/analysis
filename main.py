# main.py
import pandas as pd
import time 
from src.config import TICKERS, start_date, end_date
from src.data_loader import download_stock_data
from src.config import DEV_MODE, DEV_TICKERS_LIMIT
from pathlib import Path

def main():
    all_data = []
    failed_tickers = []
    Tickers_to_run = TICKERS
    if DEV_MODE:
        Tickers_to_run = DEV_TICKERS_LIMIT
        print(f"Running in dev mode with {len(Tickers_to_run)} tickers")
    Path("ticker_data").mkdir(exist_ok=True)
    for ticker in Tickers_to_run:
        print(f"Downloading data {ticker}...")
        csv_path = f"ticker_data/{ticker}.csv"
        if Path(csv_path).exists():
            print(f"loading existinf data for {ticker}")
            df = pd.read_csv(csv_path)
            all_data.append(df)
            continue
        df = download_stock_data(ticker, start_date, end_date)
        
        if df is not None: 
            df.to_csv(f"ticker_data/{ticker}.csv", index=False)
            all_data.append(df)
        else:
            print(f"Failed to download data for {ticker}")
            failed_tickers.append(ticker)
    if failed_tickers:
        print(f"Failed to download data for {failed_tickers}")    
        with open("failed_tickers.txt", "w") as f:
            f.write("\n".join(failed_tickers))
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values(by=["ticker", "Date"])
        combined_df.to_csv("all_stocks.csv", index=False)
        print("Data saved to all_stocks.csv")
        for ticker in TICKERS :
            print(f"Data for {ticker}")
            print(combined_df[combined_df['ticker'] == ticker].head())
        
    else:
        print("No data downloaded")
if __name__ == "__main__":
    main()

