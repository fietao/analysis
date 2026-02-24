# Fiscal AI 2.0 🚀

**Fiscal AI 2.0** is an elite, modular stock analysis engine designed to transform raw financial data into actionable analyst insights. It combines high-performance Python analytics with a modern, premium web dashboard.

---

## 🌟 Key Features

### 📊 Professional Analytics
- **Return Math**: 1Y, 3Y, and 5Y Total & Annualized returns.
- **Risk Metrics**: Annualized Volatility and Peak-to-Trough Max Drawdown.
- **Technical Indicators**: 50-day and 200-day Moving Averages.
- **Fundamentals**: PE Ratios, Dividend Yields, Profit Margins, and Revenue Growth.

### 🧠 Intelligent Insights
- **Rule-Based Interpretation**: Automatically identifies trends, momentum shifts, and risk profiles.
- **Analyst Notes**: Human-readable descriptions of a stock's current state.

### 🖼️ Advanced Visualizations
- **Price Action**: Price overlaid with moving averages.
- **Risk Curves**: Historical drawdown visualizations.
- **Benchmarking**: Performance comparison against the S&P 500 (SPY).
- **Cluster Analysis**: Risk vs. Return scatter plots for batch comparisons.

### 📂 Elite Document Ingestion
- **SEC Filing Analysis**: Automatically extracts "Risk Factors" and "Management Discussion" from 10-K/10-Q PDFs.

### 🖥️ Modern Web Dashboard
- **FastAPI Backend**: High-speed REST API bridge.
- **Next.js Frontend**: Premium dark-themed dashboard built with Tailwind CSS and Framer Motion.

---

## 🏗️ Project Structure

```bash
├── src/                    # Core Analytical Logic
│   ├── analytics.py        # Financial formulas & Insight engine
│   ├── data_loader.py      # yfinance integration & Metadata fetching
│   ├── visualizer.py       # Matplotlib charting engine
│   ├── screening.py        # Batch ranking & Filtering logic
│   └── document_processor.py # PDF extraction logic
├── frontend/               # Next.js Web Application
├── api.py                  # FastAPI REST Server
├── main.py                 # CLI Version of the tool
├── ticker_list.csv         # List of tickers to analyze (NASDAQ 100)
├── ticker_data/            # Local CSV cache of price history
├── output/                 # Generated charts and screening reports
└── input/filings/          # Folder for uploading 10-K/10-Q PDFs
```

---

## 🚀 Getting Started

### 1. Backend Setup
```bash
# Install dependencies
pip install pandas yfinance matplotlib PyPDF2 fastapi uvicorn

# Run the CLI version
python main.py

# OR Start the API server
python api.py
```

### 2. Frontend Setup (Dashboard)
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

---

## 🛠️ Requirements
- **Python 3.8+**
- **Node.js 18+**
- **yfinance**
- **Pandas & NumPy**

---

## 🎓 Development Roadmap
- [x] Phase 1-6: Core Engine & Scaling
- [x] Phase 7: Document Ingestion
- [x] Phase 8: API Bridge
- [x] Phase 9: UI Foundation
- [ ] Phase 10: Interactive Charts
- [ ] Phase 11: Screening Hub
- [ ] Phase 12: AI Summary Integration

---

*“Built with precision. Designed for insights.”*