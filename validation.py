"""
Input validation utilities for the Travel Planner application.
Provides server-side validation to prevent invalid or malicious inputs.
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:  # RFC 5321
        return False, "Email too long"
    
    return True, None


def validate_date(date_str: str, field_name: str = "Date") -> Tuple[bool, Optional[str]]:
    """
    Validate date format and ensure it's not in the past.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not date_str:
        return False, f"{field_name} is required"
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date < today:
            return False, f"{field_name} cannot be in the past"
        
        # Check if date is too far in the future (more than 1 year)
        max_future_date = today + timedelta(days=365)
        if date > max_future_date:
            return False, f"{field_name} cannot be more than 1 year in the future"
        
        return True, None
    except ValueError:
        return False, f"{field_name} must be in YYYY-MM-DD format"


def validate_date_range(start_date_str: str, end_date_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that end date is after start date.
    
    Args:
        start_date_str: Start date string in YYYY-MM-DD format
        end_date_str: End date string in YYYY-MM-DD format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # First validate individual dates
    is_valid, error = validate_date(start_date_str, "Start date")
    if not is_valid:
        return False, error
    
    if end_date_str:  # End date is optional for one-way trips
        is_valid, error = validate_date(end_date_str, "End date")
        if not is_valid:
            return False, error
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        if end_date <= start_date:
            return False, "End date must be after start date"
        
        # Check if trip duration is reasonable (max 30 days)
        if (end_date - start_date).days > 30:
            return False, "Trip duration cannot exceed 30 days"
    
    return True, None


def validate_budget(budget_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate budget amount.
    
    Args:
        budget_str: Budget amount as string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not budget_str:
        return False, "Budget is required"
    
    try:
        budget = float(budget_str)
        
        if budget <= 0:
            return False, "Budget must be greater than 0"
        
        if budget > 10000000:  # 1 crore INR max
            return False, "Budget exceeds maximum allowed amount"
        
        return True, None
    except ValueError:
        return False, "Budget must be a valid number"


def validate_passenger_count(count_str: str, field_name: str = "Passengers") -> Tuple[bool, Optional[str]]:
    """
    Validate passenger/guest count.
    
    Args:
        count_str: Count as string
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not count_str:
        return False, f"{field_name} count is required"
    
    try:
        count = int(count_str)
        
        if count < 1:
            return False, f"{field_name} count must be at least 1"
        
        if count > 9:  # Most airlines/hotels limit
            return False, f"{field_name} count cannot exceed 9"
        
        return True, None
    except ValueError:
        return False, f"{field_name} count must be a valid number"


def validate_city_code(code: str, field_name: str = "City") -> Tuple[bool, Optional[str]]:
    """
    Validate IATA city/airport code.
    
    Args:
        code: IATA code (3 letters)
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code:
        return False, f"{field_name} code is required"
    
    # IATA codes are 3 letters
    if not re.match(r'^[A-Z]{3}$', code.upper()):
        return False, f"{field_name} code must be a 3-letter IATA code"
    
    return True, None


def validate_travel_class(travel_class: str) -> Tuple[bool, Optional[str]]:
    """
    Validate travel class.
    
    Args:
        travel_class: Travel class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_classes = ['ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST']
    
    if not travel_class:
        return False, "Travel class is required"
    
    if travel_class.upper() not in valid_classes:
        return False, f"Travel class must be one of: {', '.join(valid_classes)}"
    
    return True, None


def sanitize_string(text: str, max_length: int = 200) -> str:
    """
    Sanitize and truncate user input strings.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not text:
        return ""
    
    # Remove potential SQL injection and XSS characters
    sanitized = text.strip()
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
