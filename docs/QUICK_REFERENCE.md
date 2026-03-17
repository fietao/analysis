# QUICK REFERENCE GUIDE - Jarvis Stock Analysis Platform

## 🚀 Quick Start (5 Minutes)

### Setup
```bash
# Install Python dependencies
pip install fastapi uvicorn pandas numpy requests python-dotenv

# Create .env file with your API keys
# FINNHUB_API_KEY=your_key_here
# SEC_EDGE_API_KEY=your_key_here

# Run the program
python main.py

# In another terminal, start the API
python -m uvicorn api:app --reload --port 8000

# Run the frontend
cd frontend
npm run dev  # Opens on localhost:3000
```

### Test Everything Works
```bash
# Test API endpoint
curl http://localhost:8000/api/ticker/AAPL/details

# Check metrics are normalized
python -c "import pandas as pd; df = pd.read_csv('output/screening_results.csv'); print(df.columns.tolist())"

# Expected columns: ['ticker', 'MA50', 'MA200', '1Y Return', '3Y Return', '5Y Return', 'Volatility', 'Max Drawdown', ...]
```

---

## 📁 Key Files at a Glance

| File | Purpose | When to Edit |
|------|---------|--------------|
| `src/analytics.py` | Calculate metrics | Adding new calculations |
| `api.py` | REST endpoints | Adding API routes |
| `src/screening.py` | Rank & filter stocks | Changing scoring logic |
| `src/config.py` | Settings & env vars | Configuration changes |
| `frontend/src/app/` | Next.js pages | UI/frontend work |
| `.env.example` | Configuration template | Document new env vars |
| `.gitignore` | Git ignore rules | Security (never commit .env) |

---

## 🔑 Column Names (IMPORTANT!)

**Always use these in API responses:**

```python
FRIENDLY_NAMES = {
    "1Y_total_return": "1Y Return",
    "3Y_total_return": "3Y Return",
    "5Y_total_return": "5Y Return",
    "1Y_annualized_return": "1Y Annualized Return",
    "3Y_annualized_return": "3Y Annualized Return",
    "5Y_annualized_return": "5Y Annualized Return",
    "volatility": "Volatility",
    "sharpe_ratio": "Sharpe Ratio",
    "max_drawdown": "Max Drawdown",
    "current_price": "Current Price",
    "pe_ratio": "P/E Ratio",
    "dividend_yield": "Dividend Yield",
    "debt_to_equity": "Debt/Equity",
    "ma_50": "MA50",
    "ma_200": "MA200",
}
```

**Where to normalize:**
- ✅ `api.py` responses - Use `normalize_metrics()` before returning
- ✅ CSV outputs - Column headers should be friendly
- ❌ Internal calculations - Keep internal names (easier to debug)

---

## 🛡️ Error Handling Pattern (COPY-PASTE)

**All endpoints must follow this pattern:**

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@app.get("/api/endpoint")
async def my_endpoint(ticker: str):
    """
    Endpoint description.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        dict: Response with results or error
    
    Raises:
        HTTPException: 400 if invalid input, 500 if internal error
    """
    try:
        # 1. Validate input
        ticker = ticker.upper()
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid ticker format: {ticker}. Use alphanumeric (max 5 chars)."
            )
        
        # 2. Main logic
        result = process_ticker(ticker)
        
        # 3. Handle null results gracefully
        if result is None:
            logger.warning(f"No data found for ticker: {ticker}")
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker {ticker}"
            )
        
        # 4. Return with cache headers
        return JSONResponse(
            content=result,
            headers={"Cache-Control": "max-age=3600"}  # Cache 1 hour
        )
        
    except HTTPException:
        raise  # Re-raise HTTP errors
    except Exception as e:
        logger.error(f"Error in my_endpoint for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
```

---

## 📊 API Endpoints Reference

### Stock Details
```bash
GET /api/ticker/{ticker}/details
# Returns: price, returns, volatility, metrics for one stock

GET /api/ticker/{ticker}/historical
# Returns: price history for charting (date, close, volume)

GET /api/ticker/{ticker}/fundamentals
# Returns: P/E, dividend yield, debt/equity, etc.
```

### Screening & Analysis
```bash
GET /api/screening/data
# Returns: screening_results.csv (all 502 stocks with metrics)

POST /api/screening/refresh
# Recalculates all metrics (takes 2-5 minutes)

GET /api/screening/compare?tickers=AAPL,MSFT,GOOGL
# Compare multiple stocks side by side
```

### SEC Filings
```bash
POST /api/filing/upload
# Upload PDF filing for analysis

GET /api/filing/analysis/{ticker}
# Extract key metrics from last 3 filings
```

---

## ✅ Before Committing Code

**Checklist for ANY change:**

- [ ] Error handling added (try-catch + logging)
- [ ] Input validation (ticker format, file types, etc.)
- [ ] Null checks (if value is None: return None)
- [ ] Column names normalized (use friendly names)
- [ ] Docstrings added (what, parameters, returns, errors)
- [ ] No hardcoded values (use config/env vars)
- [ ] Logging at key points (DEBUG, INFO, WARNING, ERROR)
- [ ] Tested locally (`python main.py` or API request)
- [ ] TypeScript types defined (no `any` types)
- [ ] Cache headers added to GET endpoints
- [ ] Code follows existing patterns in repo

**Before git commit:**
```bash
# 1. Test it works
python main.py

# 2. Check for errors/logs
python -m pytest test_analytics.py  # if tests exist

# 3. Review changes
git diff

# 4. Commit with clear message
git add .
git commit -m "type: Short description

Longer explanation of what changed and why.

- Bullet point 1
- Bullet point 2"

# 5. Push to GitHub
git push origin main
```

---

## 🐛 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Missing dependencies | `pip install -r requirements.txt` |
| API returns `{"detail": "Internal server error"}` | Exception not caught | Check logs, add logging to see actual error |
| Columns show internal names like `1Y_total_return` | Forgot to normalize | Add `normalize_metrics()` before returning |
| `TypeError: object of type NoneType has no len()` | Null not handled | Add `if value is None: return None` |
| Frontend shows blank page | TypeScript error in next.js | Check browser console (F12) for errors |
| Screening refresh takes 10+ minutes | Getting live data for all 502 stocks | Expected! Or use DEV_MODE with 5 tickers |
| `CORS error: Access blocked` | Frontend can't reach API | Check CORS_ORIGINS in .env |
| `.env file not found` | Missing configuration | Copy `.env.example` to `.env` and fill values |

---

## 🎯 Common Tasks

### Add a New Metric to All Stocks

**Files to update:**
1. `src/analytics.py` - Add calculation function
2. `api.py` - Return it in endpoint response
3. `frontend/src/` - Display it in UI
4. `FULLSTACK_PROMPT.md` - Document the new metric

**Example:**
```python
# In src/analytics.py
def calculate_new_metric(df: pd.DataFrame) -> float | None:
    """Calculate new metric from price data."""
    if df is None or len(df) < 10:
        return None
    # ... calculation logic
    return float(result)

# In api.py response
ticker_data = {
    "ticker": ticker,
    "price": current_price,
    "new_metric": calculate_new_metric(prices),  # NEW
}
ticker_data = normalize_metrics(ticker_data)
return ticker_data
```

### Fix a Performance Issue

**Step 1:** Identify what's slow (`print()` timing or browser DevTools)
```python
import time
start = time.time()
result = expensive_operation()
print(f"Took {time.time() - start:.2f}s")
```

**Step 2:** Cache results (if data doesn't change often)
```python
# Use JSONResponse with Cache-Control
return JSONResponse(
    content=result,
    headers={"Cache-Control": "max-age=3600"}  # Cache 1 hour
)
```

**Step 3:** Optimize the calculation
```python
# Bad: Loop through dataframe row by row
for index, row in df.iterrows():
    process(row)

# Good: Vectorized operations
df.apply(lambda row: process(row), axis=1)
```

### Handle a New Error Type

```python
# 1. Check what error occurs
try:
    risky_operation()
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")

# 2. Add specific handler
try:
    risky_operation()
except ValueError as e:
    logger.warning(f"Invalid value: {e}")
    raise HTTPException(status_code=400, detail="Invalid input provided")
except KeyError as e:
    logger.error(f"Missing key: {e}")
    raise HTTPException(status_code=500, detail="Data structure error")
```

---

## 📚 Learn More

| Topic | File | Time |
|-------|------|------|
| **Full project overview** | `FULLSTACK_PROMPT.md` | 30 min |
| **Development guidelines** | `FULLSTACK_PROMPT.md` (Dev section) | 15 min |
| **Bug list & priorities** | `FULLSTACK_ANALYSIS.md` | 20 min |
| **API endpoint specs** | `FULLSTACK_PROMPT.md` (API section) | 20 min |
| **How to run API locally** | This file + ./install_deps.bat | 5 min |
| **How to add features** | `AI_PROMPT_TEMPLATE.md` | 10 min |

**Estimated time to understand codebase:** 4-6 hours

---

## 🎓 Code Examples by Task

### Example 1: Add Endpoint to Return New Metric
```python
# api.py

@app.get("/api/ticker/{ticker}/quality-score")
async def get_quality_score(ticker: str):
    """Return quality score (0-100) for a stock."""
    try:
        # Load data
        ticker = ticker.upper()
        csv_path = f"ticker_data/{ticker}.csv"
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail=f"No data for {ticker}")
        
        df = pd.read_csv(csv_path)
        
        # Calculate score
        score = calculate_quality_score(df)
        
        if score is None:
            raise HTTPException(status_code=400, detail="Insufficient data")
        
        # Return with normalization
        result = {
            "ticker": ticker,
            "quality_score": score,
            "grade": "A" if score > 80 else "B" if score > 60 else "C"
        }
        
        return JSONResponse(
            content=result,
            headers={"Cache-Control": "max-age=300"}  # 5 min cache
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating quality score for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Calculation failed")

def calculate_quality_score(df: pd.DataFrame) -> float | None:
    """Calculate quality score from metrics."""
    if df is None or len(df) < 50:
        return None
    
    # Example: Score based on price change + volume
    price_stability = 1 - (df['Close'].std() / df['Close'].mean())
    volume_strength = df['Volume'].mean() / df['Volume'].std() if df['Volume'].std() > 0 else 0
    
    score = (price_stability * 0.6 + volume_strength * 0.4) * 100
    return min(100, max(0, score))  # Clamp 0-100
```

### Example 2: Add Validation to Existing Endpoint
```python
# Before (no validation)
@app.post("/api/compare")
async def compare_stocks(tickers: str):
    stocks = tickers.split(",")
    return get_comparison(stocks)

# After (with validation)
@app.post("/api/compare")
async def compare_stocks(tickers: str = Query(..., min_length=1, max_length=200)):
    """Compare multiple stocks. Returns metrics for each."""
    try:
        # Validate input
        if not tickers or len(tickers.strip()) == 0:
            raise HTTPException(status_code=400, detail="Provide at least one ticker")
        
        stocks = [t.strip().upper() for t in tickers.split(",") if t.strip()]
        
        # Validate each ticker format
        for stock in stocks:
            if not stock.replace("-", "").isalnum() or len(stock) > 5:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid ticker format: {stock}"
                )
        
        # Verify we have data
        available = []
        for stock in stocks:
            if os.path.exists(f"ticker_data/{stock}.csv"):
                available.append(stock)
        
        if not available:
            raise HTTPException(status_code=404, detail=f"No data for any ticker")
        
        if len(available) < len(stocks):
            logger.warning(f"Missing data for: {set(stocks) - set(available)}")
        
        # Get comparison
        result = get_comparison(available)
        return JSONResponse(
            content=result,
            headers={"Cache-Control": "max-age=600"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing stocks {tickers}: {e}")
        raise HTTPException(status_code=500, detail="Comparison failed")
```

### Example 3: Add Error Boundary to Frontend
```typescript
// frontend/src/components/ErrorBoundary.tsx

import { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error) {
    console.error("Error caught:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p className="error-message">{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage in page:
// <ErrorBoundary>
//   <ScreenerComponent />
// </ErrorBoundary>
```

---

## 🔗 Links & Resources

- **Finnhub API Docs:** https://finnhub.io/docs/api
- **SEC EDGAR API:** https://www.sec.gov/cgi-bin/browse-edgar
- **FastAPI Tutorial:** https://fastapi.tiangolo.com/
- **Next.js Docs:** https://nextjs.org/docs
- **Pandas Docs:** https://pandas.pydata.org/docs/

---

## 📞 Getting Help

**When something breaks:**

1. **Check the logs**
   ```bash
   python main.py 2>&1 | tail -20  # Last 20 lines
   ```

2. **Use the debug guide**
   See "Debug Commands" section in FULLSTACK_PROMPT.md

3. **Ask AI for help**
   Copy this file + the error into AI_PROMPT_TEMPLATE.md format

4. **Check recent commits**
   ```bash
   git log --oneline -10  # See what changed
   git diff HEAD~1       # See changes from last commit
   ```

---

**Version:** 1.0 | **Last Updated:** March 16, 2026
