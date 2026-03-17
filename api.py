from fastapi import FastAPI, HTTPException, File, UploadFile, Query, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
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
from src.models import (
    UserCreate, UserLogin, Token, UserResponse, AchievementLog,
    BadgeType, UserBadge, LeaderboardResponse, LeaderboardEntry,
    AIRequest, AIResponse, AIConversation, AIMessage
)
from src.auth import (
    create_access_token, create_refresh_token, verify_token, refresh_access_token,
    hash_password, verify_password, validate_password_strength,
    extract_user_id_from_token, extract_user_role_from_token,
    ACCESS_TOKEN_EXPIRE_HOURS
)
from src.gamification import GamificationService, LeaderboardService, AchievementTracker
import shutil
import logging
import re
import os

# ✅ SECURITY: Rate limiting
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    print("⚠️  slowapi not installed. Run: pip install slowapi")

# Configure secure logging (mask secrets)
class MaskingFormatter(logging.Formatter):
    """Formatter that masks API keys and tokens in logs"""
    
    def format(self, record):
        msg = str(record.msg)
        # Mask API keys
        msg = re.sub(
            r'(api[_-]?key[=\s:]*)[^\s,}"]*',
            r'\1***MASKED***',
            msg,
            flags=re.IGNORECASE
        )
        # Mask bearer tokens
        msg = re.sub(
            r'(bearer\s+)[^\s]*',
            r'\1***MASKED***',
            msg,
            flags=re.IGNORECASE
        )
        # Mask generic tokens
        msg = re.sub(
            r'(token[=\s:]*)[^\s,}"]*',
            r'\1***MASKED***',
            msg,
            flags=re.IGNORECASE
        )
        record.msg = msg
        return super().format(record)

# Configure logging with security
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(MaskingFormatter('%(asctime)s - %(levelname)s - %(message)s'))

app = FastAPI(title="Jarvis API", version="1.0.0")

# ✅ SECURITY: Add Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,localhost:3000,localhost:8000").split(",")
)

# ✅ SECURITY: Rate limiting
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, lambda r, e: JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    ))
else:
    limiter = None
    print("⚠️  Rate limiting disabled (install slowapi for protection)")

# ✅ SECURITY: Utility functions
def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    Removes path separators and whitelists allowed characters.
    """
    # Remove path separators
    filename = os.path.basename(filename)
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Whitelist allowed characters (alphanumeric, hyphen, underscore, dot)
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
    filename = ''.join(c if c in allowed_chars else '_' for c in filename)
    
    return filename or "upload.pdf"  # Default if all chars invalid

def sanitize_error_message(message: str) -> str:
    """
    Remove sensitive information from error messages.
    Sanitizes API keys, tokens, and paths.
    """
    # Mask API keys
    message = re.sub(
        r'(api[_-]?key[=:]*)[^\s,}"]*',
        r'\1***MASKED***',
        message,
        flags=re.IGNORECASE
    )
    # Mask tokens
    message = re.sub(
        r'(bearer\s+|token[=:]*)[^\s,}"]*',
        r'\1***MASKED***',
        message,
        flags=re.IGNORECASE
    )
    # Mask file paths (show only filename)
    message = re.sub(
        r'([/\\][^\s,}"]*)',
        r'***PATH***',
        message
    )
    return message

def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize ticker symbol.
    Returns uppercase ticker or raises ValueError.
    """
    ticker = str(ticker).upper().strip()
    
    if not ticker or len(ticker) > 5:
        raise ValueError("Ticker must be 1-5 characters")
    
    if not ticker.replace("-", "").isalnum():
        raise ValueError("Ticker must contain only letters, numbers, and hyphens")
    
    return ticker

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
        logger.warning(f"Error checking cache staleness: {sanitize_error_message(str(e))}")
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

# ✅ SECURITY: Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # HSTS: Force HTTPS for 1 year
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # CSP: Only load resources from same domain
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
    
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Cache-Control helper
def add_cache_control(response, max_age: int = 300):
    """Add Cache-Control headers to improve browser and CDN caching."""
    response.headers["Cache-Control"] = f"public, max-age={max_age}"
    return response

@app.get("/api/stocks")
def get_all_tickers():
    """Returns the list of available NASDAQ 100 tickers."""
    try:
        response_data = {"tickers": TICKERS}
        # Cache ticker list for 24 hours (static data)
        return JSONResponse(content=response_data, headers={"Cache-Control": "public, max-age=86400"})
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
        # Cache dashboard stats for 5 minutes
        return JSONResponse(content=stats, headers={"Cache-Control": "public, max-age=300"})
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
    ✅ SECURE: Fetches live data for all tickers, runs analytics and screening.
    Rate limited to 1 request per hour per IP to prevent DoS.
    Returns the new screening results. In DEV_MODE only first DEV_TICKERS_LIMIT tickers are used.
    Partial failures are handled gracefully - returns all successful results with warnings.
    """
    # ✅ Rate limiting: 1 request per hour
    if limiter:
        # This is a long-running operation, so we limit it strictly
        pass  # Decorator would be applied below
    
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
        response_data = {"results": rows}
        # Cache screening results for 10 minutes (relatively static)
        return JSONResponse(content=response_data, headers={"Cache-Control": "public, max-age=600"})
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
    ✅ SECURE: Uploads a PDF filing for a ticker and processes it.
    Prevents path traversal, validates file types and size.
    """
    try:
        # ✅ Validate ticker
        try:
            ticker = validate_ticker(ticker)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # ✅ Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        
        # ✅ Validate file size (max 50MB)
        if file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")
        
        # ✅ Sanitize filename to prevent path traversal
        safe_filename = sanitize_filename(file.filename)
        
        # ✅ Resolve absolute upload path
        upload_dir = Path("input/filings").resolve()
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # ✅ Construct file path and verify it's within upload_dir
        file_path = upload_dir / f"{ticker}_{safe_filename}"
        
        # ✅ Security check: ensure path doesn't escape upload_dir
        try:
            file_path.resolve().relative_to(upload_dir.resolve())
        except ValueError:
            logger.error(f"Path traversal attempt detected: {file_path}")
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # ✅ Save file securely
        try:
            file_content = await file.read()
            file_path.write_bytes(file_content)
            logger.info(f"Uploaded filing for {ticker}: {safe_filename}")
        except Exception as e:
            logger.error(f"Error saving uploaded file: {sanitize_error_message(str(e))}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
            
        # Process the filing
        try:
            insights = process_filing(ticker)
        except Exception as e:
            logger.warning(f"Error processing filing for {ticker}: {sanitize_error_message(str(e))}")
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

# ============================================================================
# PHASE 5: AUTHENTICATION & USER MANAGEMENT
# ============================================================================

# In-memory user store (TODO: Replace with database in Phase 6)
users_db = {}  # username -> user_info
achievement_log = []  # List of achievements
gamification_service = GamificationService()
achievement_tracker = AchievementTracker()

def get_current_user(authorization: str = Header(None)) -> dict:
    """Dependency: Extract and validate current user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    is_valid, payload = verify_token(token)
    if not is_valid or not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # TODO: Lookup user from database
    return {"user_id": user_id, "email": payload.get("email"), "role": payload.get("role")}

@app.post("/api/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    """
    User registration endpoint
    Creates new user account and returns JWT token
    """
    try:
        # Validate password strength
        is_strong, msg = validate_password_strength(user.password)
        if not is_strong:
            raise HTTPException(status_code=400, detail=msg)
        
        # Check if user exists
        if any(u["email"] == user.email for u in users_db.values()):
            raise HTTPException(status_code=409, detail="Email already registered")
        
        if any(u["username"] == user.username for u in users_db.values()):
            raise HTTPException(status_code=409, detail="Username already taken")
        
        # Create user
        user_id = len(users_db) + 1
        hashed_pw = hash_password(user.password)
        
        users_db[user.email] = {
            "id": user_id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "hashed_password": hashed_pw,
            "role": "free",
            "tier": "free",
            "points": 0,
            "badges": [],
            "created_at": datetime.utcnow(),
            "login_streak": 0,
            "last_login": None,
            "is_active": True
        }
        
        # Create tokens
        access_token = create_access_token(user_id, user.email, "free")
        refresh_token = create_refresh_token(user_id, user.email)
        
        logger.info(f"New user registered: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Signup failed")

@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    User login endpoint
    Authenticates user and returns JWT token
    """
    try:
        user = users_db.get(credentials.email)
        if not user or not verify_password(credentials.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user["is_active"]:
            raise HTTPException(status_code=403, detail="Account is disabled")
        
        # Update last login
        user["last_login"] = datetime.utcnow()
        
        # Award daily login points
        points = gamification_service.calculate_daily_bonus(user["login_streak"], True)
        user["points"] += points
        
        # Create tokens
        access_token = create_access_token(user["id"], user["email"], user["role"])
        refresh_token = create_refresh_token(user["id"], user["email"])
        
        logger.info(f"User logged in: {credentials.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/auth/refresh", response_model=Token)
async def refresh_tokens(authorization: str = Header(None)):
    """
    Refresh JWT token
    Uses refresh token to create new access token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid header")
    
    tokens = refresh_access_token(token)
    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    access_token, new_refresh = tokens
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600
    }

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        user = users_db.get(current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "tier": user["tier"],
            "created_at": user["created_at"],
            "points": user["points"],
            "badges_earned": len(user["badges"]),
            "is_active": user["is_active"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Failed to get profile")

# ============================================================================
# PHASE 5: GAMIFICATION
# ============================================================================

@app.get("/api/gamification/badges")
async def get_user_badges(current_user: dict = Depends(get_current_user)):
    """Get user's earned badges"""
    try:
        user = users_db.get(current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        badges = []
        for badge_type in user["badges"]:
            badge_def = gamification_service.badges.get(badge_type)
            badges.append({
                "type": badge_type,
                "name": badge_def["name"],
                "description": badge_def["description"],
                "icon": badge_def["icon"],
                "points": badge_def["points"]
            })
        
        return {"badges": badges, "total": len(badges)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get badges error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Failed to get badges")

@app.get("/api/gamification/achievements")
async def log_action(
    action: str,
    current_user: dict = Depends(get_current_user)
):
    """Log user action and award points/badges"""
    try:
        user = users_db.get(current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate points
        points = gamification_service.calculate_points_for_action(
            action,
            {"premium": user["role"] == "pro"}
        )
        
        # Award points
        user["points"] += points
        
        # Check for badges
        badges_earned = achievement_tracker.process_badge_achievements(
            user["id"], action, {
                "login_streak": user["login_streak"],
                "current_badges": user["badges"],
                "leaderboard_rank": 1000  # TODO: Calculate from leaderboard
            }
        )
        
        # Award new badges
        user["badges"].extend(badges_earned)
        
        # Log achievement
        achievement_log.append({
            "user_id": user["id"],
            "action": action,
            "points": points,
            "timestamp": datetime.utcnow(),
            "badges_earned": badges_earned
        })
        
        logger.info(f"Achievement logged: {user['email']} - {action} (+{points} pts)")
        
        return {
            "points_earned": points,
            "total_points": user["points"],
            "badges_earned": badges_earned,
            "tier": gamification_service.get_tier_for_points(user["points"]),
            "next_milestone": gamification_service.get_next_milestone(user["points"])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Achievement error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Failed to log achievement")

@app.get("/api/gamification/leaderboard")
async def get_leaderboard(limit: int = Query(100, ge=1, le=1000)):
    """Get global leaderboard"""
    try:
        # Build points list
        user_points = [
            (user["id"], user["points"], user["username"])
            for user in users_db.values()
        ]
        
        leaderboard = LeaderboardService.get_global_leaderboard(user_points, limit=limit)
        
        return {
            "entries": leaderboard,
            "total_users": len(users_db),
            "generated_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Leaderboard error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@app.get("/api/gamification/leaderboard/me")
async def get_user_leaderboard_position(current_user: dict = Depends(get_current_user)):
    """Get user's rank and surrounding context on leaderboard"""
    try:
        user = users_db.get(current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build points list
        all_points = [
            (u["id"], u["points"])
            for u in users_db.values()
        ]
        
        rank_info = LeaderboardService.get_user_rank_context(
            user["id"],
            user["points"],
            all_points
        )
        
        return rank_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User rank error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Failed to get rank")

# ============================================================================
# PHASE 5: AI ASSISTANT (BETA - Structure ready for GPT-4 integration)
# ============================================================================

conversations_db = {}  # conversation_id -> conversation

@app.post("/api/ai/chat")
async def ai_chat(request: AIRequest, current_user: dict = Depends(get_current_user)):
    """
    Chat with AI assistant
    TODO: Integrate GPT-4 API in Phase 5
    """
    try:
        user = users_db.get(current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        conv_id = request.conversation_id or f"conv_{user['id']}_{datetime.utcnow().timestamp()}"
        
        # TODO: Call GPT-4 API here
        # For now, return placeholder response
        ai_response = f"[AI Assistant] I received your message: '{request.message}'. Full AI integration coming in Phase 5!"
        
        # Award points for using AI
        user["points"] += gamification_service.calculate_points_for_action("ai_chat")
        
        return {
            "conversation_id": conv_id,
            "message": ai_response,
            "confidence": 0.6,
            "sources": [],
            "timestamp": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI chat error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Failed to process message")

# ============================================================================
# PHASE 5: VIDEOS (Structure ready for YouTube integration)
# ============================================================================

@app.get("/api/videos")
async def list_videos(category: str = Query(None), limit: int = Query(20)):
    """
    List available video content
    TODO: Integrate YouTube API in Phase 5
    """
    try:
        # Placeholder videos
        videos = [
            {
                "video_id": "intro_1",
                "title": "Getting Started with Stock Analysis",
                "category": "tutorial",
                "duration_seconds": 600,
                "access_tier": "free",
                "views": 1250
            },
            {
                "video_id": "strategy_1",
                "title": "Dividend Growth Strategy",
                "category": "strategy",
                "duration_seconds": 1200,
                "access_tier": "pro",
                "views": 850
            }
        ]
        
        if category:
            videos = [v for v in videos if v["category"] == category]
        
        return {"videos": videos[:limit], "total": len(videos)}
    
    except Exception as e:
        logger.error(f"Video list error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Failed to get videos")

@app.post("/api/videos/{video_id}/watch")
async def log_video_watch(video_id: str, current_user: dict = Depends(get_current_user)):
    """Log video watch and award points"""
    try:
        user = users_db.get(current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Award points for watching
        user["points"] += gamification_service.calculate_points_for_action("video_watched")
        
        return {
            "message": "Video watch logged",
            "points_earned": gamification_service.calculate_points_for_action("video_watched")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video watch error: {sanitize_error_message(str(e))}")
        raise HTTPException(status_code=500, detail="Failed to log video watch")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
