# SECURITY SETUP GUIDE

**Status:** 🟡 PARTIALLY FIXED (Critical issues addressed)  
**Date:** March 16, 2026  
**Next Steps:** Follow this guide to complete security hardening

---

## ✅ What's Been Fixed (Implemented)

### 1. ✅ Rate Limiting Added
- **Location:** `api.py` → slowapi middleware
- **Feature:** Prevents DoS by limiting requests per IP
- **Status:** Implemented with decorator support
- **Configuration:** `config/SECURITY.yaml`

**Current Limits:**
- `/api/analysis`: 30/minute
- `/api/screening/refresh`: 1/hour (heavy operation)
- Default: 100/minute

### 2. ✅ Security Headers Middleware
- **Location:** `api.py` → Security headers middleware
- **Headers Added:**
  - HSTS (HTTP Strict Transport Security)
  - X-Frame-Options (Clickjacking protection)
  - X-Content-Type-Options (MIME sniffing prevention)
  - X-XSS-Protection (XSS protection)
  - Content-Security-Policy (CSP)
  - Referrer-Policy (Referrer control)
  - Permissions-Policy (Feature restrictions)

### 3. ✅ Error Message Sanitization
- **Location:** `api.py` → `sanitize_error_message()`
- **Feature:** Removes API keys, tokens, paths from errors
- **Applied To:** Logging, error responses
- **Status:** Integrated throughout API

### 4. ✅ File Upload Security
- **Location:** `api.py` → `/api/upload-filing` endpoint
- **Features:**
  - Filename sanitization (prevents path traversal)
  - Path traversal verification
  - File size validation (50MB max)
  - File type validation (PDF only)
 **Status:** Fully implemented

### 5. ✅ CSV Injection Prevention
- **Location:** `src/security.py` → `sanitize_dataframe_for_csv()`
- **Feature:** Prefixes dangerous chars ('=', '+', '-', '@') with quote
- **Applied To:** `src/screening.py` → `save_screening_results()`
- **Status:** Implemented

### 6. ✅ Input Validation
- **Location:** `src/security.py` → `validate_ticket()`, `validate_date_range()`
- **Feature:** Strict validation of all inputs
- **Applied To:** Ticker symbols, dates, pagination
- **Status:** Implemented

### 7. ✅ Security Utilities Module
- **Location:** `src/security.py`
- **Features:**
  - Logging formatter with secret masking
  - File handling utilities
  - Validation functions
  - Dependency vulnerability checks
- **Status:** Complete module created

### 8. ✅ Updated Dependencies
- **Location:** `requirements.txt`
- **Changes:**
  - Added `slowapi` (rate limiting)
  - Added `safety` & `pip-audit` (vulnerability scanning)
  - Added `passlib[bcrypt]` (password hashing for Phase 5)
  - Added `cryptography` (encryption support)
  - Updated existing packages to latest versions
- **Status:** Ready for install

### 9. ✅ Enhanced .gitignore
- **Location:** `.gitignore`
- **Added Protection For:**
  - `.env` files
  - Secret keys & certificates
  - SSH keys
  - Temporary files
  - Debug logs
  - Database files
- **Status:** Complete

### 10. ✅ Security Configuration
- **Location:** `config/SECURITY.yaml`
- **Contains:** Complete security settings documentation
- **Sections:**
  - API Security (TLS, CORS, CSP)
  - Authentication & Authorization
  - Rate Limiting
  - Data Protection
  - File Upload
  - Input Validation
  - Logging
  - Compliance
  - Pre-deployment checklist
- **Status:** Complete reference guide

---

## 🔧 What Still Needs To Be Done

### Immediate (This Week)

#### 1. ❌ Install Security Dependencies
```bash
pip install -r requirements.txt

# Then verify vulnerable packages
safety check
pip-audit
```

**Fix:** Run the commands above

#### 2. ❌ Set Up Environment Variables Securely
Create `.env` file in project root (already in .gitignore):

```bash
# .env (NEVER commit this file!)
# ============================================================================
# ✅ SECURITY: Secrets must be HERE, NOT in code
# ============================================================================

# API Keys
FINNHUB_API_KEY=your_real_key_here
SEC_EDGAR_BASE_URL=https://data.sec.gov/submissions

# ✅ CRITICAL: Generate strong secret key
# Run: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_generated_secret_key_here

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limiting Whitelist (optional)
RATE_LIMIT_WHITELIST_IPS=

# Environment
ENVIRONMENT=development
DEBUG=False  # MUST be False in production!

# Dev Mode
DEV_MODE=True
DEV_TICKERS_LIMIT=5

# Trusted Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,localhost:3000,localhost:8000

# Encryption (Phase 6+)
# ENCRYPTION_KEY=your_32_byte_encryption_key_here
```

**Fix:** Create this file locally (don't commit!)

#### 3. ❌ Test Rate Limiting
```bash
# Start API server
python -m uvicorn api:app --reload

# Test rate limiting (should fail after 1 request in 1 hour)
for i in {1..3}; do
  curl -X POST http://localhost:8000/api/screening/refresh
done
# After 1 request, should get: {"detail": "Too many requests"}
```

**Fix:** Verify rate limits work

#### 4. ❌ Test Security Headers
```bash
# Check security headers
curl -I http://localhost:8000/api/health

# Should see:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Frame-Options: DENY
# Content-Security-Policy: ...
```

**Fix:** Verify headers are present

### Phase 1 (Before Beta)

#### 5. ❌ Implement JWT Authentication
- [ ] Create `src/auth.py` with JWT functions
- [ ] Add `/auth/signup` and `/auth/login` endpoints
- [ ] Protect endpoints with `@require_auth` decorator
- [ ] Add user profiles table (Phase 5+)

**Estimated:** 8 hours

#### 6. ❌ Add HTTPS/TLS in Production
- [ ] Generate SSL certificate (Let's Encrypt free)
- [ ] Update deployment to enforce HTTPS
- [ ] Set up nginx reverse proxy
- [ ] Automatic certificate renewal

**Tools:** Certbot, Let's Encrypt
**Estimated:** 4 hours

#### 7. ❌ Set Up Monitoring & Logging
- [ ] Configure centralized logging (ELK, Datadog, etc.)
- [ ] Set up alerts for suspicious activity
- [ ] Audit logging for all API calls
- [ ] Dashboard for security monitoring

**Tools:** Elasticsearch, Splunk, Datadog
**Estimated:** 8 hours

#### 8. ❌ Database Setup (Phase 5+)
- [ ] Create secure database (PostgreSQL with encryption)
- [ ] Set up connection pooling
- [ ] Migrate from CSV to database
- [ ] Implement backup strategy

**Estimated:** 6 hours

### Phase 2 (Before Production)

#### 9. ❌ Security Testing
- [ ] OWASP Top 10 testing
- [ ] Penetration testing
- [ ] Load testing (verify rate limits)
- [ ] SQL Injection tests (if using SQL)
- [ ] XSS tests
- [ ] CSRF tests

**Estimated:** 16 hours or hire consultant ($2-5K)

#### 10. ❌ Compliance Preparation
- [ ] Legal Review (US, EU, Asia)
- [ ] Terms of Service document
- [ ] Privacy Policy (GDPR-compliant)
- [ ] Financial Disclaimer
- [ ] Data Processing Agreement (if applicable)

**Estimated:** 8 hours or hire lawyer ($1-3K)

#### 11. ❌ Backup & Disaster Recovery
- [ ] Automated daily backups
- [ ] Backup verification
- [ ] Recovery testing
- [ ] Backup encryption
- [ ] Cloud storage (AWS S3, Azure Blob)

**Estimated:** 4 hours

#### 12. ❌ Incident Response Plan
- [ ] Written security incident procedures
- [ ] Breach notification process
- [ ] Recovery procedures
- [ ] Team communication plan
- [ ] Audit trail review

**Estimated:** 2 hours

---

## 🚀 Quick Start: Apply Fixes Now

### Step 1: Install Dependencies
```bash
pip install slowapi safety pip-audit passlib[bcrypt] cryptography
pip install -r requirements.txt
```

### Step 2: Create .env File
Copy `.env.example` to `.env` and add your secrets:
```bash
cp config/.env.example .env
# Edit .env with your API keys
```

### Step 3: Test Security Features
```bash
# Run the API with security enabled
python -m uvicorn api:app --reload

# In another terminal, test:
# 1. Rate limiting
curl -X POST http://localhost:8000/api/screening/refresh

# 2. Security headers
curl -I http://localhost:8000/api/health

# 3. Error sanitization
curl "http://localhost:8000/api/analysis/INVALID_TICKER_WITH_EQUALS=MALICIOUS"
```

### Step 4: Scan for Vulnerabilities
```bash
# Check dependencies
safety check
pip-audit

# Check code for security issues
bandit -r src/

# Check code style
black --check src/
```

---

## 🔍 Security Verification Checklist

Run these tests to verify security is working:

```bash
# ============================================================================
# TEST 1: Rate Limiting Works
# ============================================================================
echo "Testing rate limiting..."
for i in {1..3}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/screening/refresh
  sleep 1
done
# Should fail after 1 request (rate limited)

# ============================================================================
# TEST 2: Security Headers Present
# ============================================================================
echo "Testing security headers..."
curl -I http://localhost:8000/api/health | grep -E "Strict-Transport|X-Frame|X-Content|CSP"

# ============================================================================
# TEST 3: File Upload Path Traversal Blocked
# ============================================================================
echo "Testing path traversal protection..."
# Create test file
echo "malicious" > test_upload.txt
mv test_upload.txt "../../../../../../etc/passwd.pdf"
curl -X POST http://localhost:8000/api/upload-filing/AAPL \
  -F "file=@../../etc/passwd.pdf"
# Should return error (path sanitized)

# ============================================================================
# TEST 4: CSV Injection Prevention
# ============================================================================
echo "Testing CSV injection prevention..."
python -c "
import pandas as pd
from src.security import sanitize_dataframe_for_csv

df = pd.DataFrame({
    'ticker': ['=cmd|\"/c calc\"!A1', 'MSFT'],
    '1Y Return': [0.15, 0.20]
})
print('Before sanitization:', df.iloc[0,0])
sanitize_dataframe_for_csv(df)
print('After sanitization:', df.iloc[0, 0])
# Should show: '=cmd|...  (prefixed with quote)
"

# ============================================================================
# TEST 5: Error Messages Sanitized
# ============================================================================
echo "Testing error message sanitization..."
python -c "
from src.security import sanitize_error_message
error = 'Failed: API key=sk_12345abc_secret, token=bearer_xyz'
print('Original:', error)
print('Sanitized:', sanitize_error_message(error))
# Should mask both API key and token
"

# ============================================================================
# TEST 6: Input Validation Works
# ============================================================================
echo "Testing input validation..."
python -c "
from src.security import validate_ticker
try:
    validate_ticker('../../etc/passwd')  # Path traversal
except ValueError as e:
    print('Blocked:', e)
try:
    validate_ticker('AAPL')  # Valid
    print('Allowed: AAPL')
except ValueError as e:
    print('Error:', e)
"

# ============================================================================
# TEST 7: Dependency Vulnerabilities
# ============================================================================
echo "Scanning for dependency vulnerabilities..."
safety check
pip-audit
```

---

## 📋 Security Testing Checklist

- [ ] Rate limiting prevents >1 request/hour on `/api/screening/refresh`
- [ ] Security headers present on all responses
- [ ] Error messages don't contain API keys
- [ ] File uploads reject path traversal attempts
- [ ] CSV injection attempts are sanitized
- [ ] Input validation blocks malicious input
- [ ] Dependency scan returns no critical vulnerabilities
- [ ] `.env` file is in `.gitignore` (check with `git status`)
- [ ] All tests pass: `pytest tests/`
- [ ] No hardcoded secrets in `api.py`, `config.py`, etc.

---

## 🎯 Next Steps

1. **This Week:**
   - [ ] Install dependencies from requirements.txt
   - [ ] Create .env file with secrets
   - [ ] Run verification tests above
   - [ ] Test security features

2. **Week 1:**
   - [ ] Set up HTTPS/TLS (production)
   - [ ] Implement JWT authentication
   - [ ] Add comprehensive logging

3. **Before Beta Launch:**
   - [ ] Professional security testing
   - [ ] Backup & disaster recovery
   - [ ] Logging & monitoring setup
   - [ ] Legal documents ready

4. **Before Production:**
   - [ ] Penetration testing
   - [ ] Compliance verification
   - [ ] Incident response plan
   - [ ] Team security training

---

## 🔗 Resources

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **FastAPI Security:** https://fastapi.tiangolo.com/tutorial/security/
- **Secure Coding:** https://cheatsheetseries.owasp.org/
- **Python Security:** https://python.readthedocs.io/en/latest/library/security_warnings.html

---

**Questions?** Refer to `SECURITY_AUDIT.md` for detailed issue descriptions and fixes.
