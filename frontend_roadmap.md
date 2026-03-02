# Task Breakdown: Fiscal AI 2.0 Frontend

## Phase 8: API Bridge (The Backend)
- [x] Initialize FastAPI project structure
- [x] Create endpoint `/api/stocks` (returns ticker list)
- [x] Create endpoint `/api/analysis/{ticker}` (integrates with `analytics.py`)
- [x] Create endpoint `/api/screening` (integrates with `screening.py`)
- [x] Create endpoint for fetching Matplotlib charts as static assets

## Phase 9: Dashboard Core (UI Foundation)
- [x] Initialize Next.js project with Tailwind CSS
- [x] Setup "Premium Analytics" theme (Dark mode, Inter font)
- [x] Build Main Layout (Sidebar + Top Navigation)
- [x] Implement Ticker Search with autocomplete

## Phase 10: Stock Intelligence View
- [ ] Create "Stock Overview" cards (Return, Volatility, PE)
- [ ] Integrate interactive charting library (e.g., Recharts)
- [ ] Implement "Analyst Notes" section with glassmorphism styling
- [ ] Add "Benchmark Comparison" toggle (Stock vs SPY)

## Phase 11: Screening & Discovery Hub
- [ ] Build interactive Data Table for batch results
- [ ] Implement sorting by returns, yield, and margins
- [ ] Add visual "Scorecards" for top 3 daily performers
- [ ] Create CSV export button on the frontend

## Phase 12: Filing Viewer (Elite)
- [ ] Create section for uploading 10-K/10-Q PDFs
- [ ] Build "Extracted Sections" reader (Risk Factors, MD&A)
- [ ] Implement text highlighting for key financial keywords
- [ ] Add "AI Summary" overlay
