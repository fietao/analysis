# JARVIS ROADMAP v2.0 — Template-Driven Stock Analysis Platform

**Last Updated:** March 16, 2026  
**Status:** In Development - Phase 0 (Foundation)  
**Vision:** A flexible, production-grade analysis platform where users can analyze stocks using pre-built professional templates (Damodaran, Buffett, Technical, etc.) or create their own custom styles.

---

## 🎯 Core Vision

```
User selects template (or creates new one)
        ↓
System fetches all required data with citations
        ↓
Calculation engine runs all formulas
        ↓
Template renders organized, beautiful report
        ↓
User can switch styles or save as new template
```

**Key Principle:** Calculations ≠ Presentation. The same WACC, DCF, ROIC functions work for ALL templates.

---

## 📊 Folder Structure (v2.0 - ORGANIZED)

```
jarvis-stock-analysis/
├── docs/                              # All documentation
│   ├── README.md                      # Main guide
│   ├── ROADMAP_v2.md                  # This file
│   ├── TEMPLATE_SCHEMA.md             # Template design spec
│   ├── FULLSTACK_ANALYSIS.md          # Original bug analysis
│   ├── FULLSTACK_PROMPT.md            # Complete project guide
│   ├── AI_PROMPT_TEMPLATE.md          # How to ask AI for help
│   └── QUICK_REFERENCE.md             # Developer cheat sheet
│
├── src/                               # Backend Python code
│   ├── __init__.py
│   ├── config.py                      # Global settings (DEV_MODE, API keys)
│   │
│   ├── core/                          # CORE CALCULATION ENGINE (Shared by all templates)
│   │   ├── __init__.py
│   │   ├── calculator.py              # WACC, DCF, ROIC, ROE, metrics
│   │   ├── metrics.py                 # All metric formulas (in next phase)
│   │   └── validator.py               # Data validation (in next phase)
│   │
│   ├── templates/                     # TEMPLATE ENGINE
│   │   ├── __init__.py
│   │   ├── engine.py                  # TemplateRegistry, TemplateRenderer
│   │   ├── templates.py               # Template utilities (in next phase)
│   │   └── narrative_generator.py     # Generate Thai/English narratives (Phase 2)
│   │
│   ├── data/                          # DATA HANDLING
│   │   ├── __init__.py
│   │   ├── fetcher.py                 # Fetch from Finnhub, SEC, Yahoo (in next phase)
│   │   ├── normalizer.py              # Normalize column names
│   │   └── cache.py                   # Cache layer (in next phase)
│   │
│   ├── api/                           # API ENDPOINTS
│   │   ├── __init__.py
│   │   ├── routes.py                  # All endpoints (/api/v1/analyze/{ticker}?template=X)
│   │   └── middleware.py              # Error handling, CORS, logging
│   │
│   ├── analytics.py                   # [KEEP FOR NOW] Legacy analytics (deprecate Phase 3)
│   ├── screening.py                   # [KEEP] Screening logic
│   ├── data_loader.py                 # [KEEP] Live data fetching
│   │
│   └── legacy/                        # Old code (document_processor, visualizer, etc)
│       ├── document_processor.py
│       ├── financials.py
│       ├── visualizer.py
│       └── timer_helper.py
│
├── frontend/                          # Next.js + React + TypeScript (No major changes Phase 0-1)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── tests/                             # Tests
│   ├── __init__.py
│   ├── test_calculator.py             # Test WACC, DCF, etc
│   ├── test_templates.py              # Test template loading/rendering
│   ├── test_api.py                    # Test endpoints
│   └── test_analytics.py              # Original tests (moved here)
│
├── config/                            # Configuration files
│   ├── .env.example                   # Template for environment variables
│   ├── development.yaml               # Dev config
│   └── templates/                     # ALL TEMPLATE CONFIGS (JSON)
│       ├── damodaran_jet.json         # Flagship: Thai Damodaran analysis
│       ├── buffett_moat.json          # [Phase 3] Competitive moat focus
│       ├── technical_swing.json       # [Phase 3] Price-action focus
│       ├── simple_one_page.json       # [Phase 3] Quick snapshot
│       └── README.md                  # How templates work
│
├── output/                            # Generated analysis reports
│   └── .gitkeep
│
├── input/                             # User uploads, filings
│   ├── filings/
│   └── .gitkeep
│
├── .env                               # [GIT IGNORED] Local secrets
├── .env.example                       # Template for .env
├── .gitignore                         # Git exclusions
├── .git/                              # Git repository
├── requirements.txt                   # Python dependencies
├── main.py                            # Entry point (ENHANCED in Phase 0)
├── api.py                             # API server (REFACTORED in Phase 0)
└── README.md                          # Main readme
```

---

## 🚀 PHASE BREAKDOWN

### **PHASE 0: Foundation & Cleanup (Days 1–2) ✅ IN PROGRESS**

**Goal:** Stabilize core systems and build foundation for templates.

**Tasks:**
- [x] Reorganize folder structure (completed)
- [x] Delete bloat (ticker_data CSVs will be fetched live, not stored)
- [x] Create core calculation engine (`src/core/calculator.py`)
- [x] Create template engine (`src/templates/engine.py`)
- [x] Create first template config (`config/templates/damodaran_jet.json`)
- [ ] Upgrade `main.py` to use template system
- [ ] Refactor `api.py` with single `/api/v1/analyze/{ticker}?template=X` endpoint
- [ ] Fix all trailing slash + validation issues
- [ ] Ensure Python path works (src imports properly)

**Deliverable:** Running `python main.py` returns structured JSON with template rendered.

---

### **PHASE 1: Integration & Core Enhancements (Days 3–6)**

**Goal:** Connect template system to real data and calculations.

**Tasks:**
- [ ] Create data fetcher (`src/data/fetcher.py`) to pull from Finnhub + SEC
- [ ] Create data normalizer (`src/data/normalizer.py`) - single unified column names for all templates
- [ ] Implement caching layer (`src/data/cache.py`)
- [ ] Build calculation results aggregator (runs all required calculations for template)
- [ ] Implement narrative generator (`src/templates/narrative_generator.py`) - rule-based Thai narratives
- [ ] Build full API integration
- [ ] Add input validation + error handling for all calculations
- [ ] Comprehensive test suite (`tests/`)

**Deliverable:**
```bash
GET /api/v1/analyze/AAPL?template=damodaran_jet
→ Returns full analysis JSON with:
  - All calculations (WACC, DCF, ROIC, etc.)
  - Narrative commentary
  - Chart configurations
  - Source citations for every number
```

---

### **PHASE 2: Damodaran Template Polish & AI (Days 7–10)**

**Goal:** Make the Damodaran template production-ready with professional output.

**Tasks:**
- [ ] Implement all 18 calculations exactly to your Damodaran/JET specs
- [ ] Thai narrative generation (full sentences, story-style, no bullet points)
- [ ] Color-coded decision card (เขียว/ส้ม/แดง with MOS conditions)
- [ ] Citation system - every number shows data source + fetch date
- [ ] Chart rendering (waterfall DCF, revenue trend, sensitivity heatmap, etc.)
- [ ] PDF export with professional styling
- [ ] HTML export for web viewing
- [ ] Integration with frontend (display in React components)
- [ ] AI-assisted narrative generation (GPT-4) for better Thai text

**Deliverable:** Users type ticker → Get professional Thai Damodaran analysis report.

---

### **PHASE 3: Extensibility & Custom Templates (Days 11–15)**

**Goal:** Enable users to create their own analysis styles.

**Tasks:**
- [ ] Template Studio UI (simple web interface to edit templates)
- [ ] Duplicate existing template → customize sections/charts
- [ ] Save custom templates (stored in database or local JSON)
- [ ] Multi-template analysis (analyze same stock in 3 different styles)
- [ ] Template versioning (track changes)
- [ ] Community templates (optional: share templates with other users)

**Additional Templates to Add:**
- `buffett_moat.json` - Focus on competitive advantages, ROIC vs WACC gap
- `technical_swing.json` - Price patterns, moving averages, RSI, MACD
- `simple_one_page.json` - Quick snapshot (no DCF, just key metrics)
- `esg_deep_dive.json` - ESG scores, sustainability, governance
- `quarterly_update.json` - For tracking recent earnings + guidance

**Deliverable:** Users can duplicate Damodaran template, remove DCF section, add custom charts, save as "My Value Style v1", use to analyze stocks.

---

### **PHASE 4: Rich Graphing & Visualization (Days 16–18)**

**Goal:** Add interactive charts and comparison tools.

**Tasks:**
- [ ] Modal/side panel chart viewer
- [ ] Multiple time-frame support (1Y, 3Y, 5Y, 10Y, All)
- [ ] Vs benchmark comparisons (SPY, sector average, etc.)
- [ ] Interactivity: click metric → show related charts
- [ ] Export charts as images
- [ ] Chart builder (let users customize which charts to show)

**Deliverable:** Click "Revenue" in report → Modal opens showing revenue 1Y/3Y/5Y/10Y trends + vs peers.

---

## 🔄 Implementation Priority

**What gets built FIRST (ensures everything works):**
1. Calculator.py - All core formulas
2. Template engine - Load and render templates
3. Data fetcher - Get prices, financials, SEC data
4. API routes - Single `/analyze` endpoint
5. Damodaran template - First complete template

**What gets SECOND (makes it beautiful):**
1. Narrative generation - Thai story text
2. PDF/HTML export
3. Frontend integration
4. Charts + visualizations

**What gets THIRD (enables growth):**
1. Template Studio - User customization
2. Additional templates (Buffett, Technical, etc)
3. Advanced filtering and comparison

---

## 🛠️ Technical Details

### Data Flow for Any Analysis

```
1. Request: GET /api/v1/analyze/AAPL?template=damodaran_jet

2. System loads template:
   template = load_template("damodaran_jet")
   
3. Template declares what it needs:
   - 10 years of historical prices
   - 5 years of financials
   - Latest SEC filings
   - Market data (10yr treasury, sector multiples)
   
4. Data fetcher fetches EVERYTHING at once:
   prices = get_prices("AAPL", 10_years)
   financials = get_sec_data("AAPL", 5_years)
   market_data = get_market_data()
   
5. Calculation engine runs required formulas:
   wacc = calculator.calculate_wacc(...)
   fcff = calculator.calculate_fcff(...)
   dcf = calculator.calculate_dcf(...)
   mos = calculator.calculate_margin_of_safety(...)
   
6. Template renderer builds output:
   output = renderer.render_template(
     template=damodaran_jet,
     calculations={wacc, fcff, dcf, mos, ...},
     data={prices, financials, ...}
   )
   
7. Return JSON:
   {
     "template_id": "damodaran_jet",
     "sections": [
       {
         "id": "decision_card",
         "data": {intrinsic_value, current_price, mos, ...},
         "narrative": "Thai text here...",
         "charts": [...]
       },
       ...
     ],
     "sources": [
       {name: "SEC EDGAR", url: "...", fetch_time: "2026-03-16T14:30Z"},
       {name: "Finnhub", url: "...", fetch_time: "..."},
       ...
     ]
   }

8. Frontend renders JSON → HTML/PDF/Display
```

### Key Principles

✅ **Decoupling:** Calculator functions don't know about templates
✅ **Reuse:** Same WACC used by Damodaran, Buffett, Technical templates
✅ **Extensibility:** New template = new JSON file, no code changes
✅ **Transparency:** Every number links to source + timestamp
✅ **Null-safety:** Calculations gracefully handle missing data
✅ **Caching:** Data fetched once, reused by all calculations
✅ **Type Safety:** CalculationResult dataclass standardizes outputs

---

## 📋 Fixed Issues (From FULLSTACK_ANALYSIS.md)

**Critical (Phase 0):**
- ✅ Folder organization (done)
- ⏳ Trailing slash fix (in progress)
- ⏳ Single endpoint `/api/v1/analyze/{ticker}` (in progress)
- ⏳ Column naming normalization (Phase 1)
- ⏳ Error handling (Phase 1)
- ⏳ Input validation (Phase 1)

**High Priority (Phase 1):**
- ⏳ Null value handling in calculations
- ⏳ Rate limiting + request queuing
- ⏳ Async screening operations
- ⏳ TypeScript type safety (frontend)

**Medium Priority (Phase 2+):**
- PDF parsing robustness
- Global state management
- Pagination + server-side sorting

---

## 📚 Documentation Structure

**For Users:**
- `README.md` - "What is Jarvis and why I should use it"
- `docs/QUICK_START.md` - Get running in 5 minutes
- `docs/USER_GUIDE.md` - How to use templates (Phase 3)

**For Developers:**
- `docs/ARCHITECTURE.md` - System design overview
- `docs/API_REFERENCE.md` - All endpoints
- `docs/TEMPLATE_SCHEMA.md` - How to create templates
- `docs/DEV_GUIDE.md` - Step-by-step dev setup

**For AI Assistants:**
- `docs/FULLSTACK_PROMPT.md` - Complete project context
- `docs/AI_PROMPT_TEMPLATE.md` - How to ask for help
- `docs/QUICK_REFERENCE.md` - Cheat sheet

---

## 🎓 Development Checklist

**Before starting code:**
- [ ] Read TEMPLATE_SCHEMA.md
- [ ] Understand data flow diagram above
- [ ] Review existing `src/core/calculator.py`
- [ ] Review `src/templates/engine.py`
- [ ] Test folder structure is correct

**For each phase:**
- [ ] Create unit tests (`tests/`)
- [ ] Add docstrings + type hints
- [ ] Update docs
- [ ] Test locally with sample ticker
- [ ] Commit to git with clear message

---

## 📞 Questions to Answer Before Phase 1

1. **AI Narratives:** Should Phase 2 use GPT-4 for Thai text generation, or stick with rule-based templates?
2. **Export Formats:** Support PDF, HTML, JSON only in Phase 2, or add Excel?
3. **Caching:** Cache template configs in memory or reload from disk each request?
4. **Database:** Store custom templates in JSON files (simple) or SQLite (scalable)?
5. **Frontend:** Major redesign in Phase 2 to show template-based sections, or minimal changes?

---

## 🎯 Success Metrics

**Phase 0 Done:** ✅
```bash
python src/core/calculator.py
→ All CalculationResult objects returned correctly
→ No crashes on edge cases
```

**Phase 1 Done:**
```bash
python main.py
→ Returns full template-rendered analysis
→ All sections populated
→ Sources + timestamps included
```

**Phase 2 Done:**
```bash
GET /api/v1/analyze/AAPL?template=damodaran_jet&format=pdf
→ Professional PDF report in Thai generated
→ Color-coded decision card
→ All narratives in natural Thai
```

**Phase 3 Done:**
```bash
User: Duplicate Damodaran template
User: Remove DCF section
User: Save as "My Simple Value"
→ New template works for any ticker
```

---

## 🚀 Timeline

- **Week 1 (Mar 16-22):** Phase 0 + Phase 1
- **Week 2 (Mar 23-29):** Phase 2 (Damodaran polish)
- **Week 3 (Mar 30-Apr 5):** Phase 3 (Custom templates)
- **Week 4+ (Apr 6+):** Phase 4 (Charts) + Polish + Deployment

---

## 📦 Dependencies

**Python:**
- fastapi
- uvicorn
- pandas
- numpy
- requests
- python-dotenv

**Frontend:**
- Next.js 16+
- React 19
- TypeScript
- Tailwind CSS

**External APIs:**
- Finnhub (stock prices, fundamentals)
- SEC EDGAR (filings, financial data)
- Yahoo Finance (additional data)

---

**Status:** In development | **Next Step:** Phase 0 completion → Phase 1 Data Fetcher
