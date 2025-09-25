"""
DEPRECATED (2025-09-25): Simple ad-hoc Amadeus API access script kept only for historical reference.
Will be removed once formal tests exist.
"""
import os
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Amadeus API credentials
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
AMADEUS_BASE_URL = "https://test.api.amadeus.com"  # Use https://api.amadeus.com for production

def get_access_token():
    """Get access token for Amadeus API"""
    url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': AMADEUS_CLIENT_ID,
        'client_secret': AMADEUS_CLIENT_SECRET
    }
    
    try:
        print("Requesting access token...")
        response = requests.post(url, headers=headers, data=data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return None
            
        response_data = response.json()
        return response_data.get('access_token')
    except Exception as e:
        print(f"Error getting access token: {str(e)}")
        return None

def test_flight_search(token):
    """Test direct flight search API"""
    if not token:
        print("No token available")
        return
        
    url = f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    params = {
        'originLocationCode': 'JFK',
        'destinationLocationCode': 'LHR',
        'departureDate': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'adults': 1,
        'max': 5
    }
    
    try:
        print("\nTesting flight search...")
        response = requests.get(url, headers=headers, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return
            
        data = response.json()
        
        if 'data' in data and data['data']:
            print(f"Found {len(data['data'])} flights")
            print("\nSample flight offer:")
            print(f"Price: {data['data'][0]['price']['total']} {data['data'][0]['price']['currency']}")
        else:
            print("No flights found in response")
    except Exception as e:
        print(f"Error searching flights: {str(e)}")

def test_hotel_search(token):
    """Test direct hotel search API"""
    if not token:
        print("No token available")
        return
        
    url = f"{AMADEUS_BASE_URL}/v3/shopping/hotel-offers"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    params = {
        'cityCode': 'LON',
        'checkInDate': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'checkOutDate': (datetime.now() + timedelta(days=32)).strftime('%Y-%m-%d'),
        'adults': 1
    }
    
    try:
        print("\nTesting hotel search...")
        response = requests.get(url, headers=headers, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return
            
        data = response.json()
        
        if 'data' in data and data['data']:
            print(f"Found {len(data['data'])} hotels")
            print("\nSample hotel offer:")
            print(f"Hotel name: {data['data'][0]['hotel']['name']}")
        else:
            print("No hotels found in response")
    except Exception as e:
        print(f"Error searching hotels: {str(e)}")

def main():
    print("=== AMADEUS API DIRECT TEST ===")
    print(f"AMADEUS_CLIENT_ID: {'FOUND' if AMADEUS_CLIENT_ID else 'MISSING'}")
    print(f"AMADEUS_CLIENT_SECRET: {'FOUND' if AMADEUS_CLIENT_SECRET else 'MISSING'}")
    
    token = get_access_token()
    if token:
        print(f"Successfully retrieved access token: {token[:10]}...")
        test_flight_search(token)
        test_hotel_search(token)
    else:
        print("Failed to retrieve access token. API tests cannot proceed.")
    
    print("\n=== TESTS COMPLETED ===")

if __name__ == "__main__":
    main()