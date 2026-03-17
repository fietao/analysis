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

## 🎮 PHASE 5: Engagement Layer & Gamification (Days 19–25)

**Goal:** Make Jarvis addictive through engagement, not manipulation. Build habit-forming features that provide real value.

**Tasks - Gamification System:**
- [ ] User profiles + username system
- [ ] Badge system ("Analyst", "Researcher", "Sector Expert", etc.)
- [ ] Ranking system (global + sector-specific leaderboards)
- [ ] Points/streaks (research activity, analysis completions)
- [ ] Achievement unlocks (e.g., "Analyzed 100 different tickers")
- [ ] Personal score card (user dashboard showing rank, badges, activity)
- [ ] Community competition (monthly portfolio challenge, prediction accuracy)
- [ ] Watchlist system (save stocks, track performance vs predictions)
- [ ] Portfolio tracker (hypothetical P&L simulation)

**Tasks - Personal AI Assistant:**
- [ ] Context-aware chat interface
- [ ] Stock Q&A ("Why did Jensen Huang's compensation spike?")
- [ ] Narrative explanation ("Explain this DCF calculation in simple terms")
- [ ] Analysis suggestions ("Based on AAPL trend, should I look at MSFT too?")
- [ ] Learning mode ("Teach me about P/E ratios")
- [ ] Memory system (remember user preferences, watchlist, cached questions)
- [ ] Integration with Damodaran analysis (AI explains the numbers)

**Tasks - Specialized Stock AI:**
- [ ] Company executive knowledge base (CEO biography, strategy, track record)
- [ ] Sector-specific insights (NVIDIA deep dive example: chip cycle, competition, geopolitics)
- [ ] Competitor analysis (NVIDIA vs AMD vs QCOM - real-time comparison)
- [ ] Industry trend synthesis (pull news, earnings, analyst reports)
- [ ] Moat analysis (understand competitive advantages)
- [ ] Risk factor summarization (what could go wrong?)

**Tasks - Video Integration:**
- [ ] Video library structure (company stories, educational, analyst insights)
- [ ] Video hosting (YouTube API integration or self-hosted)
- [ ] Educational video series (P/E ratios, market cycles, technical analysis)
- [ ] Company story videos (15-60 sec clips of CEO/earnings highlights)
- [ ] Community video features (users share stock pitches)
- [ ] Video transcripts + searchability
- [ ] Gamification: "Watch 5 videos → unlock Learner badge"

**Deliverable:** User opens app → sees rank, badges, daily streak → watches short video → asks AI about it → gets points → climbs leaderboard.

---

## 💰 PHASE 6: Freemium Monetization (Days 26–30)

**Goal:** Sustainable revenue model that rewards engagement and honest value.

**Tasks - Tier System:**

**FREE TIER:**
- [ ] Basic stock screener (top 20 results)
- [ ] Company fundamentals + news
- [ ] Educational videos (3/day limit)
- [ ] Personal AI (2 questions/day)
- [ ] Gamification (badges, leaderboards)
- [ ] Watchlist (max 10 stocks)
- [ ] Access to Damodaran template (read-only)

**PREMIUM TIER ($9.99-$14.99/month):**
- [ ] Unlimited screening + custom filters
- [ ] Unlimited personal AI assistant
- [ ] Priority analytics (faster refresh)
- [ ] Unlimited video access
- [ ] Advanced indicators (RSI, MACD, Bollinger Bands)
- [ ] Export data (Excel, CSV, PDF)
- [ ] Portfolio tracker (hypothetical trading)
- [ ] No ads, dark mode
- [ ] Early access to new templates

**PRO TIER ($49.99+/month):**
- [ ] Everything in Premium
- [ ] Real-time alerts (price, earnings, news)
- [ ] Sector deep-dive AI (detailed competitor analysis)
- [ ] API access (developers can integrate Jarvis)
- [ ] Custom report templates (create your own)
- [ ] Multi-portfolio support (track separate strategies)
- [ ] Priority support (direct chat)
- [ ] Portfolio sync with brokers (coming soon)

**Tasks - Implementation:**
- [ ] Authentication system (sign up, login, profiles)
- [ ] Payment integration (Stripe, PayPal)
- [ ] Subscription management (cancel, upgrade, downgrade)
- [ ] Feature gating (show/hide features by tier)
- [ ] Free trial system (7-day premium trial)
- [ ] Usage tracking (count AI questions, video views, etc.)
- [ ] Upsell prompts (contextual "Upgrade to Premium" when hitting limits)

**Tasks - Analytics & Growth:**
- [ ] Track conversion metrics (free → premium rate)
- [ ] Monitor churn rate (cancellations)
- [ ] A/B test upsell messages
- [ ] Email campaigns (re-engagement for inactive users)
- [ ] Referral rewards ("Invite friend → both get 1 month free")

**Deliverable:** Seamless free experience that converts to paid when users see value.

---

## 🔄 Integration Plan: How Engagement + Templates Work Together

**User Flow:**
```
1. User signs up (Free tier)
   ├─ Welcome tutorial + first badge
   ├─ Access to Damodaran template
   └─ Gets 2 AI questions + day

2. User searches AAPL
   ├─ Sees Damodaran analysis + video (Company story)
   ├─ Clicks video → earns 10 points
   └─ Asks AI "Why should I care?" → uses 1 question

3. User views MSFT analysis
   ├─ Sees competitor comparison vs AAPL (Template feature)
   ├─ Asks specialized AI "MSFT vs NVIDIA chips?" → uses 1 question
   ├─ Adds to watchlist → progress toward "Researcher" badge
   ├─ Hits AI question limit for day
   └─ System suggests "Upgrade to Premium for unlimited!"

4. User upgrades → Premium
   ├─ Unlimited AI access
   ├─ Can watch unlimited educational videos
   ├─ Can now create custom templates
   └─ Joins weekly portfolio challenge leaderboard

5. Each interaction:
   ├─ Earns points (badges, leaderboard rank)
   ├─ Builds habit (daily streak)
   └─ Increases LTV (longer engagement = less likely to churn)
```

---

## 📊 Engagement Metrics (Track These)

| Metric | Target | Why |
|--------|--------|-----|
| **DAU/MAU** | >60% (daily/monthly) | Habit formation |
| **Avg session length** | >15 min | Engagement |
| **Stocks analyzed/week** | >5 per user | Value discovery |
| **Free → Premium conversion** | >8% | Revenue |
| **Premium churn** | <5%/month | Retention |
| **Badge completion rate** | >40% | Gamification works |
| **AI question usage** | >50% of limit | AI adds value |
| **Video completion rate** | >60% | Content quality |

---

## 🔄 Implementation Priority

**Phase 0-2 (CORE - Template-Driven Analysis):**
1. Calculator.py - All core formulas
2. Template engine - Load and render templates
3. Data fetcher - Get prices, financials, SEC data
4. API routes - Single `/analyze` endpoint
5. Damodaran template - First complete template
6. Narrative generation - Thai story text
7. PDF/HTML export
8. Frontend integration

**Phase 3-4 (EXTENSIBILITY - User Customization):**
1. Template Studio - User customization
2. Additional templates (Buffett, Technical, ESG, etc)
3. Advanced charting + comparisons
4. Multi-template analysis

**Phase 5-6 (ENGAGEMENT & MONETIZATION - Growth):**
1. User auth + profiles (foundation)
2. Gamification (badges, ranks, points)
3. AI assistant (start with GPT-4 API)
4. Video integration (YouTube API)
5. Premium tier system
6. Payment integration (Stripe)

**Recommended Order BY IMPACT:**
- ✅ Do Phases 0-2 first (without analysis, engagement is pointless)
- ✅ Do Phase 5 (engagement) before Phase 3-4 (content is more important than templates at start)
- ✅ Do Phase 6 (monetization) once you have 50K+ users engaging
- ✅ Do Phase 3-4 (extensibility) when users ask "Can I add my own analysis?"

**Rationale:**
- Core analysis → builds user trust
- Engagement → creates habit
- Monetization → sustains team
- Extensibility → scales with community

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

## 📞 Key Questions to Answer

**Phase 1-3 (Analysis):**
1. **AI Narratives:** Should Phase 2 use GPT-4 for Thai text generation, or stick with rule-based templates?
2. **Export Formats:** Support PDF, HTML, JSON only in Phase 2, or add Excel?
3. **Caching:** Cache template configs in memory or reload from disk each request?
4. **Database:** Store custom templates in JSON files (simple) or SQLite (scalable)?
5. **Frontend:** Major redesign in Phase 2 to show template-based sections, or minimal changes?

**Phase 5-6 (Engagement & Monetization):**
1. **Database:** SQLite (simple, local) or PostgreSQL (scalable, cloud-ready)?
2. **LLM for AI:** GPT-4, Claude, or open-source (cost vs quality)?
3. **Video Hosting:** YouTube API integration, Vimeo, or self-hosted?
4. **Badge Algorithm:** Time-based, achievement-based, or Elo-rating system?
5. **Pricing Model:** Fixed ($9.99/mo) or usage-based (pay per analysis)?
6. **Free Trial:** 7 days, 14 days, or limited features forever?
7. **Payment Processor:** Stripe, Paddle, Apple Pay, or multi-provider?
8. **Launch Type:** Web-only first, or simultaneous iOS/Android apps?

---

## 🎯 Success Metrics by Phase

**Phase 0-2 Done (Core Analysis):**
```
✅ GET /api/v1/analyze/AAPL?template=damodaran_jet&format=pdf
→ Professional Thai Damodaran report generated
→ All 18 calculations correct
→ Narratives in natural Thai
→ Decision card with color coding
```

**Phase 3-4 Done (Customization):**
```
✅ User can duplicate template
✅ User can create custom template
✅ Same ticker analyzed in 3 different styles
✅ Charts compare metrics across templates
```

**Phase 5 Done (Engagement):**
```
✅ Users have profiles + badges
✅ Top 10 users visible on leaderboard
✅ AI chat works (50+ Q&A)
✅ Videos integrated + watchable
✅ Points + streaks tracking
✅ >60% DAU/MAU ratio
✅ >15 min avg session
```

**Phase 6 Done (Monetization):**
```
✅ Free tier: 20 analyses/month, 2 AI questions/day
✅ Premium tier: Unlimited, real-time alerts
✅ Payment processing live (Stripe)
✅ >8% free → premium conversion
✅ <5% monthly churn
✅ First $50K MRR
```

---

## 📊 User Engagement Tracking (Phase 5+)

**Database Events to Track:**
| Event | Value | Purpose |
|-------|-------|---------|
| `analysis_viewed` | analysis_id | Track research interest |
| `video_watched` | video_id, duration | Content engagement |
| `ai_question_asked` | question_text | AI usage + value |
| `badge_earned` | badge_id | Gamification success |
| `watchlist_added` | ticker | Interest tracking |
| `premium_upgraded` | subscription_id | Revenue conversion |
| `portfolio_position_added` | ticker, qty | Involvement level |

**Metrics Dashboard (Internal):**
- Weekly active users (WAU)
- Daily active users (DAU)
- Session duration trends
- Conversion funnel (free → premium)
- Churn rate by cohort
- AI question volume
- Video completion rate
- Badge distribution

---

## 💻 Tech Stack - Phase 5-6 Additions

**Backend (Python):**
```
✅ fastapi, uvicorn              (existing)
✅ pandas, numpy                 (existing)
+ sqlalchemy                    (ORM for database)
+ alembic                       (database migrations)
+ pydantic                      (data validation)
+ passlib, python-jose          (JWT authentication)
+ openai                        (GPT-4 API for AI)
+ stripe                        (payment processing)
+ python-multipart              (file uploads)
```

**Frontend (TypeScript/React):**
```
✅ Next.js 16+, React 19         (existing)
✅ Tailwind CSS 4                (existing)
+ zustand or redux              (state management)
+ react-query                   (API data fetching)
+ chart.js                      (engagement charts)
+ iframe-resizer                (embed videos)
```

**Infrastructure:**
```
✅ Uvicorn                       (existing)
+ PostgreSQL                    (scalable database)
+ Redis                         (caching + rate limiting)
+ Docker                        (containerization)
+ AWS/GCP/Railway               (hosting)
+ Stripe API                    (payments)
+ OpenAI API                    (AI assistant)
+ YouTube API                   (videos)
```

---

## 📁 New Folder Structure (With Engagement Support)

```
src/
├── auth/
│   ├── __init__.py
│   ├── models.py                 # User, Subscription models
│   ├── security.py               # JWT, password hashing
│   └── routes.py                 # /auth/signup, /auth/login
│
├── engagement/
│   ├── __init__.py
│   ├── gamification.py           # Badges, points, leaderboard logic
│   ├── ai_assistant.py           # Personal AI + specialized stock AI
│   ├── video_service.py          # Video fetching + tracking
│   └── events.py                 # Track user events (viewed, watched, etc)
│
├── payments/
│   ├── __init__.py
│   ├── stripe_service.py         # Stripe integration
│   ├── subscription.py           # Premium tier logic
│   └── routes.py                 # /payments/subscribe, /payments/webhook
│
├── core/                         (existing)
├── templates/                    (existing)
├── data/                         (existing)
│
├── api/
│   ├── routes.py                 # Include all endpoint groups
│   │ ├─ /api/analysis           (existing)
│   │ ├─ /api/auth               (new: auth)
│   │ ├─ /api/user               (new: profiles, badges)
│   │ ├─ /api/ai                 (new: chat)
│   │ ├─ /api/videos             (new: video list)
│   │ ├─ /api/leaderboard        (new: rankings)
│   │ └─ /api/subscription       (new: premium)
│   └── middleware.py
│
└── models/
    ├── __init__.py
    ├── database.py               # SQLAlchemy setup
    ├── user.py                   # User, Badge, Subscription models
    ├── engagement.py             # Event, Portfolio models
    └── analysis.py               # SavedAnalysis, Template models
```

---

## 🚀 Go-to-Market Strategy (Phase 6+)

**Launch Phase (Week 1-2):**
- Beta: 100 early users (friends, forums, Reddit)
- Feedback: Collect via in-app survey
- Iterate: Fix bugs, improve UX

**Growth Phase (Month 2-3):**
- Content marketing: Blog posts ("How to analyze stocks")
- YouTube: Analysis walkthroughs, stock education
- Communities: Reddit, Discord, Twitter
- Referral program: "Invite friend → both get 1 month free"

**Retention Phase (Ongoing):**
- Email campaigns (weekly insights, new features)
- In-app notifications (badge unlocked, stock alert)
- Premium perks (exclusive analysis templates)
- Community features (user-generated stock pitches)

**Target Metrics:**
- Month 1: 1K free users
- Month 3: 10K free users
- Month 6: 100K free users
- Month 12: 500K users, 50K premium (10% conversion)

---

## 📞 Support & Community

**For Users:**
- Help Center (FAQ + video tutorials)
- In-app chat support (Phase 5)
- Email support (support@jarvis.app)
- Discord community (share ideas, ask questions)

**For Developers:**
- GitHub discussions (feature ideas, bug reports)
- Documentation (detailed API + template guides)
- Contributing guidelines (how to submit pull requests)
- Monthly dev meeting (community + roadmap discussion)

---

## ✅ Pre-Launch Checklist

**Legal & Compliance:**
- [ ] Terms of Service written
- [ ] Privacy Policy (GDPR, CCPA compliant)
- [ ] Investor disclaimer (not financial advice)
- [ ] Data security audit
- [ ] Accessibility audit (WCAG 2.1)

**Technical:**
- [ ] All endpoints tested (unit + integration)
- [ ] Database backups automated
- [ ] Error logging working (Sentry or similar)
- [ ] Performance tested (100+ concurrent users)
- [ ] SSL certificate installed
- [ ] CDN for assets (fast global delivery)

**Product:**
- [ ] Onboarding tutorial complete
- [ ] Error messages user-friendly
- [ ] Mobile responsive
- [ ] Dark mode working
- [ ] First 5 templates built + tested

**Marketing:**
- [ ] Landing page live
- [ ] Email list seeded (100+ signups)
- [ ] Social media profiles ready
- [ ] Launch announcement ready
- [ ] Press kit prepared

---

## 📚 Documentation Roadmap

**Phase 0-4 (Analysis Focus):**
- Architecture guide
- API reference
- Template schema
- Developer setup guide

**Phase 5-6 (Engagement Focus):**
- User guide (how to use gamification)
- AI assistant guide
- Premium features guide
- Community guidelines
- Content moderation policy

---

**Status:** Planning Phase 5-6 | **Next Step:** Complete Phase 0-2, then engage users | **Long-term Vision:** Market-leading AI-powered stock analysis platform with real community
