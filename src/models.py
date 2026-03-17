"""
Database Models for User Authentication & Gamification
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

# ============================================================================
# Authentication Models
# ============================================================================

class UserRole(str, Enum):
    """User role hierarchy"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

class UserBase(BaseModel):
    """Base user schema (shared fields)"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User registration schema"""
    password: str = Field(..., min_length=8, max_length=100)

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """User profile update schema"""
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """User response schema (public, no password)"""
    id: int
    role: UserRole
    tier: str
    created_at: datetime
    points: int = 0
    badges_earned: int = 0
    is_active: bool = True
    
    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    """User DB schema (internal use with hashed password)"""
    hashed_password: str
    last_login: Optional[datetime] = None
    login_streak: int = 0
    
    class Config:
        from_attributes = True

# ============================================================================
# Token Models
# ============================================================================

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds

class TokenData(BaseModel):
    """JWT token payload"""
    user_id: int
    email: str
    role: UserRole
    exp: datetime

# ============================================================================
# Gamification Models
# ============================================================================

class BadgeType(str, Enum):
    """Badge types for achievements"""
    FIRST_LOGIN = "first_login"
    LOGIN_STREAK_7 = "login_streak_7"
    LOGIN_STREAK_30 = "login_streak_30"
    ANALYSIS_MASTER = "analysis_master"  # 50 analyses
    SCREENING_EXPERT = "screening_expert"  # 100 screenings
    PROFILER = "profiler"  # Complete profile
    EARLY_ADOPTER = "early_adopter"  # First 1000 users
    PREMIUM_USER = "premium_user"
    TOP_10_LEADERBOARD = "top_10_leaderboard"
    TOP_100_LEADERBOARD = "top_100_leaderboard"
    REFERRER = "referrer"  # Refer 3 friends

class Badge(BaseModel):
    """Badge schema"""
    id: int
    type: BadgeType
    name: str
    description: str
    icon_url: str
    points_value: int = 10

class UserBadge(BaseModel):
    """User badge achievement"""
    badge_id: int
    badge: Badge
    earned_at: datetime
    is_new: bool = False

class AchievementLog(BaseModel):
    """Log of user achievements"""
    user_id: int
    action: str  # 'login', 'analysis', 'screening', 'purchase'
    points_earned: int
    timestamp: datetime
    details: Optional[dict] = None

# ============================================================================
# Leaderboard Models
# ============================================================================

class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: int
    username: str
    points: int
    badges_earned: int
    tier: str
    last_activity: datetime

class LeaderboardResponse(BaseModel):
    """Leaderboard response with user's rank"""
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    user_points: Optional[int] = None
    total_users: int

# ============================================================================
# Stock Analysis Models (Enhanced with gamification)
# ============================================================================

class StockAnalysisRequest(BaseModel):
    """Request to analyze a stock"""
    ticker: str = Field(..., min_length=1, max_length=5)
    analysis_type: str = Field(default="full", pattern="^(quick|full|custom)$")

class StockAnalysisResponse(BaseModel):
    """Stock analysis response with metadata"""
    ticker: str
    analysis_date: datetime
    score: float
    recommendation: str
    analysis_id: str
    points_earned: int = 5  # Points for running analysis

class UserAnalysis(BaseModel):
    """User's analysis history"""
    analysis_id: str
    ticker: str
    analysis_type: str
    score: float
    recommendation: str
    analyzed_at: datetime
    points_earned: int

# ============================================================================
# Subscription & Tier Models
# ============================================================================

class SubscriptionTier(str, Enum):
    """Subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class TierFeatures(BaseModel):
    """Features available in each tier"""
    tier: SubscriptionTier
    max_analyses_per_month: int
    max_screenings_per_month: int
    ai_assistant_enabled: bool
    video_access: bool
    custom_alerts: bool
    portfolio_tracking: bool
    leaderboard_access: bool
    price_monthly: float
    price_annual: float

class SubscriptionInfo(BaseModel):
    """User subscription information"""
    user_id: int
    tier: SubscriptionTier
    started_at: datetime
    renews_at: Optional[datetime] = None
    is_active: bool = True
    auto_renew: bool = True

# ============================================================================
# AI Assistant Models
# ============================================================================

class AIMessage(BaseModel):
    """Message in AI conversation"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: datetime

class AIConversation(BaseModel):
    """AI conversation history"""
    conversation_id: str
    user_id: int
    topic: str
    messages: List[AIMessage]
    created_at: datetime
    updated_at: datetime
    summary: Optional[str] = None

class AIRequest(BaseModel):
    """Request to AI assistant"""
    message: str = Field(..., max_length=5000)
    conversation_id: Optional[str] = None
    context: Optional[str] = None  # e.g., "AAPL analysis context"

class AIResponse(BaseModel):
    """Response from AI assistant"""
    conversation_id: str
    message: str
    confidence: float
    sources: List[str] = []
    timestamp: datetime

# ============================================================================
# Video Models
# ============================================================================

class VideoContent(BaseModel):
    """Video content available in app"""
    video_id: str
    title: str
    description: str
    youtube_id: str
    category: str  # 'tutorial', 'analysis', 'strategy'
    duration_seconds: int
    thumbnail_url: str
    access_tier: SubscriptionTier = SubscriptionTier.FREE
    views: int = 0
    created_at: datetime
    updated_at: datetime

class UserVideoProgress(BaseModel):
    """User's progress on video"""
    video_id: str
    watched_seconds: int
    total_seconds: int
    completed: bool
    last_watched_at: datetime

# ============================================================================
# Response Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    status: str = "success"
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    status_code: int
    message: str
    timestamp: datetime
