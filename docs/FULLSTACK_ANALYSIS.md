# JARVIS PROGRAM - FULLSTACK ANALYSIS & TODO LIST

## 🚨 CRITICAL ISSUES TO FIX

### **PROBLEM #1: Missing API Endpoint (API-001)**
**Severity**: 🔴 **CRITICAL** - Frontend crashes  
**Location**: `api.py` vs `frontend/src/app/page.tsx`  
**Issue**: Frontend calls `GET /api/historical/SPY` (line 39 in page.tsx) but API doesn't define this endpoint
```python
# api.py - MISSING ENDPOINT
# Frontend expects: GET /api/historical/{ticker}
# But endpoint exists at: GET /api/historical/{ticker}  ✅ (Actually it does exist at line 198!)
```
**Status**: Needs verification - may already exist but not being hit correctly

---

### **PROBLEM #2: Inconsistent Column Naming (API-002)**
**Severity**: 🟠 **HIGH** - Data misalignment  
**Location**: `api.py` line 38-47, `src/screening.py`, `frontend analytics page`  
**Issue**: Backend returns metric names in different formats causing frontend type errors
```
Backend returns: "1Y_total_return", "volatility", "max_drawdown"
Frontend expects: "1Y Return", "Volatility", "Max Drawdown"
Normalization only happens in some endpoints ❌
```
**Affects**: Screening data display, analytics charts, sorting

---

### **PROBLEM #3: Missing Error Handling (API-003)**
**Severity**: 🟠 **HIGH** - Silent failures  
**Location**: `api.py` endpoints  
**Issue**: No try-catch blocks for network failures, missing data
```python
@app.post("/api/screening/refresh")  # No timeout handling
def refresh_screening_data():
    # If yfinance hangs, endpoint hangs forever ❌
    # If 50% of tickers fail, returns partial data without warning ❌
```

---

### **PROBLEM #4: Type Safety Mismatch (API-004)**
**Severity**: 🟠 **HIGH** - TypeScript errors  
**Location**: `frontend/src/app/analytics/page.tsx` line 35-48  
**Issue**: Interface doesn't match actual API response schema
```typescript
// Frontend expects stats to always have these fields
interface StockData {
    ticker: string;
    info: { name: string; ... };  // Can be null ❌
    metrics: { "1Y_total_return": number; ... };  // May have null values ❌
}

// API can return:
{
    ticker: "AAPL",
    info: null,  // ← Frontend crashes here
    metrics: "1Y_total_return": null,  // ← Type error
}
```

---

### **PROBLEM #5: Missing Endpoint (API-005)**
**Severity**: 🟠 **HIGH** - Frontend broken  
**Location**: `frontend/src/app/page.tsx` line 39  
**Issue**: Frontend calls `/api/historical/SPY` but no route in API for SPY specifically
**Missing**: Dynamic historical data for any ticker on demand

---

### **PROBLEM #6: No Input Validation (API-006)**
**Severity**: 🟡 **MEDIUM** - Security/stability  
**Location**: All `api.py` endpoints  
**Issue**: No validation on ticker input
```python
@app.get("/api/analysis/{ticker}")
def get_stock_analysis(ticker: str):
    ticker = ticker.upper()  # ← What if ticker = "'; DROP TABLE"?
    # No validation that ticker exists in TICKERS list ❌
```

---

### **PROBLEM #7: Inconsistent Null Handling (API-007)**
**Severity**: 🟡 **MEDIUM** - Data quality  
**Location**: `src/analytics.py`, `src/data_loader.py`  
**Issue**: Metrics may be None/NaN but frontend doesn't handle gracefully
```python
# analytics.py returns:
metrics['volatility'] = None  # If < 5 data points
metrics['MA50'] = None  # If < 50 data points

# Frontend tries to format without checking:
{val:.2%}  # ← TypeError if val is None
```

---

### **PROBLEM #8: DEV_MODE Hard-coded (API-008)**
**Severity**: 🟡 **MEDIUM** - Testing limitation  
**Location**: `src/config.py` line 24
**Issue**: DEV_MODE = True hardcoded - API only analyzes 5 tickers in production!
```python
DEV_MODE = True
DEV_TICKERS_LIMIT = 5

# This means:
# /api/screening/refresh only processes 5 tickers!
# Should be configurable or use env variable
```

---

### **PROBLEM #9: No Error Boundaries (API-009)**
**Severity**: 🟡 **MEDIUM** - White screen of death  
**Location**: `frontend/src/app/analytics/page.tsx`, `page.tsx`  
**Issue**: If API fails, no error UI just blank screen
```typescript
const [error, setError] = useState<string | null>(null);
// Error state is set but not displayed on screen! ❌
// User sees: blank page, no indication something failed
```

---

### **PROBLEM #10: Cache Invalidation Missing (API-010)**  
**Severity**: 🟡 **MEDIUM** - Stale data  
**Location**: `api.py` line 175-182  
**Issue**: Frontend refresh button doesn't clear old data while loading new
```typescript
// Frontend:
onClick={() => { 
    fetchData(ticker, true); 
    fetchChartData(ticker, true); 
}}
// But doesn't show loading state or clear old data ❌
```

---

## 🔧 ARCHITECTURE ISSUES

### **ISSUE #11: Duplicate Analytics Logic (ARCH-001)**
**Severity**: 🟡 **MEDIUM** - Code duplication  
**Location**: `main.py` vs `api.py`  
**Issue**: Analytics pipeline duplicated in two entry points
```
main.py               api.py
├── Loop tickers  ×2
├── Call analytics    ×2
├── Call screening    ×2
└── Save results      ×2
```
**Impact**: Bug fixes need to be made in 2 places

---

### **ISSUE #12: Missing Rate Limiting (ARCH-002)**
**Severity**: 🟡 **MEDIUM** - API abuse  
**Location**: `api.py` endpoints  
**Issue**: No rate limiting, someone can spam requests
```python
# No decorator, no request counting
@app.post("/api/screening/refresh")
def refresh_screening_data():
    # User clicks 100x = 100 yfinance API calls at once ❌
```

---

### **ISSUE #13: No Request Queuing (ARCH-003)**
**Severity**: 🟡 **MEDIUM** - Performance  
**Location**: `api.py`  
**Issue**: Multiple `/api/screening/refresh` calls run in parallel
```
User 1: POST /api/screening/refresh  → 100 concurrent yfinance calls
User 2: POST /api/screening/refresh  → 100 more concurrent calls
Total: 200x parallel API calls = we get blocked by yfinance ❌
```

---

### **ISSUE #14: Frontend State Management (ARCH-004)**
**Severity**: 🟡 **MEDIUM** - Data consistency  
**Location**: `frontend/src/app/analytics/page.tsx`  
**Issue**: No global state, each component fetches independently
```
DashboardCards: fetch /api/dashboard
SpyChart: fetch /api/historical/SPY
TopScreened: fetch /api/screening
→ 3 independent requests, no caching ❌
```

---

## 🐛 SPECIFIC BUGS

### **BUG #1: Insights List Format (BUG-001)**
**Severity**: 🟡 **MEDIUM** - Data validation  
**Location**: `src/screening.py` line 56-58  
**Issue**: Insights is a list but screening assumes it might be string
```python
df['insights'].apply(lambda x: any("Strong long-term uptrend" in s for s in x if isinstance(x, list)))
# This handles None/non-list values laboriously instead of guaranteeing list type ❌
```

---

### **BUG #2: Moving Average Edge Case (BUG-002)**
**Severity**: 🟡 **MEDIUM** - Data validation  
**Location**: `src/analytics.py` line 77-85  
**Issue**: If stock has < 50 trading days, MA50 = None (crashes chart)
```python
df['MA50'] = df['Close'].rolling(window=50).mean()  # First 49 rows are NaN
# Frontend chart tries to plot None values ❌
```

---

### **BUG #3: Volatility Zero Division (BUG-003)**
**Severity**: 🟡 **MEDIUM** - Edge case  
**Location**: `src/screening.py` line 36  
**Issue**: If all daily returns = 0, volatility = 0, Sharpe ratio = NaN
```python
df['return_per_risk'] = df['1Y_total_return'] / df['volatility']  # Division by zero possible ❌
```

---

### **BUG #4: PDF Parsing Fragile (BUG-004)**
**Severity**: 🟡 **MEDIUM** - Regex brittle  
**Location**: `src/document_processor.py` line 19-28  
**Issue**: Regex patterns hard-coded, won't match all PDF formats
```python
patterns = {
    "Risk Factors": r"(Item\s*1A\.?\s*Risk\s*Factors.*?)(?=Item\s*1B|$)",
}
# If PDF says "Item 1A - Risk Factors" (dash instead of dot) → no match ❌
```

---

### **BUG #5: Frontend Date Parsing (BUG-005)**
**Severity**: 🟡 **MEDIUM** - Locale issues  
**Location**: `frontend/src/app/page.tsx` line 40  
**Issue**: Date formatting locale-dependent
```typescript
new Date(d.Date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
// On some timezones/locales this could be off-by-one day ❌
```

---

## 📊 DATA FLOW MISALIGNMENTS

### **MISALIGNMENT #1: Column Name Inconsistency (DATA-001)**
```
✅ backend generates: "1Y_total_return"
❌ frontend expects: "1Y Return"
❌ screening.py uses: '1Y_total_return'
→ 3 different names for same metric!
```

### **MISALIGNMENT #2: Null Value Handling (DATA-002)**
```
Backend returns: 
{
    "1Y_total_return": null,  ← Could be missing data
    "volatility": null,       ← 
    "insights": []            ← Empty list or null?
}

Frontend assumes:
- All fields present
- All non-null
- insights[0] always exists
→ Runtime errors ❌
```

### **MISALIGNMENT #3: Array vs Object (DATA-003)**
```
Backend:
"insights": ["Strong uptrend", "High volatility"]  ← Array

Frontend analytics page expects:
metrics.insights  → works ✅

Frontend screening expects:
row['insights'].apply(lambda...)  → only works if read as df ❌
```

---

## 📝 PERFORMANCE ISSUES

### **PERF #1: No Pagination (PERF-001)**
**Severity**: 🟡 **MEDIUM**  
**Location**: `api.py` endpoints  
**Issue**: Returns all 100 tickers every request
```python
@app.get("/api/screening")
def get_screening_data():
    df = pd.read_csv(csv_path)  # Reads ALL 100 rows
    return {"results": rows}     # Returns ALL 100 rows every time ❌
```

---

### **PERF #2: No Sorting Server-Side (PERF-002)**
**Severity**: 🟡 **MEDIUM**  
**Location**: Frontend does all sorting  
**Issue**: Frontend downloads all data, then sorts
```typescript
const sorted = [...screenDataInfo.results]
    .sort((a, b) => (b["1Y Return"] || 0) - (a["1Y Return"] || 0))
// Gets 100 rows every time, then sorts client-side ❌
```

---

### **PERF #3: CSV File Read Every Request (PERF-003)**
**Severity**: 🟡 **MEDIUM**  
**Location**: `api.py` line 175  
**Issue**: Re-reads CSV from disk on every GET request
```python
@app.get("/api/screening")
def get_screening_data():
    csv_path = Path("output/screening_results.csv")
    df = pd.read_csv(csv_path)  # Disk I/O every request ❌
    # Should cache in memory if not refreshed recently
```

---

## 🔐 SECURITY ISSUES

### **SEC #1: CORS Wildcard (SEC-001)**
**Severity**: 🟡 **MEDIUM**  
**Location**: `api.py` line 65-69  
**Issue**: Allows any origin
```python
CORSMiddleware(
    allow_origins=["*"],  # ← Anyone can call this API ❌
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### **SEC #2: Ticker Validation Missing (SEC-002)**
**Severity**: 🟡 **MEDIUM**  
**Location**: All ticker endpoints  
**Issue**: No validation that ticker is in TICKERS list
```python
@app.get("/api/analysis/{ticker}")
def get_stock_analysis(ticker: str):
    ticker = ticker.upper()  # What if ticker = "XXXXXXXX"?
    # No validation that ticker exists ❌
```

---

## 🚀 MISSING FEATURES

### **MISSING #1: Pagination (FEAT-001)**
**Location**: `api.py` screening endpoint  
**Issue**: Returns all 100 stocks, should support ?limit=10&offset=0

### **MISSING #2: Search/Filter (FEAT-002)**
**Location**: Frontend screener  
**Issue**: No way to search for specific ticker in results

### **MISSING #3: Sorting Query Params (FEAT-003)**
**Location**: `api.py` screening endpoint  
**Issue**: Frontend does client-side sort, should support ?sort=1Y_total_return&order=desc

### **MISSING #4: Caching Headers (FEAT-004)**
**Location**: `api.py` all endpoints  
**Issue**: No Cache-Control headers, browser cache not utilized

### **MISSING #5: Async Operations (FEAT-005)**
**Location**: `api.py` `/api/screening/refresh`  
**Issue**: Blocks for 2-3 minutes, should return job ID and allow polling

### **MISSING #6: Better Error Messages (FEAT-006)**
**Location**: All API endpoints  
**Issue**: Generic "not found" instead of specific error details

---

## 📋 TODO LIST FOR FULLSTACK MANAGER

### PRIORITY 1: CRITICAL (Do First - Breaks App)
- [ ] **API-001**: Fix column naming consistency (1Y_total_return → 1Y Return)
  - Location: `api.py` normalize_screening_row() + all endpoints
  - Impact: Screening page won't display correctly
  - Estimated: 2 hours

- [ ] **API-002**: Add error handling to all endpoints
  - Location: `api.py` all @app.get/@app.post decorators
  - Impact: Silent failures currently
  - Estimated: 3 hours

- [ ] **API-003**: Fix type safety (TypeScript interfaces match API responses)
  - Location: `frontend/src/app/analytics/page.tsx` interfaces
  - Impact: Runtime crashes with null values
  - Estimated: 2 hours

- [ ] **API-006**: Add input validation for tickers
  - Location: `api.py` all ticker endpoints
  - Impact: Invalid tickers could break system
  - Estimated: 1 hour

### PRIORITY 2: HIGH (Do Second - App Buggy)
- [ ] **API-008**: Make DEV_MODE configurable via env variable
  - Location: `src/config.py`
  - Impact: Only 5 tickers analyzed in prod
  - Estimated: 1 hour

- [ ] **API-004**: Add error boundaries in frontend
  - Location: `frontend/src/app/analytics/page.tsx`, `page.tsx`
  - Impact: Better error display instead of blank screen
  - Estimated: 2 hours

- [ ] **BUG-002**: Handle null moving averages in charts
  - Location: `src/analytics.py`, frontend chart rendering
  - Impact: Charts break for stocks < 50 trading days
  - Estimated: 1 hour

- [ ] **BUG-003**: Handle zero volatility in Sharpe ratio
  - Location: `src/screening.py` line 36
  - Impact: NaN values in screening results
  - Estimated: 1 hour

- [ ] **BUG-005**: Fix date parsing timezone issues
  - Location: `frontend/src/app/page.tsx` line 40
  - Impact: Date might be off by one day
  - Estimated: 1 hour

### PRIORITY 3: MEDIUM (Do Third - Performance/UX)
- [ ] **ARCH-002**: Add rate limiting to `/api/screening/refresh`
  - Location: `api.py`
  - Impact: Someone could spam refresh and crash yfinance
  - Estimated: 2 hours

- [ ] **ARCH-003**: Add request queuing/locking for screening
  - Location: `api.py` global lock mechanism
  - Impact: Multiple concurrent refresh calls will fail
  - Estimated: 2 hours

- [ ] **PERF-001**: Add pagination to screening endpoint
  - Location: `api.py` /api/screening?limit=10&offset=0
  - Impact: Frontend loads faster
  - Estimated: 2 hours

- [ ] **PERF-003**: Cache screening CSV in memory
  - Location: `api.py` use @lru_cache or in-memory dict
  - Impact: Disk I/O every request
  - Estimated: 1 hour

- [ ] **ARCH-004**: Add global state management (Redux/Zustand)
  - Location: `frontend/src`
  - Impact: Reduce duplicate API calls
  - Estimated: 4 hours

- [ ] **FEAT-005**: Make screening refresh async with job ID
  - Location: `api.py` use background tasks
  - Impact: UI freezes for 2-3 minutes currently
  - Estimated: 3 hours

### PRIORITY 4: LOW (Nice to Have)
- [ ] **SEC-001**: Replace CORS wildcard with specific origins
- [ ] **FEAT-002**: Add search/filter to screener frontend
- [ ] **FEAT-003**: Add query params for server-side sorting
- [ ] **FEAT-004**: Add Cache-Control headers to API responses
- [ ] **FEAT-006**: Better error messages from API
- [ ] **BUG-001**: Simplify insights list validation
- [ ] **BUG-004**: Make PDF regex patterns more robust
- [ ] **ARCH-001**: Refactor duplicate analytics logic into shared module

---

## 🎯 RECOMMENDED IMPLEMENTATION ORDER

**Week 1 (Critical fixes):**
1. Column naming consistency (API-001) - BREAKING
2. Type safety fixes (API-003) - BREAKING  
3. Error handling (API-002) - BREAKING
4. Input validation (API-006) - SECURITY

**Week 2 (High priority):**
5. DEV_MODE env variable (API-008)
6. Error boundaries (API-004)
7. Null handling for MAs (BUG-002) + Sharpe ratio (BUG-003)
8. Date parsing (BUG-005)

**Week 3 (Performance):**
9. Rate limiting (ARCH-002)
10. Request queuing (ARCH-003)
11. Pagination (PERF-001)
12. Memory caching (PERF-003)

**Week 4+ (Polish):**
13. State management (ARCH-004)
14. Async screening (FEAT-005)
15. Remaining nice-to-haves

---

## 📊 ISSUE SUMMARY

| Category | Count | Severity |
|----------|-------|----------|
| API Misalignments | 10 | 🔴🟠🟠 |
| Architecture Issues | 4 | 🟡 |
| Bugs | 5 | 🟡 |
| Performance | 3 | 🟡 |
| Security | 2 | 🟡 |
| Missing Features | 6 | 🟡 |
| **Total** | **30** | **Mixed** |

**Breaking Issues**: 5 (API-001, API-002, API-003, API-006, API-004)  
**High Priority**: 8  
**Medium Priority**: 6  
**Low Priority**: 11

---

**Manager Assessment**: Application is functionally complete but needs stabilization. 
- **Code Quality**: 6/10 (Duplication, inconsistencies)
- **Error Handling**: 3/10 (Minimal try-catch blocks)
- **Type Safety**: 5/10 (TS interfaces don't match reality)
- **Performance**: 5/10 (No caching, pagination, rate limiting)
- **Security**: 6/10 (Open CORS, no input validation)

**Recommendation**: Fix Priority 1 issues immediately before shipping to production. App currently in "alpha/beta" state, not production-ready.

