from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from src.config import TICKERS, start_date, end_date
from src.data_loader import download_stock_data, get_stock_info
from src.analytics import analyze_stock_data
from src.screening import generate_screening_report

app = FastAPI(title="Fiscal AI 2.0 API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/stocks")
def get_all_tickers():
    """Returns the list of available NASDAQ 100 tickers."""
    return {"tickers": TICKERS}

@app.get("/api/analysis/{ticker}")
def get_stock_analysis(ticker: str):
    """
    Downloads, analyzes, and returns metrics + insights for a ticker.
    """
    ticker = ticker.upper()
    
    # Try loading from local cache first
    csv_path = Path(f"ticker_data/{ticker}.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = download_stock_data(ticker, start_date, end_date)
        if df is not None:
            csv_path.parent.mkdir(exist_ok=True)
            df.to_csv(csv_path, index=False)
        else:
            raise HTTPException(status_code=404, detail="Stock data not found")

    metrics = analyze_stock_data(df)
    info = get_stock_info(ticker)
    
    return {
        "ticker": ticker,
        "info": info,
        "metrics": metrics
    }

@app.get("/api/health")
def health_check():
    return {"status": "online", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
