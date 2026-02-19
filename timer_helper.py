import time

def wait(seconds):
    time.sleep(seconds)
    
for ticker in TICKERS:
     print(f"Downloading data {ticker}...")
     csv_path = f"ticker_data/{ticker}.csv"
     if path(csv_path).exists():
         print(f"Data for{ticker} already exits")
         continue
    df = download_stock_data(ticker, start_data, end_data)

    if df is not None:
        df.to_csv(f"ticker_data/{ticker}.csv", index=False)
        all_data.append(df)
    else:
        