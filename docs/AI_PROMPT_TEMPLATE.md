# AI PROMPT TEMPLATE - FOR ADDING FEATURES TO JARVIS

## INSTRUCTION FOR AI DEVELOPERS

Copy and adapt this prompt template when asking an AI to add features to the Jarvis stock analysis program. Fill in the [BRACKETS] with your specific requirements.

---

# REQUEST TO AI: ADD [FEATURE_NAME] TO JARVIS

## Context

I have a full-stack stock analysis application called **Jarvis** that analyzes 502 NASDAQ 100 stocks. Here's the architecture:

**Tech Stack:**
- Frontend: Next.js + React 19 + TypeScript + Tailwind CSS
- Backend: FastAPI (Python)
- Data: Finnhub API + SEC EDGAR API
- Database: CSV files (local storage)

**Program Status:**
- ✅ Core analytics working (returns, volatility, metrics)
- ✅ API endpoints functional with error handling
- ✅ Batch screening operations complete
- ⚠️ Bug fixes needed (see FULLSTACK_ANALYSIS.md)
- ⚠️ Missing features (pagination, rate limiting, async jobs)

**Relevant Files:**
- Analytics: `src/analytics.py` - metric calculations
- API: `api.py` - REST endpoints
- Screening: `src/screening.py` - ranking/filtering
- Frontend: `frontend/src/app/` - Next.js pages
- Config: `src/config.py` - settings + API keys
- Docs: `FULLSTACK_PROMPT.md` - full development guide

## What I Want to Build

**Feature:** [FEATURE_NAME]

**Purpose:** [WHY_THIS_MATTERS] (example: "to allow users to...")

**Details:**
- [REQUIREMENT_1]
- [REQUIREMENT_2]
- [REQUIREMENT_3]

**Target:** [BACKEND_ONLY / FRONTEND_ONLY / FULL_STACK]

**Complexity:** [QUICK_WIN_1_2_HRS / MEDIUM_2_4_HRS / ADVANCED_4_PLUS_HRS]

## Important Constraints

1. **Column Names:** Use normalized names in API responses:
   - `1Y Return` (not `1Y_total_return`)
   - `Volatility` (not `volatility`)
   - `Max Drawdown` (not `max_drawdown`)

2. **Error Handling:** All backends must have try-catch + logging:
   ```python
   try:
       # logic here
   except HTTPException:
       raise
   except Exception as e:
       logger.error(f"Error in function_name: {e}")
       raise HTTPException(status_code=500, detail="Clear error message")
   ```

3. **Input Validation:** Validate all user inputs:
   ```python
   ticker = ticker.upper()
   if not ticker.replace("-", "").isalnum() or len(ticker) > 5:
       raise HTTPException(status_code=400, detail="Invalid ticker format")
   ```

4. **Null Handling:** Always handle None/null values:
   ```python
   if value is None or pd.isna(value):
       return None  # Don't crash
   ```

5. **Type Hints:** Use them everywhere (Python & TypeScript):
   ```python
   def function(param: str) -> dict:
   ```

6. **API Documentation:** Add docstrings to all endpoints:
   ```python
   @app.get("/api/endpoint")
   def endpoint():
       """Clear description. Returns: JSON spec. Errors: conditions."""
   ```

7. **Configuration:** Use environment variables, not hardcoded values:
   ```python
   setting = os.getenv("SETTING_NAME", "default_value")
   ```

8. **Frontend Types:** Define interfaces for all API responses:
   ```typescript
   interface ApiResponse {
       results: Array<{field: string | null}>;
       error?: string;
   }
   ```

## What I DON'T Want

❌ Return bare exceptions (wrap in HTTPException with status code)
❌ Call external APIs without timeout handling
❌ Assume data always exists (always add null checks)
❌ Hardcode values (use config/env vars)
❌ Skip logging (log errors, important steps)
❌ Return unstructured data (use normalized column names)
❌ Forget error messaging (tell user what went wrong)
❌ Write 100+ line functions (break into smaller pieces)
❌ Skip TypeScript types (define interfaces)
❌ Deploy without testing (test locally first)

## Current Known Issues to Avoid

⚠️ **DON'T FIX THESE** (unless specifically requested):
- Frontend TypeScript type safety issues (separate ticket)
- Screen refresh async jobs (separate ticket)
- Global state management (separate ticket)

✅ **DO USE THESE PATTERNS:**
- normalize_metrics() in analytics.py - when adding new metrics
- JSONResponse(..., headers={"Cache-Control": "..."}) - for caching
- ensure_live_data() - for cached file access
- try_except with logging - for error handling

## Expected Deliverables

1. **Backend Changes** (if applicable):
   - Modified/new functions in src/
   - Updated api.py endpoints
   - Error handling included
   - Logging added

2. **Frontend Changes** (if applicable):
   - New components/pages in frontend/src/
   - TypeScript interfaces defined
   - Error states handled
   - Loading states implemented

3. **Testing Checklist:**
   - [ ] Backend: `python main.py` runs without error
   - [ ] Backend: `python -c "from src.module import func; print(func())"` 
   - [ ] API: `curl http://localhost:8000/api/endpoint` returns correct data
   - [ ] Frontend: `npm run dev` starts without errors
   - [ ] Full flow: Feature works end-to-end

4. **Code Quality:**
   - Comments added (WHY, not WHAT)
   - No redundant code
   - Follows existing patterns
   - Git-ready (clean history)

## Example Request (Template Filled In)

```
**Feature:** Add Dividend Yield Sorting to Screener

**Purpose:** Let users find high-dividend stocks easily

**Details:**
- Add query parameter ?sort=dividend_yield&order=desc to /api/screening
- Frontend screener table should allow clicking column headers to sort
- Return results sorted server-side (not client-side)

**Target:** FULL_STACK (1 API endpoint + 1 React component update)

**Complexity:** MEDIUM (2-4 hours)

**Constraints:**
- Use normalized name "Dividend Yield" in responses
- Handle null dividend yields (some stocks have no dividend)
- Add cache header (max-age=300)
- Validate sort field against allowed list (security)
```

---

## How to Provide Code

**When providing code:**
1. Specify the full file path
2. Show 3-5 lines of context before/after changes
3. Highlight what changed (e.g., "NEW:", "REPLACED:", "DELETED:")
4. Explain why each change was made
5. Include any new imports needed

**Example:**
```
File: src/analytics.py

REPLACED (lines 120-125):
```python
def old_function(df):
    return df['Close'].mean()
```

WITH (adds null safety):
```python
def new_function(df):
    if df is None or df.empty:
        return None
    return float(df['Close'].mean())
```

**Why:** Prevents crashing when df is None/empty
```

---

## Quality Checklist for AI Response

Before accepting AI-generated code, verify:

- [ ] Has try-catch blocks with proper error types
- [ ] Validates all inputs (ticker format, etc.)
- [ ] Uses environment variables for config
- [ ] Normalizes column names in API responses
- [ ] Includes helpful error messages (not generic "error")
- [ ] Has logging at key points
- [ ] Handles null values gracefully
- [ ] Includes docstrings with parameter/return specs
- [ ] TypeScript has proper interfaces (no `any`)
- [ ] Follows existing code patterns in repo
- [ ] Includes 3-5 test cases or usage examples
- [ ] No hardcoded values (API keys, URLs, limits)
- [ ] No infinite loops or blocking operations
- [ ] Cache headers added to GET endpoints
- [ ] Ready to test locally (instructions provided)

---

## Quick Copy-Paste Prompts

### For Bug Fixes:

> I need to fix [BUG_NAME] in my Jarvis stock analysis program. 
> 
> Issue: [DESCRIPTION]
> Location: [FILE_PATH]
> Current behavior: [WHAT_HAPPENS_NOW]
> Expected behavior: [WHAT_SHOULD_HAPPEN]
> 
> Here's the full development guide: [PASTE FULLSTACK_PROMPT.md]
> Here's the bug analysis: [PASTE FULLSTACK_ANALYSIS.md]
> 
> Please provide:
> 1. Root cause analysis
> 2. Code fix (with context)
> 3. Test steps to verify
> 4. Any related issues to fix

### For New Features:

> I want to add [FEATURE] to my Jarvis stock analysis platform.
> 
> Current system:
> - Frontend: Next.js + TypeScript
> - Backend: FastAPI (Python)
> - Data: 502 stocks from Finnhub API
> 
> Feature requirements:
> - [REQ_1]
> - [REQ_2]
> - [REQ_3]
> 
> Constraints:
> - Use normalized column names (see FULLSTACK_PROMPT.md)
> - Must include error handling + logging
> - Must validate all inputs
> - Must handle null values gracefully
> 
> Here's the full guide: [PASTE FULLSTACK_PROMPT.md]
> 
> Please provide:
> 1. Implementation plan (steps)
> 2. Backend changes (if needed)
> 3. Frontend changes (if needed)
> 4. Test checklist
> 5. Any edge cases to handle

### For Architecture/Design Questions:

> Should I [IMPLEMENT_APPROACH_A_OR_B] for [FEATURE]?
> 
> Context:
> - This is a stock analysis platform using Next.js + FastAPI
> - Database is CSV files (not SQL database)
> - API must serve 502 stocks with live data
> - Frontend is real-time React dashboard
> 
> Option A: [DESCRIBE_APPROACH_A]
> Option B: [DESCRIBE_APPROACH_B]
> 
> Tradeoffs:
> - Performance: A vs B
> - Complexity: A vs B
> - Maintainability: A vs B
> 
> Here's the system design: [PASTE FULLSTACK_PROMPT.md]
> 
> Which approach do you recommend and why?

---

## Output Expectations

**What a good AI response includes:**

1. ✅ Clear explanation of what's being done and why
2. ✅ Step-by-step implementation instructions
3. ✅ Complete code snippets (copy-paste ready)
4. ✅ Test commands to verify it works
5. ✅ Potential issues or edge cases
6. ✅ How to integrate with existing code
7. ✅ Documentation/comments in the code
8. ✅ Before/after comparison
9. ✅ Performance implications (if any)
10. ✅ Security considerations

**What to ask AI if response doesn't include:**

> Can you also include:
> - [ ] How to test this locally?
> - [ ] What error cases might occur?
> - [ ] How does this fit into existing error handling?
> - [ ] Are there any performance implications?
> - [ ] What if [EDGE_CASE_X] happens?

---

## Pro Tips

1. **Break down large features** - Ask for backend, then frontend, then integration
2. **Show examples** - Share working code patterns so AI matches style
3. **Ask for tests** - Request test cases to verify code works
4. **Clarify constraints** - Be explicit about what's NOT allowed
5. **Review incrementally** - Check each part before moving to next
6. **Ask for edge cases** - Request handling for None/empty/invalid data
7. **Request documentation** - Ask for docstrings + comments
8. **Iterate** - If response isn't quite right, provide feedback

---

**Remember:** The better your prompt, the better the code. Take time to fill out all the [BRACKETS] and provide context!

---

**Last Updated:** March 16, 2026  
**Version:** 1.0
