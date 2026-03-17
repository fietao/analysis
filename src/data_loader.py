# data_loader.py
import pandas as pd
from pathlib import Path
from datetime import datetime
import requests

# Try importing finnhub, but fallback gracefully
try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False
    print("⚠️  finnhub-python not installed. Run: pip install finnhub-python")

from src.config import FINNHUB_API_KEY, SEC_EDGAR_BASE_URL

# Initialize Finnhub client
finnhub_client = None
if FINNHUB_AVAILABLE and FINNHUB_API_KEY:
    try:
        finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    except Exception as e:
        print(f"Error initializing Finnhub: {e}")

def download_stock_data(ticker, start_date, end_date):
    """
    Fetches historical stock data from Finnhub.
    Returns DataFrame with OHLCV data.
    """
    if not finnhub_client:
        print(f"❌ Error: Finnhub not configured. Check FINNHUB_API_KEY environment variable.")
        return None
    
    try:
        # Convert date strings to Unix timestamps
        start_ts = int(pd.Timestamp(start_date).timestamp())
        end_ts = int(pd.Timestamp(end_date or datetime.now()).timestamp())
        
        # Fetch from Finnhub
        candles = finnhub_client.stock_candles(ticker, 'D', start_ts, end_ts)
        
        if not candles or 'o' not in candles:
            print(f"No data found for {ticker}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'Date': pd.to_datetime(candles['t'], unit='s'),
            'Open': candles['o'],
            'High': candles['h'],
            'Low': candles['l'],
            'Close': candles['c'],
            'Volume': candles['v']
        })
        
        df['ticker'] = ticker.upper()
        df = df.sort_values('Date').reset_index(drop=True)
        return df
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def get_stock_info(ticker):
    """
    Fetches basic info and fundamentals for a ticker using Finnhub.
    """
    if not finnhub_client:
        print(f"❌ Error: Finnhub not configured.")
        return None
    
    try:
        # Get company profile
        profile = finnhub_client.company_profile2(symbol=ticker)
        
        # Get basic financials
        financials = finnhub_client.company_basic_financials(ticker, 'annual')
        
        return {
            "name": profile.get('name'),
            "market_cap": profile.get('marketCapitalization', 0) * 1e6 if profile.get('marketCapitalization') else None,
            "forward_pe": financials.get('metric', {}).get('peForward'),
            "dividend_yield": financials.get('metric', {}).get('dividendYield'),
            "profit_margins": financials.get('metric', {}).get('netMarginMRQ'),
            "revenue_growth": financials.get('metric', {}).get('revenueGrowthYoY'),
            "debt_to_equity": financials.get('metric', {}).get('debtToEquity'),
            "return_on_equity": financials.get('metric', {}).get('roe')
        }
    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return None
