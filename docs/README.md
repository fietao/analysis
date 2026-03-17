# Jarvis - Template-Driven Stock Analysis Platform

**Version:** 2.0.0  
**Status:** In Development (Phase 0: Foundation)

---

## 🎯 What is Jarvis?

Jarvis is a professional stock analysis platform that uses **pluggable analysis templates**. The same underlying data and calculations power multiple analysis styles:

- **Damodaran Style** (Thai) - Comprehensive DCF valuation with narrative
- **Buffett Moat Analysis** - Competitive advantages + ROIC focus  
- **Technical Swing** - Price patterns + technical indicators
- **Simple One-Pager** - Quick snapshot
- **...and any custom style you create**

**Key Innovation:** Calculations are **decoupled from presentation**. Add a new formula → it's automatically available to all templates.

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.11+
Node.js 18+ (for frontend)
API Keys: FINNHUB_API_KEY, SEC_EDGE_API_KEY
```

### Setup (5 minutes)

1. **Clone and install:**
```bash
cd jarvis-stock-analysis
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

2. **Configure environment:**
```bash
cp config/.env.example .env
# Fill in your API keys in .env
```

3. **Run backend:**
```bash
python main.py
```

4. **Run frontend (in another terminal):**
```bash
cd frontend
npm run dev
```

5. **Analyze a stock:**
```bash
# Damodaran template (Thai analysis)
curl "http://localhost:8000/api/v1/analyze/AAPL?template=damodaran_jet"

# Or simple one-pager
curl "http://localhost:8000/api/v1/analyze/AAPL?template=simple_one_page"
```

---

## 📁 Folder Structure

```
jarvis/
├── docs/                        # Complete documentation
│   ├── ROADMAP_v2.md           # Development roadmap
│   ├── TEMPLATE_SCHEMA.md      # How templates work
│   ├── FULLSTACK_ANALYSIS.md   # Bug analysis
│   └── ...
├── src/                        # Backend Python
│   ├── core/                   # Calculation engine (WACC, DCF, ROIC, etc)
│   ├── templates/              # Template loading + rendering
│   ├── data/                   # Data fetching + caching
│   ├── api/                    # API routes
│   └── config.py
├── config/
│   └── templates/              # Template JSON configs
│       ├── damodaran_jet.json
│       ├── buffett_moat.json
│       └── ...
├── frontend/                   # Next.js React app
├── tests/                      # Test suite
├── main.py                     # Entry point
├── api.py                      # API server
└── requirements.txt

```

---

## 🏗️ Architecture

```
Request for Analysis
    ↓
Load Template Config (JSON)
    ↓
Fetch Required Data (with caching)
    ↓
Run All Required Calculations
    ↓
Generate Narratives
    ↓
Render Charts
    ↓
Return Structured JSON
    ↓
Frontend/PDF Export
```

**Every template shares:**
- Same calculation engine
- Same data fetcher
- Same normalization

**Every template can have:**
- Different sections
- Different narratives  
- Different charts
- Different styling

---

## 📚 Documentation

**Start here:**
- `docs/ROADMAP_v2.md` - Complete development plan
- `docs/QUICK_REFERENCE.md` - Developer cheat sheet
- `docs/TEMPLATE_SCHEMA.md` - How to create templates

**For detailed context:**
- `docs/FULLSTACK_PROMPT.md` - Complete project guide
- `docs/AI_PROMPT_TEMPLATE.md` - How to ask AI for help
- `docs/FULLSTACK_ANALYSIS.md` - Original bug analysis

---

## 🔧 Current Status (Phase 0)

**Completed:**
- ✅ Folder reorganization
- ✅ Removed bloat (ticker_data CSVs, redundant files)
- ✅ Created `src/core/calculator.py` with all core formulas
- ✅ Created `src/templates/engine.py` (TemplateRegistry, TemplateRenderer)
- ✅ Created first template config: `damodaran_jet.json`
- ✅ Created `ROADMAP_v2.md` with complete Phase plans

**In Progress:**
- ⏳ Integrate template system with main.py
- ⏳ Create data fetcher (Finnhub, SEC, Yahoo)
- ⏳ Upgrade API with `/api/v1/analyze` endpoint

**Next (Phase 1):**
- Data fetcher + normalizer
- Full template integration
- Test suite

---

## 💡 How It Works

### For Users
1. Choose a template (or use default: Damodaran Thai)
2. Enter a ticker symbol
3. Get professional analysis report
4. Switch templates to see different perspectives
5. (Phase 3) Create custom templates

### For Developers

**Adding a new calculation method:**
```python
# In src/core/calculator.py
def calculate_my_metric(self, ...):
    return CalculationResult(
        value=result,
        formula="My formula here",
        inputs={...},
        source="my_formula",
        fetch_timestamp=self.timestamp
    )

# That's it! All templates can now use it
```

**Adding a new template:**
1. Create `config/templates/my_template.json`
2. Specify which sections + charts to show
3. System automatically loads it

---

## 🎯 Current Template (Damodaran)

The flagship template provides:

**Sections:**
1. **Decision Card** - Buy/Hold/Sell with Margin of Safety
2. **Valuation Summary** - DCF + Comparables
3. **Financial Metrics** - Historical ROE, ROIC, Growth
4. **Why Priced This Way** - Market sentiment analysis
5. **Bull & Bear Case** - Investment thesis
6. **Appendix** - Detailed calculations
7. **Sources** - Every number traced back

**Calculations:**
- WACC (Weighted Avg Cost of Capital)
- DCF Intrinsic Value
- Margin of Safety  
- ROE, ROIC, Profit Margins
- P/E Ratio + Multiples
- Technical indicators (volatility, Sharpe ratio)

**Output:**
- JSON (for APIs)
- HTML (for web)
- PDF (professional report)
- Thai narrative (story-style, not bullets)

---

## 🚀 Development Phases

| Phase | Duration | Goal | Deliverable |
|-------|----------|------|-------------|
| 0 | 2 days | Foundation | Template system working, calculator ready |
| 1 | 4 days | Integration | Full template rendering with real data |
| 2 | 4 days | Polish Damodaran | Production-ready Thai analysis |
| 3 | 5 days | Extensibility | Template Studio for custom styles |
| 4 | 3 days | Visualization | Interactive charts |

---

## 📞 Getting Help

**For understanding the codebase:**
- Read `docs/ROADMAP_v2.md` (15 min)
- Review `src/core/calculator.py` (30 min)
- Check `config/templates/damodaran_jet.json` (10 min)

**For asking AI to help:**
- Use `docs/AI_PROMPT_TEMPLATE.md` as a starting point
- Copy relevant context from `docs/FULLSTACK_PROMPT.md`
- Specify which issue or feature

**For development questions:**
- See `docs/QUICK_REFERENCE.md`
- Check commit history: `git log --oneline -20`

---

## 🔄 Next Steps

1. **Complete Phase 0:** Integrate core systems with main.py
2. **Phase 1:** Build data fetcher
3. **Phase 2:** Polish Damodaran template
4. **Phase 3:** Enable custom templates

---

## 📄 License

[Add your license here]

---

**Questions?** See `docs/QUICK_REFERENCE.md` or check `docs/ROADMAP_v2.md` for detailed roadmap.
