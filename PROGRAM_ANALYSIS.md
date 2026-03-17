# Jarvis Stock Analysis Program - Comprehensive Analysis

## 🎯 Executive Summary

**Jarvis** is a professional-grade stock analysis engine combining:
- **Advanced Python analytics** backend with financial metrics calculation
- **FastAPI REST API** for data serving
- **Next.js web dashboard** with modern UI/UX
- **SEC filing intelligence** for document processing
- **Real-time data sourcing** via yfinance

The program analyzes stock performance, fundamentals, valuations, and risk metrics across a portfolio (currently NASDAQ 100 stocks).

---

## 📊 Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────────┐
│         Frontend (Next.js)                  │ ← User Interface
│  Analytics | Screener | Filings Dashboard  │
└────────────────────┬────────────────────────┘
                     │ HTTP REST API
┌────────────────────▼────────────────────────┐
│      Backend (FastAPI)                      │ ← API Bridge
│  /api/stocks, /api/analysis, /api/screening│
└────────────────────┬────────────────────────┘
                     │ Python Core
┌────────────────────▼────────────────────────┐
│  Core Analytics Engine (Python)             │ ← Business Logic
│  • Data Loading (yfinance)                  │
│  • Metrics Calculation                      │
│  • Screening & Ranking                      │
│  • Visualization (Matplotlib)               │
│  • Document Processing (PyPDF2)             │
└─────────────────────────────────────────────┘
```

---

## 🔧 Backend Components (Python)

### 1. **Data Layer** (`src/data_loader.py`)
- **Primary Source**: yfinance (Yahoo Finance API)
- **Functions**:
  - `download_stock_data()` - Fetches OHLCV data from 2004-01-01 to present
  - `get_stock_info()` - Retrieves fundamental metrics (PE, dividend yield, margins, debt-to-equity, ROE)
- **Output**: Pandas DataFrames cached as CSV in `ticker_data/` folder
- **Cache Strategy**: 2-day staleness threshold before refresh

### 2. **Analytics Engine** (`src/analytics.py`)
Core financial calculations:

| Metric | Calculation | Purpose |
|--------|-----------|---------|
| **Returns** | 1Y, 3Y, 5Y total & annualized | Performance measurement |
| **Volatility** | Daily returns std dev × √252 | Risk measurement |
| **Max Drawdown** | Peak-to-trough decline % | Downside risk |
| **Moving Averages** | 50-day, 200-day MA | Trend analysis |
| **Fundamentals** | PE, Dividend Yield, Profit Margin, Revenue Growth | Valuation |

Key Functions:
- `calculate_annualized_return()` - Converts total return to annual %
- `calculate_volatility()` - Annualized volatility (252 trading days)
- `calculate_max_drawdown()` - Maximum historical decline
- `calculate_returns()` - Multi-period returns calculation

### 3. **Screening & Ranking** (`src/screening.py`)
Batch analysis of multiple stocks:
- **Top 1Y Performers** - Highest returns
- **Most Stable** - Lowest volatility
- **Best Risk-Adjusted** - Return/Risk ratio (Sharpe-like)
- **Highest Dividend Yield**
- **Best Profitability** - Profit margins
- Outputs ranked comparison tables

### 4. **Visualization** (`src/visualizer.py`)
Matplotlib-based charting:
- `plot_price_with_ma()` - Price + 50/200-day moving averages
- `plot_drawdown()` - Historical drawdown curve
- `plot_risk_return_scatter()` - Risk vs Return scatter (batch comparison)
- All outputs saved as PNG in `output/charts/`

### 5. **SEC Document Processing** (`src/document_processor.py`)
- Extracts Risk Factors and Management Discussion from 10-K/10-Q PDFs
- Uses PyPDF2 for text extraction + regex pattern matching
- Stores insights keyed by ticker
- Located in `input/filings/` folder

### 6. **Configuration** (`src/config.py`)
- Loads ticker list from `ticker_list.csv` (NASDAQ 100)
- Sets date range: 2004-01-01 to present
- **DEV_MODE**: Limits analysis to 5 tickers for testing
- Auto-loads ~100 tickers from CSV

### 7. **Financials** (`src/financials.py`)
- Historical financial data extraction
- Cash flow analysis for red flag detection
- Valuation models (DCF)

---

## 🌐 Backend API (FastAPI)

### Key Endpoints

**File**: `api.py`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/stocks` | GET | Returns list of all tickers |
| `/api/analysis/{ticker}` | GET | Detailed analysis for single stock |
| `/api/screening` | GET | Batch screening report |
| `/api/financials/{ticker}` | GET | Historical financials & red flags |
| `/api/valuation/{ticker}` | GET | DCF valuation & intrinsic value |
| `/upload-filing` | POST | Upload SEC PDFs for analysis |
| `/charts/{ticker}` | GET | Retrieve generated chart images |

### Cache Management
- **Strategy**: 2-day staleness check
- `is_cache_stale()` - Checks last date in CSV vs. current date
- `ensure_live_data()` - Downloads fresh data if stale or force_refresh=true

### CORS Configuration
- Allows Next.js frontend to access API (localhost:3000)

---

## 💻 Frontend (Next.js + TypeScript)

### Technology Stack
- **Framework**: Next.js 16.1.6
- **UI Library**: React 19.2.3
- **Styling**: Tailwind CSS 4
- **Charts**: Recharts 3.7.0
- **Icons**: Lucide React
- **Animations**: Framer Motion

### Project Structure
```
frontend/src/
├── app/
│   ├── layout.tsx (Main template)
│   ├── page.tsx (Home/Dashboard)
│   ├── analytics/
│   │   └── [ticker]/ (Deep dive stock analysis)
│   ├── screener/
│   │   └── page.tsx (Batch screening interface)
│   └── filings/
│       └── page.tsx (SEC document upload/analysis)
├── components/
│   ├── Sidebar.tsx (Navigation)
│   ├── TopNav.tsx (Header)
│   └── ... (Other UI components)
└── globals.css (Tailwind styles)
```

### Key Pages

1. **Dashboard (Home)** - Overview of market analysis
2. **Analytics Page** - Deep-dive for individual stock
   - Returns/Volatility/Drawdown cards
   - Moving average charts
   - Fundamental metrics
   - Analyst notes
3. **Screener Hub** - Batch comparison table
   - Sortable metrics
   - Top 3 performer cards
   - One-click drill-down to analytics
4. **Filings Intelligence** - Document upload/processing
   - Upload 10-K/10-Q PDFs
   - Extracted Risk Factors
   - Management Discussion summary
   - Red flag alerts

---

## 📈 Key Features & Workflow

### Workflow: Full Analysis Pipeline

```
1. Load Tickers (ticker_list.csv → config.py)
        ↓
2. Download Data (yfinance → ticker_data/*.csv)
        ↓
3. Calculate Metrics (analytics.py)
        ↓
4. Generate Visualizations (visualizer.py → output/charts/)
        ↓
5. Batch Screening (screening.py → comparison report)
        ↓
6. Optional: Process Filings (document_processor.py)
        ↓
7. Serve via API (api.py ← backend endpoints)
        ↓
8. Display on Dashboard (Next.js frontend)
```

### Entry Points

**CLI Mode**: `python main.py`
- Runs full analysis pipeline
- Generates all charts and reports
- Saves to `output/` folder

**API Server**: `python api.py`
- Starts FastAPI on http://localhost:8000
- Serves real-time data endpoints

**Frontend**: `cd frontend && npm run dev`
- Launches Next.js on http://localhost:3000
- Connects to API backend

---

## 📁 Directory Structure

```
stock-analysis-program/
├── src/                           # Core Python analytics
│   ├── analytics.py              # Financial calculations
│   ├── data_loader.py            # yfinance integration
│   ├── screening.py              # Batch ranking
│   ├── visualizer.py             # Matplotlib charts
│   ├── document_processor.py      # PDF extraction
│   ├── financials.py             # SEC data & valuation
│   └── config.py                 # Configuration & tickers
├── frontend/                     # Next.js web dashboard
│   ├── src/app/                 # Pages
│   ├── src/components/          # UI Components
│   ├── public/                  # Static assets
│   └── package.json
├── api.py                        # FastAPI server
├── main.py                       # CLI entry point
├── ticker_data/                  # CSV cache (100 stocks)
├── ticker_list.csv               # Ticker configuration
├── output/                       # Generated outputs
│   ├── charts/                  # PNG visualizations
│   └── screening_results.csv    # Batch report
├── input/filings/               # SEC 10-K/10-Q PDFs
└── README.md
```

---

## 🔌 Data Flow Examples

### Example 1: Single Stock Analysis
```
Request: GET /api/analysis/AAPL
  ↓
1. Load from cache (ticker_data/AAPL.csv)
2. If stale, download fresh data from yfinance
3. Calculate: returns, volatility, drawdown, MA50/200
4. Fetch fundamentals: PE, dividend yield, margins
5. Return JSON response with all metrics
  ↓
Frontend renders: Cards, Charts, Tables
```

### Example 2: Batch Screening
```
Request: GET /api/screening
  ↓
1. Loop through all ~100 tickers
2. Load/download data for each
3. Calculate metrics
4. Generate ranking tables (by return, volatility, etc.)
5. Return table data as JSON
  ↓
Frontend renders: Sortable data table, Top 3 cards
```

### Example 3: SEC Filing Analysis
```
User Action: Upload 10-K PDF for MSFT
  ↓
1. POST /upload-filing (file + ticker)
2. Extract text from PDF
3. Identify sections: Risk Factors, MD&A
4. Store insights in filing_insights[ticker]
5. Return extracted sections to UI
  ↓
Frontend displays: Risk highlights, MD&A summary
```

---

## 🚀 Development Roadmap Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1-6 | Core Engine & Scaling | ✅ Complete |
| 7 | Document Ingestion | ✅ Complete |
| 8 | API Bridge | ✅ Complete |
| 9 | UI Foundation | ✅ Complete |
| 10 | Analytics Hub | ✅ Complete |
| 11 | Screening Hub | ✅ Complete |
| 12 | AI Summary Integration | ✅ Complete |
| 13 | SEC XBRL Data (Financials) | ✅ Complete |
| 14 | Red Flag Detection | ✅ Complete |
| 15 | DCF Valuation Modeling | ✅ Complete |

---

## 🔍 Strengths & Architecture Benefits

1. **Modular Design** - Each component (analytics, viz, screening) is independently testable
2. **Caching Strategy** - CSV cache + staleness detection minimizes API calls
3. **REST API** - Frontend agnostic; API can serve other clients
4. **Real-Time Data** - yfinance integration with configurable refresh
5. **Professional Visualizations** - Matplotlib for publication-quality charts
6. **Document Intelligence** - SEC filing extraction for regulatory insights
7. **Performance Metrics** - Multi-period returns, risk metrics, fundamental ratios
8. **Batch Processing** - Screen entire portfolio efficiently
9. **TypeScript Frontend** - Type-safe React with Next.js modern stack
10. **Scalable** - Can add new metrics/indicators without core changes

---

## ⚠️ Considerations & Potential Improvements

### Current Limitations
1. **Real-time Updates** - API refreshes on 2-day staleness cadence
2. **PDF Processing** - Regex-based; may miss some section variations
3. **Single Factor Models** - Screening uses individual metrics (could add composites)
4. **No Alerts** - No notification system for price/metric thresholds
5. **Manual Ticker Updates** - ticker_list.csv requires manual refresh

### Potential Enhancements
1. **Real-time WebSockets** - Live price/metric updates
2. **ML-based Insights** - Anomaly detection, predictive models
3. **Alternative Data** - Add sentiment analysis, insider transactions
4. **Portfolio Optimization** - Mean-variance optimization engine
5. **Regulatory Alerts** - Automatic 8-K/earnings notifications
6. **Advanced Charts** - TradingView-like candlestick charts
7. **Database Backend** - Move from CSV to PostgreSQL
8. **Authentication** - User accounts, watchlists, saved screens

---

## 📊 Technologies Summary

### Backend
- **Language**: Python 3.8+
- **Web Framework**: FastAPI
- **Data Processing**: Pandas, NumPy
- **Data Source**: yfinance
- **Visualization**: Matplotlib
- **Document Processing**: PyPDF2
- **Financial Data**: edgartools (for SEC XBRL)

### Frontend
- **Framework**: Next.js 16.1.6
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: React 19
- **Charts**: Recharts
- **Animations**: Framer Motion
- **Icons**: Lucide React

### Deployment Ready
- ✅ Python dependencies: `pip install pandas yfinance matplotlib PyPDF2 fastapi uvicorn`
- ✅ Node dependencies: `npm install` (frontend)
- ✅ Configuration files: `tsconfig.json`, `next.config.ts`, `postcss.config.mjs`

---

## 🎓 Usage Quick Start

```bash
# 1. Backend Setup
pip install pandas yfinance matplotlib PyPDF2 fastapi uvicorn

# 2. Start API Server
python api.py
# Runs on http://localhost:8000

# 3. Frontend Setup
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000

# 4. CLI Mode (if needed)
python main.py
```

---

## 📝 Conclusion

**Jarvis** is a sophisticated, production-ready stock analysis platform combining quantitative analysis with financial fundamentals and regulatory intelligence. The modular architecture supports both real-time API-driven clients and batch analysis workflows, making it suitable for both retail investors and institutional analysis environments.

The program demonstrates professional software engineering practices: separation of concerns, caching strategies, type safety (TypeScript), REST API patterns, and comprehensive metric calculation.

---

**Last Updated**: March 16, 2026
