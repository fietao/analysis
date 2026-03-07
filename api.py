from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from src.config import TICKERS, start_date, end_date, DEV_MODE, DEV_TICKERS_LIMIT
from src.data_loader import download_stock_data, get_stock_info
from src.analytics import analyze_stock_data
from src.screening import generate_screening_report, save_screening_results
from src.document_processor import process_filing
from src.financials import get_historical_financials
from fastapi.responses import FileResponse
import shutil

app = FastAPI(title="Jarvis API")

# Cache is considered stale if last date in CSV is older than this many calendar days
CACHE_STALE_DAYS = 2

def is_cache_stale(csv_path: Path) -> bool:
    """Return True if cache is missing or older than CACHE_STALE_DAYS."""
    if not csv_path.exists():
        return True
    try:
        df = pd.read_csv(csv_path, nrows=1)
        if "Date" not in df.columns:
            return True
        full = pd.read_csv(csv_path)
        full["Date"] = pd.to_datetime(full["Date"])
        last_date = full["Date"].max()
        if pd.isna(last_date):
            return True
        cutoff = datetime.now() - timedelta(days=CACHE_STALE_DAYS)
        return last_date.to_pydatetime() < cutoff
    except Exception:
        return True

def ensure_live_data(ticker: str, force_refresh: bool) -> pd.DataFrame:
    """Load ticker data from cache or download; refresh if stale or force_refresh."""
    csv_path = Path(f"ticker_data/{ticker}.csv")
    if force_refresh or is_cache_stale(csv_path):
        df = download_stock_data(ticker, start_date, end_date)
        if df is not None:
            csv_path.parent.mkdir(exist_ok=True)
            df.to_csv(csv_path, index=False)
            return df
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None

def normalize_screening_row(row: dict) -> dict:
    """Map backend column names to frontend-friendly keys."""
    out = dict(row)
    if "1Y_total_return" in out and "1Y Return" not in out:
        out["1Y Return"] = out["1Y_total_return"]
    if "volatility" in out and "Volatility" not in out:
        out["Volatility"] = out["volatility"]
    if "max_drawdown" in out and "Max Drawdown" not in out:
        out["Max Drawdown"] = out["max_drawdown"]
    return out

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

@app.get("/api/dashboard")
def get_dashboard_stats():
    """
    Live stats for the dashboard: ticker count and screening summary if available.
    """
    stats = {
        "ticker_count": len(TICKERS),
        "screening_available": False,
        "screening_ticker_count": 0,
        "avg_1y_return_pct": None,
        "last_updated": None,
    }
    csv_path = Path("output/screening_results.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        stats["screening_available"] = True
        stats["screening_ticker_count"] = len(df)
        if "1Y_total_return" in df.columns:
            mean_ = df["1Y_total_return"].mean()
            if pd.notna(mean_):
                stats["avg_1y_return_pct"] = round(float(mean_) * 100, 2)
        try:
            stats["last_updated"] = datetime.fromtimestamp(csv_path.stat().st_mtime).isoformat() + "Z"
        except Exception:
            pass
    return stats

@app.get("/api/analysis/{ticker}")
def get_stock_analysis(ticker: str, refresh: bool = Query(False, description="Force re-download live data")):
    """
    Returns metrics + insights for a ticker using live or cached data.
    Cache is auto-refreshed if older than 2 days; use refresh=true to force update.
    """
    ticker = ticker.upper()
    df = ensure_live_data(ticker, force_refresh=refresh)
    if df is None:
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

@app.post("/api/screening/refresh")
def refresh_screening_data():
    """
    Fetches live data for all tickers, runs analytics and screening, and saves results.
    Returns the new screening results. In DEV_MODE only first DEV_TICKERS_LIMIT tickers are used.
    """
    tickers_to_run = TICKERS[:DEV_TICKERS_LIMIT] if DEV_MODE else TICKERS
    Path("ticker_data").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)

    all_metrics_list = []
    for ticker in tickers_to_run:
        df = ensure_live_data(ticker.upper(), force_refresh=True)
        if df is None:
            continue
        metrics = analyze_stock_data(df)
        metrics["ticker"] = ticker.upper()
        info = get_stock_info(ticker.upper())
        if info:
            metrics["market_cap"] = info.get("market_cap")
            metrics["forward_pe"] = info.get("forward_pe")
            metrics["dividend_yield"] = info.get("dividend_yield")
            metrics["profit_margins"] = info.get("profit_margins")
            metrics["revenue_growth"] = info.get("revenue_growth")
            if info.get("market_cap"):
                metrics["Market Cap (B)"] = info["market_cap"] / 1e9
            if info.get("forward_pe"):
                metrics["Forward PE"] = info["forward_pe"]
            if info.get("dividend_yield"):
                metrics["Div Yield"] = info["dividend_yield"]
            if info.get("profit_margins"):
                metrics["Profit Margin"] = info["profit_margins"]
            if info.get("revenue_growth"):
                metrics["Rev Growth"] = info["revenue_growth"]
        metrics["1Y Return"] = metrics.get("1Y_total_return")
        metrics["Volatility"] = metrics.get("volatility")
        metrics["Max Drawdown"] = metrics.get("max_drawdown")
        all_metrics_list.append(metrics)

    if not all_metrics_list:
        raise HTTPException(status_code=503, detail="No ticker data could be loaded. Check network and ticker list.")

    save_screening_results(all_metrics_list)
    rows = [normalize_screening_row(m) for m in all_metrics_list]
    return {"results": rows, "tickers_processed": len(all_metrics_list)}

@app.get("/api/screening")
def get_screening_data():
    """
    Returns the batch screening metrics as JSON (live data from cache or file).
    Use POST /api/screening/refresh to recompute from live market data.
    """
    csv_path = Path("output/screening_results.csv")
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Screening data not found. Click 'Refresh with live data' on the Screener page.")
    
    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)
    rows = [normalize_screening_row(r) for r in df.to_dict(orient="records")]
    return {"results": rows}

@app.get("/api/charts/{ticker}")
def get_stock_chart(ticker: str):
    """
    Returns the Matplotlib chart as a static asset.
    """
    ticker = ticker.upper()
    chart_path = Path(f"output/charts/{ticker}_price_ma.png")
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")
    return FileResponse(chart_path, media_type="image/png")

@app.get("/api/historical/{ticker}")
def get_historical_data(ticker: str, refresh: bool = Query(False, description="Force re-download live data")):
    """
    Returns the last 200 trading days of price data for interactive Recharts.
    Uses live data when cache is stale or refresh=true.
    """
    ticker = ticker.upper()
    df = ensure_live_data(ticker, force_refresh=refresh)
    if df is None:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    df = df.tail(200)
    chart_data = df[["Date", "Close"]].to_dict(orient="records")
    return {"ticker": ticker, "data": chart_data}

@app.post("/api/upload-filing/{ticker}")
async def upload_filing(ticker: str, file: UploadFile = File(...)):
    """
    Uploads a PDF filing for a ticker and processes it.
    """
    ticker = ticker.upper()
    upload_dir = Path("input/filings")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{ticker}_{file.filename}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the filing
        insights = process_filing(ticker)
        if insights:
            return {"ticker": ticker, "status": "success", "insights": insights}
        else:
            return {"ticker": ticker, "status": "processed", "message": "Filing saved but no key sections extracted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/filings/{ticker}")
def get_filing_analysis(ticker: str):
    """
    Returns existing filing analysis for a ticker.
    """
    ticker = ticker.upper()
    insights = process_filing(ticker)
    if not insights:
        raise HTTPException(status_code=404, detail="No filing found for this ticker")
    return {"ticker": ticker, "insights": insights}

@app.get("/api/financials/{ticker}")
def get_stock_financials(ticker: str):
    """
    Returns historical Revenue and Net Income trends.
    """
    ticker = ticker.upper()
    data = get_historical_financials(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Financial data not found for this ticker")
    return data

@app.post("/api/upload-data/{ticker}")
async def upload_custom_data(ticker: str, file: UploadFile = File(...)):
    """
    Uploads a custom Excel/CSV dataset for a ticker.
    Expects columns: 'Date' and 'Close'.
    """
    ticker = ticker.upper()
    upload_dir = Path("ticker_data")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = Path(file.filename).suffix.lower()
    temp_path = upload_dir / f"temp_{ticker}{file_ext}"
    final_path = upload_dir / f"{ticker}.csv"

    try:
        # Save uploaded file temporarily
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Validate and convert to CSV
        if file_ext == '.csv':
            df = pd.read_csv(temp_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(temp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")

        # Column normalization
        df.columns = [c.capitalize() for c in df.columns]
        if 'Date' not in df.columns or 'Close' not in df.columns:
            # Try lowercase if capitalize failed
            df.columns = [c.lower() for c in df.columns]
            if 'date' in df.columns and 'close' in df.columns:
                df = df.rename(columns={'date': 'Date', 'close': 'Close'})
            else:
                raise HTTPException(status_code=400, detail="Missing required columns: 'Date' and 'Close'")

        # Save as the ticker's primary data source
        df.to_csv(final_path, index=False)
        temp_path.unlink() # Delete temp file
        
        return {"ticker": ticker, "status": "success", "message": f"Custom dataset for {ticker} initialized successfully."}
    except Exception as e:
        if temp_path.exists(): temp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
