"""
Unit tests for validation module.
"""

import pytest
from datetime import datetime, timedelta
from validation import (
    validate_email,
    validate_date,
    validate_date_range,
    validate_budget,
    validate_passenger_count,
    validate_city_code,
    validate_travel_class,
    sanitize_string
)


class TestEmailValidation:
    """Tests for email validation."""
    
    def test_valid_email(self):
        is_valid, error = validate_email("user@example.com")
        assert is_valid is True
        assert error is None
    
    def test_invalid_email_format(self):
        is_valid, error = validate_email("invalid-email")
        assert is_valid is False
        assert "Invalid email format" in error
    
    def test_empty_email(self):
        is_valid, error = validate_email("")
        assert is_valid is False
        assert "required" in error


class TestDateValidation:
    """Tests for date validation."""
    
    def test_valid_future_date(self):
        future_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        is_valid, error = validate_date(future_date)
        assert is_valid is True
        assert error is None
    
    def test_past_date(self):
        past_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        is_valid, error = validate_date(past_date)
        assert is_valid is False
        assert "past" in error
    
    def test_invalid_date_format(self):
        is_valid, error = validate_date("2026-13-45")
        assert is_valid is False
        assert "format" in error
    
    def test_date_too_far_future(self):
        far_future = (datetime.now() + timedelta(days=400)).strftime('%Y-%m-%d')
        is_valid, error = validate_date(far_future)
        assert is_valid is False
        assert "1 year" in error


class TestDateRangeValidation:
    """Tests for date range validation."""
    
    def test_valid_date_range(self):
        start = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        end = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        is_valid, error = validate_date_range(start, end)
        assert is_valid is True
        assert error is None
    
    def test_end_before_start(self):
        start = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        end = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        is_valid, error = validate_date_range(start, end)
        assert is_valid is False
        assert "after start date" in error
    
    def test_duration_too_long(self):
        start = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        end = (datetime.now() + timedelta(days=40)).strftime('%Y-%m-%d')
        is_valid, error = validate_date_range(start, end)
        assert is_valid is False
        assert "30 days" in error


class TestBudgetValidation:
    """Tests for budget validation."""
    
    def test_valid_budget(self):
        is_valid, error = validate_budget("50000")
        assert is_valid is True
        assert error is None
    
    def test_negative_budget(self):
        is_valid, error = validate_budget("-100")
        assert is_valid is False
        assert "greater than 0" in error
    
    def test_budget_too_large(self):
        is_valid, error = validate_budget("20000000")
        assert is_valid is False
        assert "maximum" in error
    
    def test_invalid_budget_format(self):
        is_valid, error = validate_budget("abc")
        assert is_valid is False
        assert "valid number" in error


class TestPassengerCount:
    """Tests for passenger count validation."""
    
    def test_valid_count(self):
        is_valid, error = validate_passenger_count("2")
        assert is_valid is True
        assert error is None
    
    def test_zero_passengers(self):
        is_valid, error = validate_passenger_count("0")
        assert is_valid is False
        assert "at least 1" in error
    
    def test_too_many_passengers(self):
        is_valid, error = validate_passenger_count("15")
        assert is_valid is False
        assert "cannot exceed 9" in error


class TestCityCodeValidation:
    """Tests for IATA city code validation."""
    
    def test_valid_city_code(self):
        is_valid, error = validate_city_code("DEL")
        assert is_valid is True
        assert error is None
    
    def test_lowercase_city_code(self):
        # Should accept lowercase and uppercase it automatically
        is_valid, error = validate_city_code("del")
        assert is_valid is True  # Function uppercases before validation
        assert error is None
    
    def test_invalid_code_length(self):
        is_valid, error = validate_city_code("DELH")
        assert is_valid is False
        assert "3-letter" in error


class TestTravelClassValidation:
    """Tests for travel class validation."""
    
    def test_valid_classes(self):
        for travel_class in ['ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST']:
            is_valid, error = validate_travel_class(travel_class)
            assert is_valid is True
            assert error is None
    
    def test_invalid_class(self):
        is_valid, error = validate_travel_class("SUPER_LUXURY")
        assert is_valid is False
        assert "must be one of" in error


class TestStringSanitization:
    """Tests for string sanitization."""
    
    def test_basic_sanitization(self):
        result = sanitize_string("  Mumbai  ")
        assert result == "Mumbai"
    
    def test_remove_dangerous_chars(self):
        result = sanitize_string("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result
    
    def test_truncate_long_string(self):
        long_string = "a" * 300
        result = sanitize_string(long_string, max_length=200)
        assert len(result) == 200
    
    def test_empty_string(self):
        result = sanitize_string("")
        assert result == ""
