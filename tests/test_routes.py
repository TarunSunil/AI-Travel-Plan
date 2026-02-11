"""
Integration tests for Flask routes.
"""

import pytest
from datetime import datetime, timedelta


@pytest.mark.integration
class TestRoutes:
    """Tests for Flask routes."""
    
    def test_home_page(self, client):
        """Test that home page loads."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_login_page(self, client):
        """Test that login page loads."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_signup_page(self, client):
        """Test that signup page loads."""
        response = client.get('/signup')
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.api
class TestSearchFlights:
    """Tests for flight search endpoint."""
    
    def test_search_flights_missing_params(self, client):
        """Test flight search with missing parameters."""
        response = client.post('/search_flights', data={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_search_flights_invalid_city_code(self, client):
        """Test flight search with invalid city code."""
        future_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        response = client.post('/search_flights', data={
            'startPointCode': 'INVALID',
            'destinationCode': 'BOM',
            'startDate': future_date,
            'adults': '1',
            'travelClass': 'ECONOMY'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert '3-letter' in data['error']
    
    def test_search_flights_past_date(self, client):
        """Test flight search with past date."""
        past_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = client.post('/search_flights', data={
            'startPointCode': 'DEL',
            'destinationCode': 'BOM',
            'startDate': past_date,
            'adults': '1',
            'travelClass': 'ECONOMY'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'past' in data['error']
    
    def test_search_flights_invalid_passenger_count(self, client):
        """Test flight search with invalid passenger count."""
        future_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        response = client.post('/search_flights', data={
            'startPointCode': 'DEL',
            'destinationCode': 'BOM',
            'startDate': future_date,
            'adults': '15',  # Too many
            'travelClass': 'ECONOMY'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'exceed 9' in data['error']


@pytest.mark.integration
@pytest.mark.api
class TestSearchHotels:
    """Tests for hotel search endpoint."""
    
    def test_search_hotels_missing_destination(self, client):
        """Test hotel search with missing destination."""
        response = client.post('/search_hotels', data={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_search_hotels_invalid_date_range(self, client):
        """Test hotel search with invalid date range."""
        start = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        end = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        response = client.post('/search_hotels', data={
            'destination': 'Mumbai',
            'startDate': start,
            'endDate': end,
            'adults': '2'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'after start date' in data['error']
