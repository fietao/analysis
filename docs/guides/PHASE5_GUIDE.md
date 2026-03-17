# 🚀 PHASE 5: USER ENGAGEMENT LAYER - IMPLEMENTATION GUIDE

**Status:** ✅ **BACKEND FOUNDATION COMPLETE**  
**Date:** March 17, 2026  
**Version:** 1.0.0

---

## 📋 What's Implemented

### ✅ Authentication System

**JWT Token-Based Authentication with Security**
- Password hashing with bcrypt (12 rounds - production-grade security)
- JWT access tokens (24-hour expiration, configurable)
- JWT refresh tokens (30-day expiration)
- Password strength validation
  - Minimum 8 characters
  - Uppercase + lowercase + digits + special characters required
  - Secure random token generation

**API Endpoints:**
```
POST   /api/auth/signup          - User registration
POST   /api/auth/login           - User login
POST   /api/auth/refresh         - Refresh access token
GET    /api/users/me             - Get current user profile
```

**Security Features:**
- Passwords NEVER stored in plain text
- Tokens validated on every protected endpoint
- Secret error messages (API keys masked)
- Dependency: passlib[bcrypt], cryptography, python-jose

---

### ✅ User Models & Database Structure

**User Profiles:**
```python
Fields:
- id: int (unique user ID)
- email: str (unique, validated)
- username: str (3-50 chars)
- full_name: str (optional)
- role: str ('free', 'pro', 'enterprise', 'admin')
- tier: str (member, bronze, silver, gold, platinum)
- points: int (gamification score)
- badges: List[str] (earned achievement badges)
- created_at: datetime
- last_login: datetime
- login_streak: int (consecutive days)
- is_active: bool
```

**TODO: Database Schema**
```sql
-- Users table (currently in-memory, needs migration to PostgreSQL Phase 6)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'free',
    tier VARCHAR(20) DEFAULT 'member',
    points INTEGER DEFAULT 0,
    badges JSON DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    login_streak INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_achievements (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50),
    points_earned INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    badges_earned JSON
);
```

---

### ✅ Gamification System

#### Badge System (11 Badges)

```
1. 🎉 First Member      - First login (10 pts)
2. 🔥 On Fire!          - 7-day login streak (50 pts)
3. ⭐ Unstoppable       - 30-day login streak (200 pts)
4. 📊 Analysis Master   - 50 analyses completed (100 pts)
5. 🔍 Screening Expert  - 100 screenings completed (150 pts)
6. 👤 Pro Profile       - Complete user profile (25 pts)
7. 💎 Premium Member    - Subscribe to pro tier (200 pts)
8. 🏆 Top 10            - Ranked in top 10 (250 pts)
9. 🥇 Top 100           - Ranked in top 100 (100 pts)
10. 👥 Brand Ambassador - Referral 3 friends (150 pts)
11. 🚀 Early Adopter    - First 1000 users (500 pts)
```

#### Points System (20+ Actions)

**Core Activities:**
```
- Login:              5 pts (daily)
- Run analysis:       10 pts
- Save analysis:      15 pts
- Stock screening:    8 pts
- Share screening:    20 pts
- Complete profile:   50 pts
- AI chat message:    3 pts
- Watch video:        2 pts (per 10 min)
- Video completion:   25 pts
```

**Bonuses:**
- Premium user 1.5x multiplier
- Login streak bonus: +10% per day (capped at 2.0x)
- Consecutive actions: +10% bonus (capped at 1.5x)

#### Leaderboard System

**Global Leaderboard:**
```
GET /api/gamification/leaderboard
- Top 100 users by points
- Rank, username, points, tier
- Real-time updates
- Weekly and all-time variants
```

**User Leaderboard Position:**
```
GET /api/gamification/leaderboard/me
- User's current rank
- Points to next tier
- Percentile ranking
- Nearby competitors (±3 ranks)
```

**User Tier Progression:**
```
Member:    0 - 499 pts
Bronze:    500 - 1,999 pts
Silver:    2,000 - 4,999 pts
Gold:      5,000 - 9,999 pts
Platinum:  10,000+ pts
```

---

### ✅ API Endpoints

#### Authentication

```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "password": "Secure@Pass123",
    "full_name": "John Doe"
  }'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Secure@Pass123"
  }'

# Refresh Token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"

# Get User Profile
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <access_token>"
```

#### Gamification

```bash
# Log Action (returns points earned)
curl -X GET "http://localhost:8000/api/gamification/achievements?action=analysis" \
  -H "Authorization: Bearer <token>"

# Get User Badges
curl -X GET http://localhost:8000/api/gamification/badges \
  -H "Authorization: Bearer <token>"

# Global Leaderboard
curl -X GET "http://localhost:8000/api/gamification/leaderboard?limit=50"

# User's Leaderboard Position
curl -X GET http://localhost:8000/api/gamification/leaderboard/me \
  -H "Authorization: Bearer <token>"
```

#### AI Assistant (Beta)

```bash
# Chat with AI
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is a good dividend stock?",
    "conversation_id": "conv_123"
  }'
```

#### Videos

```bash
# List Videos
curl -X GET "http://localhost:8000/api/videos?category=tutorial&limit=20"

# Log Video Watch
curl -X POST http://localhost:8000/api/videos/intro_1/watch \
  -H "Authorization: Bearer <token>"
```

---

## 📁 Files Created/Modified

### New Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/models.py` | 350+ | Pydantic models for users, gamification, AI |
| `src/auth.py` | 400+ | JWT tokens, password hashing, validation |
| `src/gamification.py` | 450+ | Badges, points, leaderboards |

### Modified Files

| File | Changes |
|------|---------|
| `api.py` | Added 500+ lines: auth endpoints, gamification, AI, videos |
| `requirements.txt` | Added email-validator for Pydantic EmailStr |

---

## 🔐 Security Implementation

### Authentication Security

✅ **Password Security:**
- bcrypt hashing (12 rounds, CPU intensive)
- Minimum 8 characters required
- Strong password requirements enforced
- Never stored in plain text
- Salted hashes prevent rainbow table attacks

✅ **Token Security:**
- JWT signed with SECRET_KEY (from .env)
- HS256 algorithm
- Automatic expiration (24 hours)
- Refresh tokens for extended sessions
- Token validation on every protected endpoint

✅ **Error Handling:**
- Secrets masked in logs
- Generic error messages to users
- Detailed logging for debugging

---

## 🎯 How to Use Phase 5 Features

### 1. User Registration

```python
# POST /api/auth/signup
{
  "email": "john@example.com",
  "username": "john_trader",
  "password": "MyPassword@123!",
  "full_name": "John Smith"
}

# Gets JWT token + refresh token
```

### 2. User Login

```python
# POST /api/auth/login
{
  "email": "john@example.com",
  "password": "MyPassword@123!"
}

# Gets new session tokens
```

### 3. Earn Badges

When user performs actions:
- Runs analysis → 10 points
- 7-day login streak → "On Fire!" badge + 50 points
- 50 analyses → "Analysis Master" badge
- Leaderboard top 10 → "Top 10" badge

### 4. View Leaderboard

```python
# GET /api/gamification/leaderboard
- Shows top 100 users
- User's ranking (if logged in)
- Points comparison
- Tier information
```

### 5. Integrate with Stock Analysis

When user runs analysis:
```python
# 1. Run analysis
result = analyze_stock("AAPL")

# 2. Log achievement
POST /api/gamification/achievements?action=analysis
# Adds 10 points, checks for badges

# 3. Check leaderboard
GET /api/gamification/leaderboard/me
# Shows if user entered top 100
```

---

## 📊 Database Plan (Phase 6)

Current: **In-Memory** (for development)  
Target: **PostgreSQL**

```python
# Phase 6 migration:
- Move users_db → PostgreSQL
- Move achievement_log → PostgreSQL
- Add connection pooling
- Add query optimization
- Add data backups
```

---

## 🤖 AI Assistant Integration (Phase 5 Future)

Current: **Placeholder** structure ready  
Target: **GPT-4 API Integration**

```python
# Currently returns demo responses
POST /api/ai/chat
→ "I received your message. Full AI integration coming in Phase 5!"

# Phase 5 production:
→ Uses GPT-4 API with context
→ Stores conversation history
→ Tracks token usage
→ Awards points for interactions
```

**Setup Required:**
```bash
# In .env
OPENAI_API_KEY=sk_your_key
GPT_MODEL=gpt-4
AI_ASSISTANT_ENABLED=True
```

**Link to AI context:**
```python
# Include user's portfolio, analysis history, preferences
# GPT-4 returns personalized advice
# API: $0.03 per 1K input tokens, $0.06 per 1K output tokens
```

---

## 🎬 Video Integration (Phase 5 Future)

Current: **Placeholder** structure ready  
Target: **YouTube API Integration**

```python
# Currently shows demo videos
GET /api/videos
→ Returns sample tutorial videos

# Phase 5 production:
→ Uses YouTube Data API
→ Stores video metadata
→ Tracks watch history
→ Awards badges for completions
```

**Setup Required:**
```bash
# In .env
YOUTUBE_API_KEY=your_api_key
VIDEO_ENABLED=True
```

**Videos by Tier:**
```
Free:       Basic tutorials (beginners)
Pro:        Advanced strategies (subscribers)
Enterprise: Custom analysis videos (organizations)
```

---

## ✅ Pre-Production Checklist

**Authentication:**
- [ ] Test user signup with weak password (should reject)
- [ ] Test token expiration
- [ ] Test refresh token endpoint
- [ ] Test profile retrieval

**Gamification:**
- [ ] Test points calculation with bonuses
- [ ] Test badge eligibility checks
- [ ] Test leaderboard ranking
- [ ] Test tier progression

**API Security:**
- [ ] All endpoints require valid JWT
- [ ] Rate limiting active on endpoints
- [ ] Error messages don't leak secrets
- [ ] CORS configured properly

---

## 🚀 Next Steps

### Week 1
- [ ] Database migration (CSV → PostgreSQL)
- [ ] Add admin dashboard
- [ ] Implement 2FA for premium users

### Week 2
- [ ] GPT-4 AI Assistant integration
- [ ] YouTube video integration
- [ ] Referral system backend

### Week 3
- [ ] Frontend integration (React components)
- [ ] User profile UI
- [ ] Leaderboard UI
- [ ] Badge display UI

### Week 4
- [ ] Payment integration (Stripe)
- [ ] Subscription management
- [ ] Premium tier features

---

## 📞 Quick Reference

**Current User Count:** 0 (ready for testing)  
**Active Sessions:** 0  
**Total Points Distributed:** 0  
**Badgesawarded:** 0  

**Default Configuration:**
```
JWT_ALGORITHM = HS256
JWT_EXPIRATION_HOURS = 24
REFRESH_TOKEN_EXPIRE_DAYS = 30
BCRYPT_ROUNDS = 12
```

**Test Credentials (for manual testing):**
```
Email: demo@example.com
Password: DemoPass@123!
```

---

## 📝 Architecture Diagram

```
Client (React App)
    ↓
[Authentication Endpoints]
├── POST /auth/signup      → Pydantic Models → Auth Module → Users DB
├── POST /auth/login       → Verify Password → JWT Token
├── POST /auth/refresh     → Validate Token → New Token
└── GET /users/me          → Extract User → Return Profile

[Gamification Endpoints]
├── POST /gamification/achievements  → Calculate Points → Update DB
├── GET /gamification/badges         → Query Badges → Return List
├── GET /gamification/leaderboard    → Sort by Points → Return Ranks
└── GET /gamification/leaderboard/me → Find User Rank → Return Context

[AI Assistant Endpoints]
├── POST /ai/chat          → Store Message → [Phase 5: Call GPT-4] → Response
└── GET /ai/conversations  → Query History → Return Messages

[Video Endpoints]
├── GET /videos            → [Phase 5: Query YouTube] → Return List
└── POST /videos/{id}/watch → Log Watch → Award Points
```

---

## 🎉 Summary

**Phase 5 Backend is now READY!**

✅ Full authentication system with JWT  
✅ 11 different achievement badges  
✅ Points system with multipliers  
✅ Global leaderboard with ranking  
✅ AI assistant structure ready for GPT-4  
✅ Video integration structure ready for YouTube  
✅ Secure password handling with bcrypt  
✅ Token refresh mechanism  
✅ User profiles and role management  

**Technology Stack:**
- FastAPI (REST API framework)
- Pydantic (data validation)
- JWT (authentication)
- bcrypt (password hashing)
- python-jose (token handling)
- email-validator (email validation)

**What's Next:**
1. Database migration to PostgreSQL
2. Frontend React components for auth UI
3. GPT-4 API integration
4. YouTube API integration
5. Stripe payment integration

---

**Status: 🚀 Ready for Next Phase**
