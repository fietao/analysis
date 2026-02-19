import pandas as pd
from pathlib import Path

# Automatically set project root (assumes config.py is in src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TICKER_FILE = PROJECT_ROOT / "ticker_list.csv"

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

DEV_MODE = True
DEV_TICKERS_LIMIT = 5