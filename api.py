from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis API")

# Cache is considered stale if last date in CSV is older than this many calendar days
CACHE_STALE_DAYS = 2
API_TIMEOUT = 30  # seconds

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
    except Exception as e:
        logger.warning(f"Error checking cache staleness: {e}")
        return True

def ensure_live_data(ticker: str, force_refresh: bool) -> pd.DataFrame:
    """
    Load ticker data from cache or download; refresh if stale or force_refresh.
    Includes timeout and error handling for network failures.
    """
    csv_path = Path(f"ticker_data/{ticker}.csv")
    try:
        if force_refresh or is_cache_stale(csv_path):
            try:
                df = download_stock_data(ticker, start_date, end_date)
            except TimeoutError as e:
                logger.warning(f"Timeout downloading {ticker}: {e}. Using cached data.")
                df = None
            except Exception as e:
                logger.warning(f"Error downloading {ticker}: {e}. Using cached data.")
                df = None
                
            if df is not None and not df.empty:
                try:
                    csv_path.parent.mkdir(exist_ok=True)
                    df.to_csv(csv_path, index=False)
                    logger.info(f"Successfully updated {ticker} data")
                    return df
                except Exception as e:
                    logger.error(f"Error saving {ticker} to cache: {e}")
                    # Return the downloaded data even if cache save failed
                    return df if df is not None and not df.empty else None
                    
        # Try loading from cache
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                if df.empty:
                    logger.warning(f"Cache for {ticker} is empty")
                    return None
                return df
            except Exception as e:
                logger.error(f"Error reading cache for {ticker}: {e}")
                return None
    except Exception as e:
        logger.error(f"Unexpected error in ensure_live_data for {ticker}: {e}")
        
    return None

def normalize_screening_row(row: dict) -> dict:
    """
    Defensive normalization - ensures all required friendly column names exist.
    Note: metrics are now normalized by analyze_stock_data() in analytics.py,
    but this function serves as a safety net for legacy or external data.
    """
    out = dict(row)
    # Map backend names to frontend names if they still exist
    if "1Y_total_return" in out and "1Y Return" not in out:
        out["1Y Return"] = out["1Y_total_return"]
    if "volatility" in out and "Volatility" not in out:
        out["Volatility"] = out["volatility"]
    if "max_drawdown" in out and "Max Drawdown" not in out:
        out["Max Drawdown"] = out["max_drawdown"]
    return out

# Allowed CORS origins - configure via environment variable
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
if "CORS_ORIGINS" not in os.environ:
    logger.info("CORS_ORIGINS not set. Using default (localhost only)")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/api/stocks")
def get_all_tickers():
    """Returns the list of available NASDAQ 100 tickers."""
    try:
        return {"tickers": TICKERS}
    except Exception as e:
        logger.error(f"Error in get_all_tickers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve ticker list")

@app.get("/api/dashboard")
def get_dashboard_stats():
    """
    Live stats for the dashboard: ticker count and screening summary if available.
    """
    try:
        stats = {
            "ticker_count": len(TICKERS),
            "screening_available": False,
            "screening_ticker_count": 0,
            "avg_1y_return_pct": None,
            "last_updated": None,
            "error": None,
        }
        csv_path = Path("output/screening_results.csv")
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                if not df.empty:
                    stats["screening_available"] = True
                    stats["screening_ticker_count"] = len(df)
                    
                    # Try to calculate average return - handle both old and new column names
                    return_col = "1Y Return" if "1Y Return" in df.columns else "1Y_total_return"
                    if return_col in df.columns:
                        mean_val = pd.to_numeric(df[return_col], errors='coerce').mean()
                        if pd.notna(mean_val):
                            stats["avg_1y_return_pct"] = round(float(mean_val) * 100, 2)
                    
                    try:
                        stats["last_updated"] = datetime.fromtimestamp(csv_path.stat().st_mtime).isoformat() + "Z"
                    except Exception as e:
                        logger.warning(f"Could not get file modification time: {e}")
            except Exception as e:
                logger.warning(f"Error reading screening results: {e}")
                stats["error"] = "Screening data is corrupted. Please refresh."
        return stats
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate dashboard stats")

@app.get("/api/analysis/{ticker}")
def get_stock_analysis(ticker: str, refresh: bool = Query(False, description="Force re-download live data")):
    """
    Returns metrics + insights for a ticker using live or cached data.
    Cache is auto-refreshed if older than 2 days; use refresh=true to force update.
    """
    try:
        ticker = ticker.upper()
        
        # Validate ticker format
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
        df = ensure_live_data(ticker, force_refresh=refresh)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Stock data not found for ticker {ticker}")

        try:
            metrics = analyze_stock_data(df)
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to analyze {ticker}")
        
        try:
            info = get_stock_info(ticker)
        except Exception as e:
            logger.warning(f"Could not retrieve company info for {ticker}: {e}")
            info = None
        
        return {
            "ticker": ticker,
            "info": info,
            "metrics": metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stock_analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stock analysis")

@app.get("/api/health")
def health_check():
    return {"status": "online", "version": "2.0.0"}

@app.post("/api/screening/refresh")
def refresh_screening_data():
    """
    Fetches live data for all tickers, runs analytics and screening, and saves results.
    Returns the new screening results. In DEV_MODE only first DEV_TICKERS_LIMIT tickers are used.
    Partial failures are handled gracefully - returns all successful results with warnings.
    """
    try:
        tickers_to_run = TICKERS[:DEV_TICKERS_LIMIT] if DEV_MODE else TICKERS
        Path("ticker_data").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)

        all_metrics_list = []
        failed_tickers = []
        
        for ticker in tickers_to_run:
            try:
                df = ensure_live_data(ticker.upper(), force_refresh=True)
                if df is None or df.empty:
                    logger.warning(f"No data for {ticker}")
                    failed_tickers.append(ticker)
                    continue
                
                # analyze_stock_data now returns normalized column names
                try:
                    metrics = analyze_stock_data(df)
                except Exception as e:
                    logger.warning(f"Error analyzing {ticker}: {e}")
                    failed_tickers.append(ticker)
                    continue
                    
                metrics["ticker"] = ticker.upper()
                
                # Add company info - don't let this fail the whole ticker
                try:
                    info = get_stock_info(ticker.upper())
                    if info:
                        market_cap = info.get("market_cap")
                        metrics["Market Cap (B)"] = market_cap / 1e9 if market_cap else None
                        metrics["Forward PE"] = info.get("forward_pe")
                        metrics["Dividend Yield"] = info.get("dividend_yield")
                        metrics["Profit Margin"] = info.get("profit_margins")
                        metrics["Revenue Growth"] = info.get("revenue_growth")
                except Exception as e:
                    logger.debug(f"Could not get company info for {ticker}: {e}")
                
                all_metrics_list.append(metrics)
                
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {e}")
                failed_tickers.append(ticker)
                continue

        if not all_metrics_list:
            raise HTTPException(
                status_code=503, 
                detail="No ticker data could be loaded. Check network, API keys, and ticker list."
            )

        try:
            save_screening_results(all_metrics_list)
        except Exception as e:
            logger.error(f"Error saving screening results: {e}")
            raise HTTPException(status_code=500, detail="Failed to save screening results")
        
        rows = [normalize_screening_row(m) for m in all_metrics_list]
        
        response = {
            "results": rows, 
            "tickers_processed": len(all_metrics_list),
            "total_tickers": len(tickers_to_run),
        }
        
        if failed_tickers:
            response["failed_tickers"] = failed_tickers
            response["warning"] = f"Could not retrieve data for {len(failed_tickers)} ticker(s)"
            logger.info(f"Screening complete: {len(all_metrics_list)} succeeded, {len(failed_tickers)} failed")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh_screening_data: {e}")
        raise HTTPException(status_code=500, detail="Screening refresh failed")

@app.get("/api/screening")
def get_screening_data():
    """
    Returns the batch screening metrics as JSON (live data from cache or file).
    Use POST /api/screening/refresh to recompute from live market data.
    """
    try:
        csv_path = Path("output/screening_results.csv")
        if not csv_path.exists():
            raise HTTPException(
                status_code=404, 
                detail="Screening data not found. Click 'Refresh with live data' on the Screener page."
            )
        
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            logger.error(f"Error reading screening CSV: {e}")
            raise HTTPException(status_code=500, detail="Screening data is corrupted")
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Screening data is empty")
        
        df = df.where(pd.notnull(df), None)
        rows = [normalize_screening_row(r) for r in df.to_dict(orient="records")]
        return {"results": rows}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_screening_data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve screening data")

@app.get("/api/charts/{ticker}")
def get_stock_chart(ticker: str):
    """
    Returns the Matplotlib chart as a static asset.
    """
    try:
        ticker = ticker.upper()
        
        # Validate ticker
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
        chart_path = Path(f"output/charts/{ticker}_price_ma.png")
        if not chart_path.exists():
            raise HTTPException(status_code=404, detail=f"Chart not found for {ticker}")
        return FileResponse(chart_path, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stock_chart: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chart")

@app.get("/api/historical/{ticker}")
def get_historical_data(ticker: str, refresh: bool = Query(False, description="Force re-download live data")):
    """
    Returns the last 200 trading days of price data for interactive Recharts.
    Uses live data when cache is stale or refresh=true.
    """
    try:
        ticker = ticker.upper()
        
        # Validate ticker
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
        df = ensure_live_data(ticker, force_refresh=refresh)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Stock data not found for {ticker}")
        
        if "Date" not in df.columns or "Close" not in df.columns:
            raise HTTPException(status_code=500, detail="Data format error: missing required columns")
        
        df = df.tail(200)
        try:
            chart_data = df[["Date", "Close"]].to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error formatting chart data for {ticker}: {e}")
            raise HTTPException(status_code=500, detail="Failed to format historical data")
            
        return {"ticker": ticker, "data": chart_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_historical_data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve historical data")

@app.post("/api/upload-filing/{ticker}")
async def upload_filing(ticker: str, file: UploadFile = File(...)):
    """
    Uploads a PDF filing for a ticker and processes it.
    Validates file types and handles errors gracefully.
    """
    try:
        ticker = ticker.upper()
        
        # Validate ticker format
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        
        # Validate file size (max 50MB)
        if file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")
        
        upload_dir = Path("input/filings")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{ticker}_{file.filename}"
        
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                logger.info(f"Uploaded filing for {ticker}: {file.filename}")
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
            
        # Process the filing
        try:
            insights = process_filing(ticker)
        except Exception as e:
            logger.warning(f"Error processing filing for {ticker}: {e}")
            insights = None
        
        if insights:
            return {"ticker": ticker, "status": "success", "insights": insights}
        else:
            return {
                "ticker": ticker, 
                "status": "processed", 
                "message": "Filing saved but no key sections extracted."
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_filing: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

@app.get("/api/filings/{ticker}")
def get_filing_analysis(ticker: str):
    """
    Returns existing filing analysis for a ticker.
    """
    try:
        ticker = ticker.upper()
        
        # Validate ticker format
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
        try:
            insights = process_filing(ticker)
        except Exception as e:
            logger.warning(f"Error processing filing for {ticker}: {e}")
            insights = None
            
        if not insights:
            raise HTTPException(status_code=404, detail="No filing found for this ticker")
        return {"ticker": ticker, "insights": insights}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_filing_analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve filing analysis")

@app.get("/api/financials/{ticker}")
def get_stock_financials(ticker: str):
    """
    Returns historical Revenue and Net Income trends.
    """
    try:
        ticker = ticker.upper()
        
        # Validate ticker format
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
        try:
            data = get_historical_financials(ticker)
        except Exception as e:
            logger.warning(f"Error getting financials for {ticker}: {e}")
            data = None
            
        if not data:
            raise HTTPException(status_code=404, detail="Financial data not found for this ticker")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stock_financials: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve financial data")

@app.post("/api/upload-data/{ticker}")
async def upload_custom_data(ticker: str, file: UploadFile = File(...)):
    """
    Uploads a custom Excel/CSV dataset for a ticker.
    Expects columns: 'Date' and 'Close'.
    Validates data and handles errors gracefully.
    """
    try:
        ticker = ticker.upper()
        
        # Validate ticker format
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
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
                try:
                    df = pd.read_csv(temp_path)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
            elif file_ext in ['.xlsx', '.xls']:
                try:
                    df = pd.read_excel(temp_path)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid Excel file: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")

            if df.empty:
                raise HTTPException(status_code=400, detail="File contains no data")

            # Column normalization
            df.columns = [c.strip() for c in df.columns]
            
            # Try to find Date and Close columns (case-insensitive)
            col_lower = {c.lower(): c for c in df.columns}
            
            if 'date' not in col_lower or 'close' not in col_lower:
                raise HTTPException(status_code=400, detail="Missing required columns: 'Date' and 'Close'")
            
            # Rename to standard format
            df = df.rename(columns={col_lower['date']: 'Date', col_lower['close']: 'Close'})
            
            # Validate data
            try:
                pd.to_datetime(df['Date'])
                pd.to_numeric(df['Close'], errors='coerce')
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid data types: {str(e)}")
            
            # Save as the ticker's primary data source
            df.to_csv(final_path, index=False)
            logger.info(f"Successfully uploaded custom data for {ticker}")
            
            return {
                "ticker": ticker, 
                "status": "success", 
                "message": f"Custom dataset for {ticker} initialized successfully."
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in upload_custom_data: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_custom_data: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
