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
        response = _request_with_retry('POST', url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {str(e)}")
        return None

def _request_with_retry(method, url, headers=None, params=None, data=None, json=None, max_retries=3, backoff_base=0.5):
    """Make HTTP request with basic retry and exponential backoff for 429/5xx."""
    attempt = 0
    while True:
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            else:
                response = requests.post(url, headers=headers, params=params, data=data, json=json)
            # Retry on 429 and 5xx
            if response.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
                wait_s = backoff_base * (2 ** attempt)
                print(f"{method} {url} -> {response.status_code}, retrying in {wait_s:.1f}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait_s)
                attempt += 1
                continue
            return response
        except requests.exceptions.RequestException as e:
            if attempt >= max_retries:
                raise
            wait_s = backoff_base * (2 ** attempt)
            print(f"{method} {url} exception: {e}, retrying in {wait_s:.1f}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait_s)
            attempt += 1

def search_flights(origin, destination, departure_date, return_date=None, adults=1, travel_class='ECONOMY', currency='USD'):
    """Search flights using Amadeus API"""
    print(f"Searching flights: {origin} to {destination} on {departure_date}")
    
    try:
        # Get Amadeus API access token
        token = get_access_token()
        if not token:
            print("Failed to get Amadeus API access token")
            raise Exception("Failed to get Amadeus API access token")
        
        url = f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers"
        headers = {'Authorization': f'Bearer {token}'}
        
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults,
            'currencyCode': currency,
            'max': 15  # Increased for more variety
        }
        
        # Add optional parameters if provided
        if return_date:
            params['returnDate'] = return_date
        if travel_class:
            params['travelClass'] = travel_class
            
        # Make the API request
        print(f"Making request to {url} with params: {params}")
        response = _request_with_retry('GET', url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Flight search error: {response.status_code} - {response.text}")
            raise Exception(f"Flight search API returned: {response.status_code}")
            
        data = response.json()
        print(f"Flight search response received, status {response.status_code}")
        
        flights = []
        if 'data' in data and len(data['data']) > 0:
            print(f"Found {len(data['data'])} flight offers")
            
            # Process each flight offer
            for i, offer in enumerate(data['data']):
                if i >= 10:  # Limit to 10 results
                    break
                
                # Get the first segment of the first itinerary for simple display
                if 'itineraries' in offer and offer['itineraries']:
                    itinerary = offer['itineraries'][0]
                    if 'segments' in itinerary and itinerary['segments']:
                        segment = itinerary['segments'][0]
                        
                        carrier = segment.get('carrierCode', 'Unknown')
                        flight_data = {
                            # Use camelCase for frontend consistency
                            'airline': get_airline_name(carrier),
                            'airlineCode': carrier,
                            'flightNumber': segment.get('number', 'Unknown'),
                            'departureTime': segment.get('departure', {}).get('at', 'N/A'),
                            'arrivalTime': segment.get('arrival', {}).get('at', 'N/A'),
                            'departureAirport': segment.get('departure', {}).get('iataCode', origin),
                            'arrivalAirport': segment.get('arrival', {}).get('iataCode', destination),
                            'price': float(offer.get('price', {}).get('total', 0)),
                            'currency': offer.get('price', {}).get('currency', currency),
                            'duration': itinerary.get('duration', 'N/A')
                        }
                        flights.append(flight_data)
            
            print(f"Processed {len(flights)} flights")
            
            # Deduplicate flights by unique key (airline + flight number + departure time)
            seen = set()
            unique_flights = []
            for flight in flights:
                key = f"{flight['airline']}{flight['flightNumber']}{flight['departureTime']}"
                if key not in seen:
                    seen.add(key)
                    unique_flights.append(flight)
            
            print(f"After deduplication: {len(unique_flights)} unique flights")
            flights = unique_flights
        else:
            print("No flight data found in API response")
        
        # Return up to 3 real flights only
        return flights[:3]
        
    except Exception as e:
        print(f"Error searching flights: {e}")
        return []

def search_hotels(city_name, check_in, check_out, adults=1):
    """Search for hotels - always return only real Amadeus data (no mock)"""
    print(f"Hotel search - Real data only for: {city_name}")
    hotels = []
    try:
        token = get_access_token()
        if token:
            city_code = get_city_code(city_name, token)
            print(f"City code for {city_name}: {city_code}")
            if city_code:
                hotel_list_url = f"{AMADEUS_BASE_URL}/v1/reference-data/locations/hotels/by-city"
                headers = {'Authorization': f'Bearer {token}'}
                params = {
                    'cityCode': city_code,
                    'radius': 50,
                    'radiusUnit': 'KM',
                    'hotelSource': 'ALL'
                }
                print(f"Searching for hotels in {city_name} ({city_code})...")
                hotel_response = _request_with_retry('GET', hotel_list_url, headers=headers, params=params)
                print(f"Hotel list API response status: {hotel_response.status_code}")
                if hotel_response.status_code == 200:
                    hotel_data = hotel_response.json()
                    print(f"Hotel list data: {len(hotel_data.get('data', []))} hotels found")
                    if 'data' in hotel_data and hotel_data['data']:
                        hotel_ids = [hotel.get('hotelId') for hotel in hotel_data['data'][:5]]
                        if hotel_ids:
                            url = f"{AMADEUS_BASE_URL}/v3/shopping/hotel-offers"
                            params = {
                                'hotelIds': ','.join(hotel_ids),
                                'checkInDate': check_in,
                                'checkOutDate': check_out,
                                'adults': adults,
                                'currency': 'INR'
                            }
                            print(f"Fetching offers for {len(hotel_ids)} hotels...")
                            response = _request_with_retry('GET', url, headers=headers, params=params)
                            print(f"Hotel offers API response status: {response.status_code}")
                            if response.status_code == 200:
                                data = response.json()
                                print(f"Hotel offers data: {len(data.get('data', []))} offers returned")
                                if 'data' in data:
                                    for hotel_data in data['data'][:3]:  # Take up to 3 real hotels
                                        try:
                                            hotel_info = hotel_data['hotel']
                                            offer = hotel_data['offers'][0]
                                            hotel_obj = {
                                                'name': hotel_info.get('name', f'Hotel {city_name}'),
                                                'rating': hotel_info.get('rating', 4.0),
                                                'price': float(offer['price']['total']),
                                                'currency': offer['price'].get('currency', 'INR'),
                                                'location': f"{city_name} City Center",
                                                'description': f"Real hotel in {city_name} from Amadeus API",
                                                'amenities': hotel_info.get('amenities', ['WiFi', 'Restaurant'])
                                            }
                                            hotels.append(hotel_obj)
                                            print(f"Successfully parsed hotel: {hotel_obj['name']} - ₹{hotel_obj['price']}")
                                        except (KeyError, ValueError) as e:
                                            print(f"Error parsing real hotel data: {e}")
                                            continue
                            else:
                                print(f"Hotel offers API error: {response.status_code} - {response.text[:200]}")
                                # If no data or an error, try a fallback date window (+30 days)
                                try:
                                    ci_dt = datetime.strptime(check_in, '%Y-%m-%d')
                                    co_dt = datetime.strptime(check_out, '%Y-%m-%d')
                                    alt_ci = (ci_dt + timedelta(days=30)).strftime('%Y-%m-%d')
                                    alt_co = (co_dt + timedelta(days=30)).strftime('%Y-%m-%d')
                                    params_alt = dict(params)
                                    params_alt['checkInDate'] = alt_ci
                                    params_alt['checkOutDate'] = alt_co
                                    print(f"Retrying hotel offers with alternate dates {alt_ci} -> {alt_co}")
                                    response_alt = _request_with_retry('GET', url, headers=headers, params=params_alt)
                                    if response_alt.status_code == 200:
                                        data_alt = response_alt.json()
                                        for hotel_data in data_alt.get('data', [])[:3]:
                                            try:
                                                hotel_info = hotel_data['hotel']
                                                offer = hotel_data['offers'][0]
                                                hotel_obj = {
                                                    'name': hotel_info.get('name', f'Hotel {city_name}'),
                                                    'rating': hotel_info.get('rating', 4.0),
                                                    'price': float(offer['price']['total']),
                                                    'currency': offer['price'].get('currency', 'INR'),
                                                    'location': f"{city_name} City Center",
                                                    'description': f"Real hotel in {city_name} (alt dates) from Amadeus API",
                                                    'amenities': hotel_info.get('amenities', ['WiFi', 'Restaurant'])
                                                }
                                                hotels.append(hotel_obj)
                                            except Exception:
                                                continue
                                except Exception as e:
                                    print(f"Alternate date retry failed: {e}")
                    else:
                        print(f"No hotel IDs found for {city_name}")
                else:
                    print(f"Hotel list API error: {hotel_response.status_code} - {hotel_response.text[:200]}")
            else:
                print(f"Could not find city code for {city_name}")
        else:
            print(f"Could not get access token")
    except Exception as e:
        print(f"Error fetching real hotel data: {e}")
        import traceback
        traceback.print_exc()
    print(f"Returning {len(hotels)} real hotels for {city_name}")
    return hotels

def get_city_code(city_name, token):
    """Get IATA city code for hotel search"""
    url = f"{AMADEUS_BASE_URL}/v1/reference-data/locations/cities"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    params = {
        'keyword': city_name,
        'max': 1
    }
    
    try:
        response = _request_with_retry('GET', url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            return data['data'][0]['iataCode']
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error getting city code: {str(e)}")
        return None

def get_airline_name(carrier_code):
    """Get airline name from carrier code"""
    airline_codes = {
        '6E': 'IndiGo',
        'AI': 'Air India',
        'SG': 'SpiceJet',
        'G8': 'GoAir',
        'I5': 'AirAsia India',
        'UK': 'Vistara',
        'EK': 'Emirates',
        'QR': 'Qatar Airways',
        'EY': 'Etihad Airways',
        'TK': 'Turkish Airlines',
        'LH': 'Lufthansa',
        'BA': 'British Airways',
        'AF': 'Air France',
        'KL': 'KLM',
        'SQ': 'Singapore Airlines',
        'TG': 'Thai Airways',
        'MH': 'Malaysia Airlines',
        'CX': 'Cathay Pacific',
        'JL': 'Japan Airlines',
        'NH': 'ANA'
    }
    
    return airline_codes.get(carrier_code, f"{carrier_code} Airlines")

def search_cities(query):
    """Search for cities/airports"""
    token = get_access_token()
    if not token:
        return []
    
    url = f"{AMADEUS_BASE_URL}/v1/reference-data/locations"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    params = {
        'keyword': query,
        'subType': 'AIRPORT,CITY',
        'sort': 'analytics.travelers.score',
        'view': 'LIGHT'
    }
    
    try:
        response = _request_with_retry('GET', url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        locations = []
        if 'data' in data:
            for location in data['data']:
                try:
                    location_info = {
                        'name': location['name'],
                        'iataCode': location['iataCode'],
                        'subType': location['subType'],
                        'address': location.get('address', {})
                    }
                    locations.append(location_info)
                except KeyError as e:
                    print(f"Error parsing location data: {e}")
                    continue
        
        return locations
        
    except requests.exceptions.RequestException as e:
        print(f"Error searching cities: {str(e)}")
        return []

def get_flight_status(carrier_code, flight_number, departure_date):
    """Get flight status"""
    token = get_access_token()
    if not token:
        return None
    
    url = f"{AMADEUS_BASE_URL}/v2/schedule/flights"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    params = {
        'carrierCode': carrier_code,
        'flightNumber': flight_number,
        'scheduledDepartureDate': departure_date
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            flight = data['data'][0]
            return {
                'flightNumber': f"{carrier_code}{flight_number}",
                'status': 'Scheduled',  # Basic status
                'departure': flight['flightPoints'][0],
                'arrival': flight['flightPoints'][1]
            }
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error getting flight status: {str(e)}")
        return None
