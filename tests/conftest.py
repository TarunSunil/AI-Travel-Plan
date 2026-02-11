"""
Pytest fixtures and configuration for Travel Planner tests.
"""

import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app as flask_app


@pytest.fixture
def app():
    """Create and configure a Flask application instance for testing."""
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-for-testing-only",
    })
    
    yield flask_app


@pytest.fixture
def client(app):
    """A test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def sample_flight_data():
    """Sample flight data for testing."""
    return {
        'airline': 'Test Airlines',
        'flightNumber': 'TA123',
        'price': 5000,
        'currency': 'INR',
        'departureTime': '2026-02-15T10:00:00',
        'arrivalTime': '2026-02-15T12:00:00',
        'departureAirport': 'DEL',
        'arrivalAirport': 'BOM'
    }


@pytest.fixture
def sample_hotel_data():
    """Sample hotel data for testing."""
    return {
        'name': 'Test Hotel',
        'location': 'Mumbai, India',
        'price': 3000,
        'currency': 'INR',
        'rating': 4.5,
        'description': 'A test hotel',
        'amenities': ['WiFi', 'Pool']
    }


@pytest.fixture
def valid_search_params():
    """Valid search parameters for testing."""
    future_date = datetime.now().strftime('%Y-%m-%d')
    return {
        'startPoint': 'Delhi, India',
        'startPointCode': 'DEL',
        'destination': 'Mumbai, India',
        'destinationCode': 'BOM',
        'startDate': future_date,
        'endDate': future_date,
        'adults': '2',
        'travelClass': 'ECONOMY',
        'budget': '50000'
    }
