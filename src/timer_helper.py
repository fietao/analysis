import time
from pathlib import Path
from src.config import TICKERS, start_date, end_date
from src.data_loader import download_stock_data

# Ensure the output directory exists
Path("ticker_data").mkdir(exist_ok=True)

all_data = []

for ticker in TICKERS:
    print(f"Downloading data {ticker}...")
    csv_path = Path(f"ticker_data/{ticker}.csv")

    if csv_path.exists():
        print(f"Data for {ticker} already exists")
        continue

    df = download_stock_data(ticker, start_date, end_date)

    if df is not None:
        df.to_csv(csv_path, index=False)
        all_data.append(df)
    else:
        print(f"Failed to download {ticker}")

    time.sleep(0.5)