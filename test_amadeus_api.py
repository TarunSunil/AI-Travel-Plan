"""
Test script for Amadeus API functionality
"""
import os
from dotenv import load_dotenv
from amadeus_api import get_access_token, search_flights, search_hotels, search_cities
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

def test_flight_search():
    """Test flight search functionality"""
    print("\n--- TESTING FLIGHT SEARCH ---")
    
    # Test parameters
    origin = "JFK"  # New York
    destination = "LHR"  # London
    departure_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"Searching flights: {origin} to {destination} on {departure_date}")
    
    try:
        flights = search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            currency='INR'
        )
        
        print(f"Found {len(flights)} flights")
        
        # Display first flight details
        if flights:
            print("\nSample flight details:")
            flight = flights[0]
            for key, value in flight.items():
                print(f"  {key}: {value}")
        else:
            print("No flights found")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

def test_hotel_search():
    """Test hotel search functionality"""
    print("\n--- TESTING HOTEL SEARCH ---")
    
    # Test parameters
    city = "London"
    check_in = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    check_out = (datetime.now() + timedelta(days=32)).strftime('%Y-%m-%d')
    
    print(f"Searching hotels in {city} from {check_in} to {check_out}")
    
    try:
        hotels = search_hotels(
            city_name=city,
            check_in=check_in,
            check_out=check_out,
            adults=1
        )
        
        print(f"Found {len(hotels)} hotels")
        
        # Display first hotel details
        if hotels:
            print("\nSample hotel details:")
            hotel = hotels[0]
            for key, value in hotel.items():
                print(f"  {key}: {value}")
        else:
            print("No hotels found")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

def test_city_search():
    """Test city search functionality"""
    print("\n--- TESTING CITY SEARCH ---")
    
    # Test parameters
    query = "London"
    
    print(f"Searching for cities matching: {query}")
    
    try:
        cities = search_cities(query)
        
        print(f"Found {len(cities)} matching locations")
        
        # Display first few cities
        if cities:
            print("\nTop matching locations:")
            for i, city in enumerate(cities[:3]):
                print(f"\nLocation {i+1}:")
                for key, value in city.items():
                    if key != 'address':  # Skip address to keep output clean
                        print(f"  {key}: {value}")
        else:
            print("No locations found")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

def test_access_token():
    """Test access token retrieval"""
    print("\n--- TESTING ACCESS TOKEN ---")
    
    try:
        token = get_access_token()
        if token:
            print(f"Successfully retrieved access token: {token[:10]}...")
        else:
            print("Failed to retrieve access token")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    print("=== AMADEUS API TEST SCRIPT ===")
    print(f"AMADEUS_CLIENT_ID: {'FOUND' if os.getenv('AMADEUS_CLIENT_ID') else 'MISSING'}")
    print(f"AMADEUS_CLIENT_SECRET: {'FOUND' if os.getenv('AMADEUS_CLIENT_SECRET') else 'MISSING'}")
    
    # Run tests
    test_access_token()
    test_flight_search()
    test_hotel_search()
    test_city_search()
    
    print("\n=== TESTS COMPLETED ===")