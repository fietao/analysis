from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from src.config import TICKERS, start_date, end_date
from src.data_loader import download_stock_data, get_stock_info
from src.analytics import analyze_stock_data
from src.screening import generate_screening_report
from fastapi.responses import FileResponse

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

@app.get("/api/screening")
def get_screening_data():
    """
    Returns the batch screening metrics as JSON.
    Loads from output/screening_results.csv.
    """
    csv_path = Path("output/screening_results.csv")
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Screening data not found. Please run backend processing first.")
    
    df = pd.read_csv(csv_path)
    # Replace NaNs with None for JSON serialization
    df = df.where(pd.notnull(df), None)
    return {"data": df.to_dict(orient="records")}

@app.get("/api/charts/{ticker}")
def get_stock_chart(ticker: str):
    """
    Returns the Matplotlib chart as a static asset.
    """
    ticker = ticker.upper()
    chart_path = Path(f"output/charts/{ticker}_analysis.png")
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")
    return FileResponse(chart_path, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
