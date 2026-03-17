import pandas as pd
import os
from pathlib import Path

# Try to load environment variables from .env file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass  # dotenv not installed, use environment variables only

# Automatically set project root (assumes config.py is in src/)
TICKER_FILE = PROJECT_ROOT / "ticker_list.csv"

# API Configuration
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
SEC_EDGAR_BASE_URL = os.getenv("SEC_EDGAR_BASE_URL", "https://data.sec.gov/submissions")
OPENCORPORATES_API_KEY = os.getenv("OPENCORPORATES_API_KEY", "")

if not FINNHUB_API_KEY:
    print("⚠️  WARNING: FINNHUB_API_KEY not set in environment variables")
    print("   Get free key: https://finnhub.io")
    print("   Set via: export FINNHUB_API_KEY='your_key' or add to .env file")

start_date = "2004-01-01"
end_date = None

# Check if file exists
if not TICKER_FILE.exists():
    raise FileNotFoundError(f"Ticker file not found at {TICKER_FILE}")

# Read CSV
df = pd.read_csv(TICKER_FILE)

# Clean column names (remove spaces, make lowercase)
df.columns = df.columns.str.strip().str.lower()

# Make sure the column exists
if "ticker" not in df.columns:
    raise KeyError(f"'ticker' column not found in {TICKER_FILE}. Columns found: {list(df.columns)}")

# Get tickers as list of strings
TICKERS = df["ticker"].astype(str).tolist()

print(f"Loaded {len(TICKERS)} tickers from {TICKER_FILE}")

# DEV_MODE Configuration - can be overridden by environment variable
DEV_MODE = os.getenv("DEV_MODE", "True").lower() == "true"
DEV_TICKERS_LIMIT = int(os.getenv("DEV_TICKERS_LIMIT", "5"))

if DEV_MODE:
    print(f"🔧 DEV_MODE enabled: Only processing first {DEV_TICKERS_LIMIT} tickers")