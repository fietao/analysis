# src/security.py
"""
Security utilities for Jarvis application.
Handles sanitization, validation, and protection against common attacks.
"""

import re
import os
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CSV INJECTION PROTECTION
# ============================================================================

def sanitize_csv_value(value: Any) -> str:
    """
    ✅ Prevent CSV injection (formula injection) attacks.
    
    Dangerous characters that Excel/Sheets interprets as formulas:
    - = (equals: starts formula)
    - + (plus: starts formula)
    - - (minus: starts formula)  
    - @ (at: function call)
    - \t (tab: separator)
    - \r (carriage return: separator)
    
    Solution: Prefix with single quote to force text interpretation.
    
    Args:
        value: Value to sanitize
        
    Returns:
        Sanitized string safe for CSV export
    """
    if value is None:
        return ""
    
    str_value = str(value).strip()
    
    # Check for dangerous starting characters
    if str_value and str_value[0] in ['=', '+', '-', '@', '\t', '\r']:
        return f"'{str_value}"  # Excel will treat as text
    
    # Remove any embedded tab/carriage returns (prevent injection)
    str_value = str_value.replace('\t', '').replace('\r', '\n')
    
    return str_value

def sanitize_dataframe_for_csv(df) -> None:
    """
    ✅ In-place sanitization of DataFrame for safe CSV export.
    Prevents formula injection in all string columns.
    
    Args:
        df: pandas DataFrame to sanitize
    """
    import pandas as pd
    
    # Sanitize all object (string) columns
    for col in df.select_dtypes(include=['object']).columns:
        try:
            df[col] = df[col].apply(sanitize_csv_value)
        except Exception as e:
            logger.warning(f"Could not sanitize column {col}: {e}")
            pass

# ============================================================================
# INPUT VALIDATION
# ============================================================================

def validate_ticker(ticker: str) -> str:
    """
    ✅ Validate and normalize ticker symbol.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Uppercase validated ticker
        
    Raises:
        ValueError: If ticker is invalid
    """
    ticker = str(ticker).upper().strip()
    
    if not ticker or len(ticker) > 5:
        raise ValueError("Ticker must be 1-5 characters")
    
    if not ticker.replace("-", "").isalnum():
        raise ValueError("Ticker must contain only letters, numbers, and hyphens")
    
    return ticker

def validate_date_range(start_date: str, end_date: str = None) -> tuple:
    """
    ✅ Validate date range for queries.
    
    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD) or None for today
        
    Returns:
        Tuple of (start_date, end_date) as strings
        
    Raises:
        ValueError: If dates are invalid
    """
    from datetime import datetime, timedelta
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid start_date format: {start_date}")
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid end_date format: {end_date}")
    else:
        end = datetime.now()
    
    if start > end:
        raise ValueError("start_date must be before end_date")
    
    if end > datetime.now():
        raise ValueError("end_date cannot be in the future")
    
    return start_date, end_date or datetime.now().strftime("%Y-%m-%d")

def validate_limit_offset(limit: int = None, offset: int = None) -> tuple:
    """
    ✅ Validate pagination parameters.
    
    Args:
        limit: Number of results (capped at 1000)
        offset: Number of results to skip
        
    Returns:
        Tuple of (limit, offset) validated
    """
    limit = int(limit) if limit else 100
    offset = int(offset) if offset else 0
    
    # Prevent abuse
    if limit < 1 or limit > 1000:
        limit = 100
    if offset < 0:
        offset = 0
    
    return limit, offset

# ============================================================================
# ERROR SANITIZATION
# ============================================================================

def sanitize_error_message(message: str) -> str:
    """
    ✅ Remove sensitive information from error messages.
    Prevents leaking API keys, tokens, file paths, etc.
    
    Args:
        message: Error message to sanitize
        
    Returns:
        Sanitized message safe to log/display
    """
    message = str(message)
    
    # Mask API keys
    message = re.sub(
        r'(api[_-]?key[=:\s]*)[^\s,}"]*',
        r'\1***MASKED***',
        message,
        flags=re.IGNORECASE
    )
    
    # Mask bearer tokens
    message = re.sub(
        r'(bearer\s+)[^\s]*',
        r'\1***MASKED***',
        message,
        flags=re.IGNORECASE
    )
    
    # Mask generic tokens
    message = re.sub(
        r'(token[=:\s]*)[^\s,}"]*',
        r'\1***MASKED***',
        message,
        flags=re.IGNORECASE
    )
    
    # Mask authorization headers
    message = re.sub(
        r'(Authorization:\s*)[^\s]*',
        r'\1***MASKED***',
        message,
        flags=re.IGNORECASE
    )
    
    # Mask file paths (show only filename)
    message = re.sub(
        r'([/\\][^\s,}"]*)',
        r'***PATH***',
        message
    )
    
    return message

# ============================================================================
# FILE HANDLING
# ============================================================================

def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    ✅ Sanitize filename to prevent path traversal and injection attacks.
    
    Removes path separators and whitelists safe characters.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe sanitized filename
    """
    if not filename:
        return "upload"
    
    # Remove path separators
    filename = os.path.basename(filename)
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Whitelist allowed characters
    # Allow: letters, numbers, hyphen, underscore, dot, space
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- ')
    filename = ''.join(c if c in allowed_chars else '_' for c in filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > max_length:
        # Keep extension if present
        if '.' in filename:
            name, ext = filename.rsplit('.', 1)
            filename = name[:max_length - len(ext) - 1] + '.' + ext
        else:
            filename = filename[:max_length]
    
    return filename or "upload"

def verify_file_within_directory(file_path, base_directory) -> bool:
    """
    ✅ Verify that file_path is within base_directory.
    Prevents path traversal attacks using symlinks.
    
    Args:
        file_path: Path to verify
        base_directory: Base directory file should be within
        
    Returns:
        True if file is safe, False otherwise
    """
    from pathlib import Path
    
    try:
        file_path = Path(file_path).resolve()
        base_directory = Path(base_directory).resolve()
        file_path.relative_to(base_directory)
        return True
    except ValueError:
        logger.warning(f"Path traversal detected: {file_path}")
        return False

# ============================================================================
# LOGGING SECURITY
# ============================================================================

class MaskingFormatter(logging.Formatter):
    """
    ✅ Logging formatter that masks sensitive data.
    Prevents secrets from appearing in logs.
    """
    
    def format(self, record):
        # Sanitize the message
        record.msg = sanitize_error_message(str(record.msg))
        
        # Sanitize args if present
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: sanitize_error_message(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(sanitize_error_message(str(arg)) for arg in record.args)
        
        return super().format(record)

# ============================================================================
# RATE LIMITING HELPERS
# ============================================================================

def check_rate_limit_exceeded(current_count: int, limit: int, window_seconds: int) -> bool:
    """
    ✅ Check if rate limit has been exceeded.
    
    Args:
        current_count: Current request count in window
        limit: Maximum requests allowed
        window_seconds: Time window in seconds
        
    Returns:
        True if limit exceeded, False otherwise
    """
    return current_count >= limit

def get_client_identifier(request) -> str:
    """
    ✅ Get client identifier for rate limiting.
    Checks X-Forwarded-For for proxied requests, falls back to client host.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Client identifier (IP address or identifier)
    """
    # Check for forwarded IP (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Fall back to direct client
    return request.client.host if request.client else "unknown"

# ============================================================================
# DEPENDENCY SECURITY
# ============================================================================

def check_package_vulnerabilities() -> List[Dict]:
    """
    ✅ Check for known vulnerabilities in installed packages.
    Requires: pip-audit or safety to be installed.
    
    Returns:
        List of vulnerabilities found
    """
    import subprocess
    import json
    
    vulnerabilities = []
    
    try:
        # Try pip-audit first (modern tool)
        result = subprocess.run(
            ["pip-audit", "--desc"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            vulnerabilities.append({"tool": "pip-audit", "issues": result.stdout})
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.info("pip-audit not available")
    
    try:
        # Fallback to safety
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            try:
                data = json.loads(result.stdout)
                vulnerabilities.extend(data.get("vulnerabilities", []))
            except json.JSONDecodeError:
                vulnerabilities.append({"tool": "safety", "issues": result.stdout})
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.info("safety not available")
    
    return vulnerabilities
