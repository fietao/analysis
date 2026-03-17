"""
JWT Authentication System
Handles token creation, validation, and user authentication
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
import secrets
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-to-a-real-secret-key-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing setup
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # High rounds for security
)

# ============================================================================
# Password Management
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {sanitize_error_message(str(e))}")
        return False

# ============================================================================
# JWT Token Management
# ============================================================================

def create_access_token(
    user_id: int,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User ID
        email: User email
        role: User role ('free', 'pro', 'enterprise', 'admin')
        expires_delta: Custom expiration time
    
    Returns:
        JWT token string
    """
    to_encode = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "type": "access"
    }
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Access token created for user {user_id}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {sanitize_error_message(str(e))}")
        raise

def create_refresh_token(user_id: int, email: str) -> str:
    """
    Create JWT refresh token (longer expiration)
    
    Args:
        user_id: User ID
        email: User email
    
    Returns:
        JWT refresh token string
    """
    to_encode = {
        "user_id": user_id,
        "email": email,
        "type": "refresh",
        "jti": secrets.token_urlsafe(16)  # JWT ID (one-time use)
    }
    
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Refresh token created for user {user_id}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Refresh token creation error: {sanitize_error_message(str(e))}")
        raise

def verify_token(token: str) -> Tuple[bool, Optional[dict]]:
    """
    Verify JWT token and extract payload
    
    Args:
        token: JWT token to verify
    
    Returns:
        Tuple of (is_valid, payload_dict)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True, payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return False, None
    except Exception as e:
        logger.error(f"Token verification error: {sanitize_error_message(str(e))}")
        return False, None

def refresh_access_token(refresh_token: str) -> Optional[Tuple[str, str]]:
    """
    Create new access token from refresh token
    
    Args:
        refresh_token: Valid refresh token
    
    Returns:
        Tuple of (new_access_token, new_refresh_token) or None if invalid
    """
    is_valid, payload = verify_token(refresh_token)
    
    if not is_valid:
        return None
    
    if payload.get("type") != "refresh":
        logger.warning("Invalid token type for refresh")
        return None
    
    user_id = payload.get("user_id")
    email = payload.get("email")
    
    if not user_id or not email:
        logger.warning("Missing user info in refresh token")
        return None
    
    # Create new tokens
    new_access = create_access_token(user_id, email, payload.get("role", "free"))
    new_refresh = create_refresh_token(user_id, email)
    
    logger.info(f"Access token refreshed for user {user_id}")
    return new_access, new_refresh

# ============================================================================
# Token Validation Utilities
# ============================================================================

def extract_user_id_from_token(token: str) -> Optional[int]:
    """Extract user_id from token"""
    is_valid, payload = verify_token(token)
    if is_valid and payload:
        return payload.get("user_id")
    return None

def extract_user_email_from_token(token: str) -> Optional[str]:
    """Extract email from token"""
    is_valid, payload = verify_token(token)
    if is_valid and payload:
        return payload.get("email")
    return None

def extract_user_role_from_token(token: str) -> Optional[str]:
    """Extract role from token"""
    is_valid, payload = verify_token(token)
    if is_valid and payload:
        return payload.get("role")
    return None

# ============================================================================
# Security Helpers
# ============================================================================

def sanitize_error_message(message: str) -> str:
    """
    Sanitize error messages to prevent secret exposure
    Masks API keys, tokens, and sensitive paths
    """
    import re
    
    # Mask API keys
    message = re.sub(r'sk_[a-zA-Z0-9_]{20,}', 'sk_***MASKED***', message)
    message = re.sub(r'pk_[a-zA-Z0-9_]{20,}', 'pk_***MASKED***', message)
    
    # Mask JWT tokens
    message = re.sub(r'eyJ[A-Za-z0-9_-]{20,}', 'eyJ***MASKED***', message)
    
    # Mask database passwords
    message = re.sub(r'password[\'"]?\s*[:=]\s*[\'"]?[^\s\'"]+', 'password=***MASKED***', message, flags=re.IGNORECASE)
    
    # Mask file paths
    message = re.sub(r'C:\\Users\\[^\\]+', 'C:\\Users\\***', message)
    message = re.sub(r'/home/[^/]+', '/home/***', message)
    
    return message

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)

# ============================================================================
# Compliance & Security Headers
# ============================================================================

def get_auth_headers() -> dict:
    """Headers for secure token transmission"""
    return {
        "Authorization": "Bearer <token>",
        "X-Token-Type": "JWT",
        "Cache-Control": "no-store, max-age=0"
    }

def validate_token_not_revoked(token: str, revoked_tokens: list) -> bool:
    """
    Check if token is in revocation list
    (Implement actual revocation with Redis in production)
    """
    return token not in revoked_tokens

# ============================================================================
# Password Validation
# ============================================================================

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements
    
    Requirements:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    import re
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets security requirements"

# ============================================================================
# Session Management Helpers
# ============================================================================

def create_session_token(user_id: int) -> str:
    """Create a session token for maintaining user session"""
    to_encode = {
        "user_id": user_id,
        "type": "session",
        "created_at": datetime.utcnow().isoformat()
    }
    
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_session_token(token: str, expected_user_id: int) -> bool:
    """Verify a session token belongs to the expected user"""
    is_valid, payload = verify_token(token)
    
    if not is_valid or not payload:
        return False
    
    if payload.get("type") != "session":
        return False
    
    if payload.get("user_id") != expected_user_id:
        return False
    
    return True
