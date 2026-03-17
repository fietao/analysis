# JARVIS STOCK ANALYSIS PROGRAM - FULL-STACK DEVELOPMENT PROMPT

## 🎯 PROJECT OVERVIEW

**Project Name:** Jarvis  
**Purpose:** Comprehensive stock analysis and screening platform using real-time market data  
**Architecture:** 3-tier full-stack (Frontend/API/Core Analytics)  
**Status:** Beta - Functional but needs bug fixes and feature expansion  
**Last Updated:** March 16, 2026

### Quick Facts
- **502 NASDAQ 100 tickers** analyzed
- **5-year historical data** per stock
- **Batch screening** with custom metrics
- **SEC EDGAR integration** for financial filings
- **Interactive charts** and dashboards

---

## 📊 TECH STACK

### Frontend
- **Framework:** Next.js 16.1.6 (React 19.2.3)
- **Language:** TypeScript
- **Styling:** Tailwind CSS 4
- **Charts:** Recharts (interactive line/bar charts)
- **Animations:** Framer Motion
- **State:** Current plan: Zustand (or Redux - not implemented)

### Backend API
- **Framework:** FastAPI (Python 3.14.2)
- **Server:** Uvicorn
- **CORS:** Restricted middleware
- **Caching:** Browser cache with Cache-Control headers
- **Error Handling:** Try-catch + logging on all endpoints

### Data & Analytics
- **Data Processing:** pandas, numpy
- **Data Source:** Finnhub API (professional stock data)
- **Filings:** SEC EDGAR API (structured company data)
- **Visualization:** matplotlib (static charts)

### Infrastructure
- **Configuration:** python-dotenv (environment variables)
- **File Storage:** Local CSV files (ticker_data/, output/)
- **Version Control:** Git/GitHub (fietao/analysis)

---

## 🏗️ ARCHITECTURE & DATA FLOW

### Core Pipeline (3-Phase Analysis)

```
INPUT: Ticker List (502 stocks)
  ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 1: DATA COLLECTION                            │
│ ├─ download_stock_data() [Finnhub API]              │
│ ├─ get_stock_info() [Company fundamentals]          │
│ └─ Cache: ticker_data/{TICKER}.csv                  │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 2: ANALYTICS                                  │
│ ├─ calculate_returns() [1Y, 3Y, 5Y]                 │
│ ├─ calculate_volatility() [annualized std dev]      │
│ ├─ calculate_max_drawdown()                         │
│ ├─ get_moving_averages() [MA50, MA200]              │
│ ├─ generate_insights() [human-readable notes]       │
│ ├─ normalize_metrics() [friendly column names]      │
│ └─ Output: metrics dict with normalized names       │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 3: SCREENING & REPORTING                      │
│ ├─ generate_screening_report() [rankings, filters]  │
│ ├─ save_screening_results() [CSV output]            │
│ ├─ create_visualizations() [PNG charts]             │
│ └─ Cache: output/screening_results.csv              │
└─────────────────────────────────────────────────────┘
  ↓
OUTPUT: Metrics, Charts, Insights
```

### API Endpoints (REST)

**GET /api/stocks**
- Returns: `{tickers: ["AAPL", "MSFT", ...]}`
- Cache: 24 hours

**GET /api/dashboard**
- Returns: `{ticker_count, screening_available, avg_1y_return_pct, last_updated}`
- Cache: 5 minutes

**GET /api/analysis/{ticker}?refresh=false**
- Returns: `{ticker, info: {...}, metrics: {...}}`
- Metrics keys: "1Y Return", "Volatility", "Max Drawdown", etc.
- Cache: 2 hours (auto-refresh if > 2 days old)

**POST /api/screening/refresh**
- Refreshes all tickers with live data
- Returns: `{results: [...], tickers_processed, failed_tickers, warning}`
- No cache (always fresh)
- DEV_MODE: Only 5 tickers

**GET /api/screening**
- Returns: `{results: [...]}`  - pre-calculated screening data
- Cache: 10 minutes

**GET /api/historical/{ticker}**
- Returns: Latest 200 trading days: `{ticker, data: [{Date, Close}, ...]}`
- Cache: 2 hours

**GET /api/charts/{ticker}**
- Returns: PNG file (matplotlib) with price + moving averages
- Cache: 24 hours

**GET /api/financials/{ticker}**
- Returns: Revenue, Net Income trends (from SEC EDGAR)

**POST /api/upload-filing/{ticker}**
- Upload PDF filing for processing

**POST /api/upload-data/{ticker}**
- Upload custom Excel/CSV data (Date, Close columns required)

---

## 📁 DIRECTORY STRUCTURE

```
stock analysis program/
├── main.py                          # CLI entry point
├── api.py                           # FastAPI server
├── requirements.txt                 # Python dependencies
├── ticker_list.csv                  # 502 NASDAQ tickers
├── all_stocks.csv                   # Generated analysis data
├── .env.example                     # Configuration template
├── .gitignore                       # Exclude secrets
│
├── src/                             # Core analytics
│   ├── __init__.py
│   ├── config.py                    # DEV_MODE, API keys, settings
│   ├── data_loader.py               # Finnhub API integration
│   ├── analytics.py                 # Metrics calculation + normalization
│   ├── screening.py                 # Ranking and filtering logic
│   ├── visualizer.py                # matplotlib chart generation
│   ├── document_processor.py         # SEC EDGAR filing extraction
│   ├── financials.py                # Financial metrics extraction
│   └── __pycache__/
│
├── ticker_data/                     # CSV cache (502 stocks)
│   ├── AAPL.csv, MSFT.csv, ...     # Historical OHLCV data
│   └── ... (500+ ticker files)
│
├── output/                          # Generated reports
│   ├── screening_results.csv        # Batch metrics (cached)
│   ├── all_stocks.csv               # Combined analysis
│   └── charts/                      # PNG files (price charts)
│       ├── AAPL_price_ma.png
│       ├── MSFT_price_ma.png
│       └── ... (100+ charts)
│
├── input/
│   └── filings/                     # User-uploaded PDFs
│
├── frontend/                        # Next.js React app
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── eslint.config.mjs
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Root layout
│   │   │   ├── page.tsx             # Dashboard home
│   │   │   ├── error.tsx            # Error boundary (NOT IMPLEMENTED ❌)
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx         # Analytics detail page (TYPE ISSUES ❌)
│   │   │   ├── screener/
│   │   │   │   └── page.tsx         # Screening results
│   │   │   └── filings/
│   │   │       └── page.tsx         # Filing uploads
│   │   └── components/
│   │       ├── DashboardCards.tsx
│   │       ├── ScreenerTable.tsx
│   │       └── ... (other components)
│   ├── public/
│   └── node_modules/
│
├── PROGRAM_ANALYSIS.md              # Architecture documentation
├── FULLSTACK_ANALYSIS.md            # Bug list and TODO
├── API_SETUP_GUIDE.md               # Finnhub/SEC EDGAR setup
├── API_STRATEGY.md                  # API evaluation
├── README.md                        # Project overview
└── frontend_roadmap.md              # Frontend tasks
```

---

## 🔑 KEY FILES EXPLAINED

### src/config.py
**Purpose:** Centralized configuration  
**Key Variables:**
- `FINNHUB_API_KEY` - Live API key (from .env)
- `SEC_EDGAR_BASE_URL` - Free government data endpoint
- `DEV_MODE` - Toggle between dev (5 tickers) & production (502 tickers)
- `DEV_TICKERS_LIMIT` - How many to process in dev mode
- `TICKERS` - List of 502 stock symbols

**How to Configure:**
```bash
# Create .env file (NOT committed to git)
export DEV_MODE=False              # Switch to production
export DEV_TICKERS_LIMIT=10        # Or run 10 tickers in dev
export FINNHUB_API_KEY="sk_..."    # From https://finnhub.io
export CORS_ORIGINS="https://yourdomain.com"  # For production
```

### src/data_loader.py
**Purpose:** Fetch and cache stock data  
**Main Functions:**
- `download_stock_data(ticker, start_date, end_date)` - Finnhub API calls
- `get_stock_info(ticker)` - Company fundamentals (market cap, PE ratio, etc.)
- Both return None on error and log warnings

### src/analytics.py
**Purpose:** Calculate investment metrics  
**Main Functions:**
- `analyze_stock_data(df)` - Main orchestrator (calls all below)
  - `calculate_returns()` - 1Y/3Y/5Y total and annualized
  - `calculate_volatility()` - Annualized std dev (252 trading days)
  - `calculate_max_drawdown()` - Peak-to-trough percentage loss
  - `get_moving_averages()` - MA50, MA200 (handles null for < 50/200 data points)
  - `generate_insights()` - Human-readable analysis (e.g., "Strong uptrend")
  - `normalize_metrics()` - **KEY FUNCTION** converts internal names to friendly names:
    - `1Y_total_return` → `1Y Return`
    - `volatility` → `Volatility`
    - `max_drawdown` → `Max Drawdown`

**Important:** All metrics returned use friendly names for consistency

### src/screening.py
**Purpose:** Rank and filter stocks  
**Main Functions:**
- `generate_screening_report(all_metrics)` - Prints rankings (top 10 by return, volatility, etc.)
- `save_screening_results(all_metrics)` - Writes output/screening_results.csv

**Metrics Used:**
- "1Y Return" - Top performers
- "Volatility" - Most stable
- "Market Cap (B)" / "Forward PE" - Size & valuation
- "Dividend Yield" - Income stocks

### api.py
**Purpose:** FastAPI REST server  
**Key Features:**
- ✅ All endpoints have try-catch + logging
- ✅ All ticker inputs validated (format, length)
- ✅ Graceful partial failures (failed tickers returned in response)
- ✅ Timeout handling & cache fallback
- ✅ File upload validation (type, size, content)
- ✅ Cache-Control headers on GET endpoints
- ✅ Restricted CORS (not wildcard)

**Current Limitations:**
- ❌ No rate limiting (user could spam refresh)
- ❌ No request queuing (parallel calls conflict)
- ❌ All responses unfiltered (no pagination)
- ❌ No async jobs (blocks for 2-3 minutes)

### main.py
**Purpose:** CLI execution for batch analysis  
**Flow:**
1. Load 502 tickers (or 5 if DEV_MODE)
2. Download SPY benchmark data
3. Loop: download → analyze → save metrics
4. Generate screening report + charts
5. Save results to CSV

---

## 🔄 CURRENT STATE & KNOWN ISSUES

### ✅ What's Working

| Feature | Status | Notes |
|---------|--------|-------|
| Stock data download | ✅ | Finnhub API, caches in CSV |
| Return calculations | ✅ | 1Y/3Y/5Y total & annualized |
| Volatility + Drawdown | ✅ | Proper annualization, handles zero |
| Moving averages | ✅ | Returns None if insufficient data |
| Company info | ✅ | Market cap, PE, dividend yield |
| Screening metrics | ✅ | Rankings by return, risk, etc. |
| Chart generation | ✅ | Price + MA50/MA200 |
| Error handling | ✅ | All endpoints have try-catch |
| Input validation | ✅ | Ticker format & length checked |
| API caching | ✅ | Cache-Control headers added |
| CORS security | ✅ | Restricted to configured origins |
| DEV_MODE toggle | ✅ | Configurable via environment |
| Null handling | ✅ | Moving averages, volatility safe |
| Partial failures | ✅ | Failed tickers tracked & returned |

### ❌ What Needs Fixing (Priority Order)

**CRITICAL (Breaks App):**
1. **TypeScript Type Safety** - Frontend interfaces don't match API responses
   - Issue: `info` can be null but interface says required
   - Fix: Update interfaces in `frontend/src/app/analytics/page.tsx`

2. **Error Boundaries** - Frontend crashes go blank
   - Issue: No error UI, just white screen
   - Fix: Add `<ErrorBoundary>` wrappers

**HIGH (Buggy):**
3. **Date parsing timezone** - Off-by-one day possible
   - Issue: `new Date(d.Date).toLocaleDateString()`
   - Fix: Use ISO format, specify timezone

4. **Duplicate analytics** - Logic in both main.py and api.py
   - Issue: Bug fixes needed in 2 places
   - Fix: Consolidate to single function

**MEDIUM (Performance/UX):**
5. **Rate limiting** - No spam protection
   - Fix: Use `slowapi` or custom decorator

6. **Request queuing** - Parallel refresh calls conflict
   - Fix: Use global lock (asyncio.Lock)

7. **Pagination** - Returns all 100 stocks
   - Fix: Add ?limit=10&offset=0 query params

8. **Async screening** - Blocks frontend for 2-3 minutes
   - Fix: Use FastAPI BackgroundTask, return job ID

9. **Server-side sorting** - All filtering client-side
   - Fix: Add ?sort=field&order=asc query params

**LOW (Nice to Have):**
10. PDF regex robustness - Pattern doesn't match all formats
11. Search/filter in screener UI - No way to find tickers
12. Global state management - Each component fetches independently

---

## 📐 METRICS REFERENCE

### Normalized Column Names (Used Everywhere)

**Returns:**
- `1Y Return` - 1-year total return percentage
- `1Y Annualized Return` - Annualized equivalent
- `3Y Return`, `3Y Annualized Return`
- `5Y Return`, `5Y Annualized Return`

**Risk:**
- `Volatility` - Annualized standard deviation
- `Max Drawdown` - Peak-to-trough loss

**Fundamentals:**
- `Market Cap (B)` - Billions of dollars
- `Forward PE` - Price-to-earnings ratio
- `Dividend Yield` - Annual dividend as % of price
- `Profit Margin` - Net profit as % of revenue
- `Revenue Growth` - YoY revenue growth

**Technical:**
- `MA50` - 50-day moving average
- `MA200` - 200-day moving average

**Qualitative:**
- `insights` - List of strings (e.g., ["Strong uptrend", "High volatility"])

---

## 🛠️ DEVELOPMENT GUIDELINES

### Adding a New Feature (Step-by-Step)

#### 1. Backend API Endpoint

**Do:**
```python
@app.get("/api/new-endpoint/{ticker}")
def new_endpoint(ticker: str, limit: int = Query(10, ge=1, le=100)):
    """
    Description of what this does.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL")
        limit: Number of results (1-100)
    
    Returns:
        JSON response with normalized column names
    """
    try:
        ticker = ticker.upper()
        
        # Input validation
        if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker")
        
        # Business logic
        results = process_data(ticker, limit)
        
        # Error handling
        if not results:
            raise HTTPException(status_code=404, detail=f"No data for {ticker}")
        
        # Response with cache headers
        return JSONResponse(
            content={"results": results},
            headers={"Cache-Control": "public, max-age=300"}  # 5 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in new_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Don't:**
- ❌ Use generic exception handling (catch Exception without logging)
- ❌ Forget input validation
- ❌ Return raw objects (use JSONResponse for headers)
- ❌ Skip error messages (users need to know what went wrong)
- ❌ Hardcode cache times (use constants)

#### 2. Analytics Function

**Do:**
```python
def new_metric(df):
    """Calculate new metric from price data.
    
    Args:
        df: DataFrame with 'Close' column
    
    Returns:
        float or None if insufficient data
    """
    if df is None or len(df) < 10:
        return None
    
    try:
        # Safe operations
        values = df['Close'].dropna()
        result = calculate_something(values)
        
        # Handle edge cases
        if result is None or np.isnan(result) or np.isinf(result):
            return None
        
        return float(result)
    except Exception as e:
        logger.warning(f"Could not calculate metric: {e}")
        return None
```

**Then update normalize_metrics():**
```python
def normalize_metrics(metrics: dict) -> dict:
    # Add mapping for new metric
    if "new_metric" in metrics:
        metrics["New Metric"] = metrics.pop("new_metric")
    return metrics
```

#### 3. Frontend Component

**Do:**
```typescript
import { useEffect, useState } from 'react';

interface ApiResponse {
    results: Array<{
        ticker: string;
        metric: number | null;  // Allow null
    }>;
    error?: string;  // Optional error message
}

export default function NewComponent() {
    const [data, setData] = useState<ApiResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            
            try {
                const res = await fetch('/api/new-endpoint/SPY');
                
                if (!res.ok) {
                    throw new Error(`API error: ${res.statusText}`);
                }
                
                const json = await res.json();
                setData(json);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error');
            } finally {
                setLoading(false);
            }
        };
        
        fetchData();
    }, []);
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div className="text-red-500">Error: {error}</div>;
    if (!data) return <div>No data</div>;
    
    return (
        <div>
            {data.results.map(r => (
                <div key={r.ticker}>
                    {r.ticker}: {r.metric ?? 'N/A'}
                </div>
            ))}
        </div>
    );
}
```

**Don't:**
- ❌ Assume API always returns data (add null checks)
- ❌ Forget loading/error states
- ❌ Hardcode API URLs
- ❌ Skip error messages to user

### Testing Your Feature

```bash
# Backend
python main.py                    # Run CLI batch
python -c "from src.analytics import new_metric; import pandas as pd; df = pd.read_csv('ticker_data/AAPL.csv'); print(new_metric(df))"

# Frontend
cd frontend && npm run dev       # Start dev server
# Visit http://localhost:3000

# API
curl http://localhost:8000/api/new-endpoint/AAPL

# Full validation
export DEV_MODE=True && python main.py  # Should work
export DEV_MODE=False && python main.py # Should work with all 502
```

### Code Style

**Python:**
- Use type hints: `def func(x: str) -> dict:`
- Log debug info: `logger.info(f"Processed {ticker}")`
- Handle None gracefully: `if val is not None:`
- Use f-strings: `f"Error: {err}"`

**TypeScript:**
- Define interfaces before use
- Allow null in types: `field: string | null`
- Use `const` by default, `let` rarely
- Arrow functions: `() => {}`

**General:**
- Keep functions < 30 lines
- One responsibility per function
- Comment WHY, not WHAT
- Use environment variables for config

---

## 🚀 FEATURE IDEAS (Ready to Implement)

### Quick Wins (1-2 hours each)
- [ ] Add PE ratio to screener sorts
- [ ] Export screening results to Excel
- [ ] Add company name/sector filtering
- [ ] Stock comparison tool (AAPL vs MSFT side-by-side)
- [ ] 52-week high/low tracking

### Medium Features (2-4 hours each)
- [ ] Watchlist saving (localStorage)
- [ ] Alert thresholds (email when stock hits price)
- [ ] Technical indicator overlay (RSI, MACD)
- [ ] Historical sharpe ratio trend
- [ ] Peer comparison (vs sector average)

### Advanced Features (4+ hours each)
- [ ] DCF valuation model
- [ ] Options pricing integration
- [ ] ML stock prediction
- [ ] Real-time streaming data
- [ ] Multi-portfolio support

---

## 📞 SUPPORT & DEBUGGING

### Common Issues

**"Invalid API key"**
→ Set `FINNHUB_API_KEY` in .env file (get free key at https://finnhub.io)

**"Screening data not found"**
→ Run `POST /api/screening/refresh` to generate initial data

**"TypeError: cannot format None as percentage"**
→ Chart component needs null checks (use `value ?? 'N/A'`)

**Frontend shows blank page**
→ Check browser console for errors (missing error boundary)

**Program only processes 5 tickers**
→ Set `DEV_MODE=False` in .env file for production mode

### Debug Commands

```bash
# Check installed packages
pip list | grep -E "finnhub|fastapi|pandas"

# Test API directly
curl -s http://localhost:8000/api/stocks | python -m json.tool

# Check cache files
ls -lh ticker_data/ | head -20

# Monitor logs
tail -f output/screening_results.csv

# Validate Python code
python -m py_compile src/analytics.py
```

---

## 📋 BEFORE SUBMITTING A PR

1. ✅ Code runs without errors
2. ✅ New features tested locally (main.py + api.py + frontend)
3. ✅ Error handling added (try-catch + logging)
4. ✅ Input validation done
5. ✅ Comments added (WHY not WHAT)
6. ✅ No hardcoded values (use config or env vars)
7. ✅ Null checks added (nothing crashes on None)
8. ✅ TypeScript types updated (frontend)
9. ✅ API documented (docstring with examples)
10. ✅ Commit message clear and descriptive

---

## 🎓 LEARNING PATH

**To understand this codebase:**

1. **Start here:** Read PROGRAM_ANALYSIS.md for architecture overview
2. **Data flow:** Trace one ticker through main.py (MMM example)
3. **Analytics:** Study src/analytics.py (how metrics are calculated)
4. **API:** Look at api.py (how frontend gets data)
5. **Frontend:** Check frontend/src/app/page.tsx (what data is displayed)
6. **Issues:** Review FULLSTACK_ANALYSIS.md for known bugs

**Time estimate:** 4-6 hours to fully understand how everything connects

---

## 📞 QUESTIONS?

Refer to:
- **Architecture:** PROGRAM_ANALYSIS.md
- **Known bugs:** FULLSTACK_ANALYSIS.md
- **API setup:** API_SETUP_GUIDE.md
- **Roadmap:** frontend_roadmap.md

Or examine the code - it's heavily commented!

---

**Last Updated:** March 16, 2026  
**Maintainer:** Jarvis Development Team  
**Version:** 1.0.0-beta
