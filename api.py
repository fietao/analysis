from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from src.config import TICKERS, start_date, end_date
from src.data_loader import download_stock_data, get_stock_info
from src.analytics import analyze_stock_data
from src.screening import generate_screening_report
from src.document_processor import process_filing
from src.financials import get_historical_financials
from fastapi.responses import FileResponse
import shutil

app = FastAPI(title="Jarvis API")

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
    return {"results": df.to_dict(orient="records")}

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
def get_historical_data(ticker: str):
    """
    Returns the last 200 trading days of price data for interactive Recharts.
    """
    ticker = ticker.upper()
    csv_path = Path(f"ticker_data/{ticker}.csv")
    
    if not csv_path.exists():
        df = download_stock_data(ticker, start_date, end_date)
        if df is not None:
            df.to_csv(csv_path, index=False)
        else:
            raise HTTPException(status_code=404, detail="Stock data not found")
    else:
        df = pd.read_csv(csv_path)
    
    # Take last 200 points for a clean chart
    df = df.tail(200)
    
    # Return Date and Close for Recharts
    chart_data = df[['Date', 'Close']].to_dict(orient="records")
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
