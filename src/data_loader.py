#data_loader.py
import yfinance as yf #import information from yahoo finance
from pathlib import Path #import information from path
import pandas as pd

def download_stock_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if df.empty:
        print(f"No data found for {ticker}")
        return None
    # make the columns into one level
    # Fix MultiIndex columns properly
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df["ticker"] = ticker
    return df

def get_stock_info(ticker):
    """
    Fetches basic info for a ticker using yfinance.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "name": info.get("longName"),
            "market_cap": info.get("marketCap")
        }
    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return None
