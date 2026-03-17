# Jarvis Stock Analysis Platform v2.0

**Quick Links:** [Full Docs](./docs/) | [Roadmap](./docs/ROADMAP_v2.md) | [API Reference](./docs/API_REFERENCE.md)

---

## 🎯 What is Jarvis?

A professional **template-driven stock analysis platform** that generates comprehensive financial reports in multiple styles.

**Templates Include:**
- 🇹🇭 **Damodaran (Thai)** - Full DCF valuation with narrative
- 💪 **Buffett Moat** - Competitive advantage analysis  
- 📈 **Technical Swing** - Price-action focused
- ⚡ **Simple One-Pager** - Quick snapshot
- ➕ Create your own custom templates

**Key Insight:** Same calculation engine, infinite presentation styles.

---

## 🚀 60-Second Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp config/.env.example .env
# Edit .env with your API keys

# 3. Run
python main.py

# 4. Analyze
# Browser: http://localhost:3000
# API: curl "http://localhost:8000/api/v1/analyze/AAPL?template=damodaran_jet"
```

---

## 📁 What's Inside

```
jarvis/
├── docs/                    ← ALL documentation
│   ├── ROADMAP_v2.md       ← Development plan (phases, timeline)
│   ├── TEMPLATE_SCHEMA.md  ← How to create templates
│   ├── QUICK_REFERENCE.md  ← Dev cheat sheet
│   └── ...
├── src/                    ← Backend (Python)
│   ├── core/               ← Calculation engine (WACC, DCF, etc)
│   ├── templates/          ← Template loader + renderer
│   ├── data/               ← Data fetcher + normalizer
│   ├── api/                ← API routes
│   └── config.py
├── config/templates/       ← Template configs (JSON)
├── frontend/               ← React + Next.js
├── tests/                  ← Test suite
├── main.py                 ← Entry point
└── api.py                  ← API server
```

---

## 🏗️ Architecture Overview

```
Request: analyze AAPL with Damodaran template
    ↓
Load template config
    ↓
Fetch: prices, financials, market data
    ↓
Run calculations: WACC, DCF, ROIC, Margins
    ↓
Generate Thai narrative
    ↓
Render: JSON + charts + citations
    ↓
Output: JSON, PDF, or HTML
```

**Design Principle:** Calculations are decoupled from presentation. Add a new formula → automatically available to all templates.

---

## 📊 Current Status

**Phase 0: Foundation** ✅ COMPLETE
- ✅ Reorganized folder structure
- ✅ Created calculation engine (`src/core/calculator.py`)
- ✅ Created template system (`src/templates/engine.py`)
- ✅ First template config (`damodaran_jet.json`)
- ✅ Roadmap with 4 development phases

**Phase 1: Integration** ⏳ IN PROGRESS
- ⏳ Data fetcher (Finnhub, SEC, Yahoo)
- ⏳ Template integration with main.py
- ⏳ Unified API endpoint

---

## 📚 Documentation

Start with these files in `docs/`:

| File | Purpose | Time |
|------|---------|------|
| **ROADMAP_v2.md** | Full development roadmap + phases | 20 min |
| **QUICK_REFERENCE.md** | Developer cheat sheet + examples | 10 min |
| **TEMPLATE_SCHEMA.md** | How templates work + how to create | 15 min |
| **README.md** (in docs) | Complete setup + architecture | 15 min |

---

## 💡 How Templates Work

Every template is just a **JSON configuration**:

```json
{
  "template_id": "damodaran_jet",
  "sections": [
    {
      "id": "decision_card",
      "required_calculations": ["wacc", "dcf", "margin_of_safety"],
      "display_fields": [...],
      "narrative_requirements": {...}
    }
  ]
}
```

**System automatically:**
1. Loads template JSON
2. Fetches required data
3. Runs required calculations  
4. Renders output
5. Returns JSON/PDF/HTML

---

## 🛠️ Development

**For Phase 1 work:** See `docs/ROADMAP_v2.md`

**Common tasks:**
```bash
# Run verification
python verify_setup.py

# Run tests
python -m pytest tests/

# Start development
python main.py
```

**Key files to understand:**
- `src/core/calculator.py` - All calculation logic
- `src/templates/engine.py` - Template loading + rendering  
- `config/templates/damodaran_jet.json` - Example template

---

## 🎯 Current Features

**Calculation Engine:**
- WACC (Weighted Average Cost of Capital)
- DCF (Discounted Cash Flow) valuation
- ROE, ROIC, Profit margins
- Volatility + Sharpe ratio
- Margin of Safety
- P/E ratios + multiples

**Template System:**
- Load any template by ID
- Render sections + narratives
- Generate charts configuration
- Track data sources

**Coming Soon (Phase 1+):**
- Live data fetching (Finnhub, SEC)
- Thai narrative generation
- PDF/HTML export
- Custom template creation
- Multi-template comparison

---

## 🤝 Contributing

**Before making changes:**
1. Read `docs/ROADMAP_v2.md`
2. Check what phase you're working on
3. See `docs/QUICK_REFERENCE.md` for patterns

**After making changes:**
- Update relevant docs
- Add tests
- Commit with clear message
- Push to GitHub

---

## 📞 Getting Help

**Understanding the code:**
- `docs/TEMPLATE_SCHEMA.md` - Design explanation
- `docs/ROADMAP_v2.md` - Architecture overview
- `src/core/calculator.py` - Heavily commented

**Asking AI for help:**
- Use `docs/AI_PROMPT_TEMPLATE.md` as starting point
- Provide context from `docs/FULLSTACK_PROMPT.md`

**Issues or questions:**
- Check `docs/QUICK_REFERENCE.md`
- Search existing commits: `git log --oneline`

---

## 📋 Project Timeline

| Week | Phase | Goal |
|------|-------|------|
| Week 1 | 0 + 1 | Core system + data integration |
| Week 2 | 2 | Damodaran template polish |
| Week 3 | 3 | Custom template support |
| Week 4+ | 4 | Charts + visualization |

---

## 📦 Tech Stack

**Backend:**
- FastAPI (API server)
- Pandas (data processing)
- NumPy (calculations)

**Frontend:**
- Next.js 16+ (React)
- TypeScript
- Tailwind CSS

**Data:**
- Finnhub API (prices, fundamentals)
- SEC EDGAR (filings, metrics)
- Yahoo Finance (additional data)

---

## 🔗 Quick Links

- 📖 [Full Documentation](./docs/)
- 🗺️ [Development Roadmap](./docs/ROADMAP_v2.md)
- 🏗️ [Architecture Guide](./docs/TEMPLATE_SCHEMA.md)
- ⚡ [Quick Reference](./docs/QUICK_REFERENCE.md)
- 💬 [AI Prompt Template](./docs/AI_PROMPT_TEMPLATE.md)

---

**Status:** Pre-Alpha | **Phase:** 0/4 Complete | **Last Updated:** March 16, 2026

---

See `docs/ROADMAP_v2.md` for detailed development plan.
