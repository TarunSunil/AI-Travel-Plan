from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import sqlite3
import requests  # Added for enhanced Gemini API integration
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from amadeus_api import (search_flights as amadeus_search_flights,
                          get_flight_status, search_cities, search_hotels as amadeus_search_hotels)
from city_data import (get_city_info, get_available_cities, get_airport_codes, 
                        format_city_info, AVAILABLE_CITIES, ESTIMATED_HOTEL_PRICES)
import google.generativeai as genai
from validation import (validate_date_range, validate_budget, validate_passenger_count,
                        validate_city_code, validate_travel_class, sanitize_string)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Set up static folder in the project directory
from pathlib import Path

# Use the local static folder
app = Flask(__name__, static_folder='static')

# Require SECRET_KEY - fail fast if not configured
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set. Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'")
app.secret_key = SECRET_KEY

# Configure rate limiting to prevent API abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# In-memory cache for minimum hotel price lookups
MIN_PRICE_CACHE = {}
MIN_PRICE_CACHE_LOCK = Lock()
MIN_PRICE_CACHE_TTL = timedelta(hours=6)
MIN_PRICE_MAX_WORKERS = 4  # Reduced from 8 to avoid rate limiting

print(f"Flask app initialized with static_folder: {app.static_folder}")

@app.route('/static/<path:filename>')
def static_files(filename):
    try:
        return app.send_static_file(filename)
    except Exception as e:
        return str(e), 404

@app.route('/')
def index():
    # Let Firebase handle authentication state on frontend
    # Users will be redirected by JavaScript if not authenticated
    return render_template('index.html')

# Authentication routes
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Your existing routes...
@app.route('/search_cities', methods=['POST'])
def search_city():
    try:
        query = request.form.get('query', '').strip()

        if not query:
            # If no query, return all available cities from our predefined list
            all_cities = []
            for city_name, city_data in AVAILABLE_CITIES.items():
                all_cities.append({
                    "name": city_name,
                    "country": city_data.get("country", ""),
                    "city_code": city_data.get("city_code", "")
                })
            return jsonify({"available_cities": all_cities})
        else:
            # If there is a query, search using the Amadeus API
            cities = search_cities(query)
            return jsonify({"suggestions": cities})

    except Exception as e:
        print(f"Error in search_cities: {str(e)}")
        return jsonify({"error": str(e)}), 500
 
def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'travel_planner.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def _collect_prices_for_date(dest_name, check_date, fetcher):
    """Helper to collect hotel prices for a specific date."""
    import time
    time.sleep(0.3)  # 300ms delay to avoid Amadeus rate limiting (429 errors)
    
    check_in_str = check_date.strftime('%Y-%m-%d')
    check_out_date = check_date + timedelta(days=1)
    check_out_str = check_out_date.strftime('%Y-%m-%d')
    try:
        hotels = fetcher(
            city_name=dest_name,
            check_in=check_in_str,
            check_out=check_out_str,
            adults=1
        )
    except Exception as fetch_error:
        print(f"Error fetching hotel data for {dest_name} on {check_in_str}: {fetch_error}")
        return []

    prices = []
    if hotels:
        import re
        for hotel in hotels:
            price = hotel.get('price', 0)
            if isinstance(price, str):
                price_match = re.search(r'[\d.]+', str(price).replace('₹', '').replace(',', ''))
                if price_match:
                    price = float(price_match.group())
                else:
                    continue
            prices.append(price)
    return prices


def get_min_price_for_destination(dest_name, fetcher=amadeus_search_hotels, days=7):  # Reduced from 30 to avoid rate limits
    """Fetch minimum hotel price for destination with caching and parallel lookups."""
    dest_clean = dest_name.strip()
    normalized = dest_clean.lower()
    today = datetime.now().date()
    cache_key = (normalized, today, days)
    now = datetime.now()

    with MIN_PRICE_CACHE_LOCK:
        cached_entry = MIN_PRICE_CACHE.get(cache_key)
        if cached_entry and now - cached_entry['timestamp'] < MIN_PRICE_CACHE_TTL:
            return cached_entry['price']

    current_date = datetime.now()
    all_prices = []
    # Reduced to 3 days to avoid rate limiting (was 7)
    days_to_check = min(days, 3)
    with ThreadPoolExecutor(max_workers=MIN_PRICE_MAX_WORKERS) as executor:
        futures = [executor.submit(_collect_prices_for_date, dest_clean, current_date + timedelta(days=i), fetcher)
                   for i in range(days_to_check)]
        for future in as_completed(futures):
            try:
                prices = future.result()
                all_prices.extend(prices)
            except Exception as e:
                print(f"Error retrieving prices from future: {e}")

    min_prices = [price for price in all_prices if price and price > 0]
    min_price = min(min_prices) if min_prices else None
    
    # Fallback to estimated prices if no API data available
    if min_price is None:
        normalized_dest = dest_clean.lower()
        min_price = ESTIMATED_HOTEL_PRICES.get(normalized_dest)
        if min_price:
            print(f"Using estimated hotel price for {dest_clean}: ₹{min_price}")

    with MIN_PRICE_CACHE_LOCK:
        MIN_PRICE_CACHE[cache_key] = {'price': min_price, 'timestamp': now}

    return min_price


@app.route('/get_min_prices', methods=['POST'])
@limiter.limit("30 per minute")  # Higher limit as this uses cache
def get_min_prices():
    try:
        origin = request.form.get('startPoint', '').strip()
        destination = request.form.get('destination', '').strip()

        if not origin or not destination:
            return jsonify({"error": "Origin and destination are required"}), 400

        dest_name = destination.split(",")[0].strip()

        print(f"Getting min hotel prices for {dest_name}")

        min_price = get_min_price_for_destination(dest_name)

        return jsonify({
            'min_hotel_price': f"₹{min_price:,.0f}" if min_price else "N/A"
        })

    except Exception as e:
        print(f"Error in get_min_prices: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/search_flights', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to prevent API quota exhaustion
def search_flights():
    try:
        # Use the reliable city codes sent from the frontend
        origin_code = request.form.get('startPointCode', '').strip().upper()
        dest_code = request.form.get('destinationCode', '').strip().upper()
        
        departure_date = request.form.get('startDate', '').strip()
        return_date = request.form.get('endDate', '').strip()
        adults = request.form.get('adults', '1')
        travel_class = request.form.get('travelClass', 'ECONOMY').upper()
        
        # Validate required fields
        if not origin_code or not dest_code or not departure_date:
            return jsonify({"error": "Origin, destination, and departure date are required"}), 400
        
        # Validate city codes
        is_valid, error = validate_city_code(origin_code, "Origin")
        if not is_valid:
            return jsonify({"error": error}), 400
        
        is_valid, error = validate_city_code(dest_code, "Destination")
        if not is_valid:
            return jsonify({"error": error}), 400
        
        # Validate date range
        is_valid, error = validate_date_range(departure_date, return_date)
        if not is_valid:
            return jsonify({"error": error}), 400
        
        # Validate passenger count
        is_valid, error = validate_passenger_count(adults, "Adults")
        if not is_valid:
            return jsonify({"error": error}), 400
        adults = int(adults)
        
        # Validate travel class
        is_valid, error = validate_travel_class(travel_class)
        if not is_valid:
            return jsonify({"error": error}), 400
        
        print(f"Flight search - Origin Code: {origin_code}, Destination Code: {dest_code}, Date: {departure_date}")
        
        # Search for flights using Amadeus API with INR currency
        flights = amadeus_search_flights(
            origin=origin_code,
            destination=dest_code,
            departure_date=departure_date,
            return_date=return_date if return_date else None,
            adults=adults,
            travel_class=travel_class,
            currency='INR'
        )
        
        if flights:
            # Return raw data without formatting - let frontend handle formatting
            limited_flights = flights[:3]
            for flight in limited_flights:
                # Ensure price is numeric (remove any formatting)
                if 'price' in flight:
                    price_val = flight['price']
                    if isinstance(price_val, str):
                        # Extract numeric value from formatted string
                        import re
                        price_match = re.search(r'[\d.]+', str(price_val).replace('₹', '').replace(',', ''))
                        if price_match:
                            flight['price'] = float(price_match.group())
                        else:
                            flight['price'] = 0
                if 'currency' not in flight:
                    flight['currency'] = 'INR'
            
            return jsonify(limited_flights)
        
        return jsonify({"error": "No flights found for the specified criteria"}), 404
    
    except Exception as e:
        print(f"Error in search_flights: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/search_hotels', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to prevent API quota exhaustion
def search_hotels():
    try:
        destination = sanitize_string(request.form.get('destination', '').strip())
        check_in_date = request.form.get('startDate', '').strip()
        check_out_date = request.form.get('endDate', '').strip()
        adults = request.form.get('adults', '1')
        
        # Validate required fields
        if not destination:
            return jsonify({"error": "Destination is required"}), 400
        
        # Validate date range
        is_valid, error = validate_date_range(check_in_date, check_out_date)
        if not is_valid:
            return jsonify({"error": error}), 400
        
        # Validate guest count
        is_valid, error = validate_passenger_count(adults, "Guests")
        if not is_valid:
            return jsonify({"error": error}), 400
        adults = int(adults)
        
        print(f"Hotel search - Destination: {destination}")
        
        dest_base = destination.split(",")[0].strip()
        print(f"Parsed destination: {dest_base}")
        
        # Get hotel data (enhanced to get more real data)
        hotels = amadeus_search_hotels(
            city_name=dest_base,
            check_in=check_in_date,
            check_out=check_out_date,
            adults=adults
        )
            
        if hotels:
            # Return raw data without formatting - let frontend handle formatting
            limited_hotels = hotels[:3]
            for hotel in limited_hotels:
                # Ensure price is numeric
                if 'price' in hotel:
                    price_val = hotel['price']
                    if isinstance(price_val, str):
                        # Extract numeric value from formatted string
                        import re
                        price_match = re.search(r'[\d.]+', str(price_val).replace('₹', '').replace(',', ''))
                        if price_match:
                            hotel['price'] = float(price_match.group())
                        else:
                            hotel['price'] = 0
                if 'currency' not in hotel:
                    hotel['currency'] = 'INR'
            
            return jsonify(limited_hotels)
        
        # If no hotels from API, return estimated prices as fallback
        dest_lower = dest_base.lower()
        if dest_lower in ESTIMATED_HOTEL_PRICES:
            estimated_price = ESTIMATED_HOTEL_PRICES[dest_lower]
            fallback_hotels = [
                {
                    'name': f'Hotels in {dest_base}',
                    'rating': 4.0,
                    'price': estimated_price,
                    'currency': 'INR',
                    'location': f'{dest_base} City Center',
                    'description': f'Estimated average hotel price in {dest_base}. Actual prices may vary.',
                    'isEstimate': True
                }
            ]
            print(f"Returning fallback hotel data for {dest_base}: ₹{estimated_price}")
            return jsonify(fallback_hotels)

        return jsonify([])  # Return empty array if no data available
    
    except Exception as e:
        print(f"Error in search_hotels: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/flight_status', methods=['POST'])
def flight_status():
    try:
        carrier_code = request.form['carrierCode']
        flight_number = request.form['flightNumber']
        departure_date = request.form['departureDate']
        
        status = get_flight_status(carrier_code, flight_number, departure_date)
        
        if status:
            return jsonify(status)
        else:
            return jsonify({"error": "Flight status not found"}), 404
    except Exception as e:
        print(f"Error in flight_status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chatbot', methods=['POST'])
@limiter.limit("20 per minute")  # Slightly higher limit for chatbot
def chatbot():
    user_message = request.form['message']
    destination = request.form.get('destination', '').strip()
    origin = request.form.get('startPoint', '').strip()  # Add this line
    start_date = request.form.get('startDate', '')
    end_date = request.form.get('endDate', '')

    if not GEMINI_API_KEY:
        return jsonify({"response": "API key is missing. Please check your configuration."})

    # Check if the question is about flights or hotels
    message_lower = user_message.lower()
    
    # Get relevant flights data using existing Amadeus API
    if any(word in message_lower for word in ['flight', 'airline', 'fly', 'flying', 'airport']):
        if not destination:
            return jsonify({"response": "Please specify a destination to search for flights."})
        
        if not origin:
            return jsonify({"response": "Please specify an origin city to search for flights."})
        
        try:
            # Use the user-selected origin instead of hardcoded "Delhi"
            origin_name = origin.split(",")[0].strip()  # Remove country part if present
            dest_name = destination.split(",")[0].strip()
            
            origin_codes = get_airport_codes(origin_name)
            dest_codes = get_airport_codes(dest_name)
            
            if not origin_codes or not dest_codes:
                return jsonify({"response": f"Sorry, I couldn't find airport information for {origin_name} or {dest_name}."})
            
            # Get current date as default
            from datetime import datetime
            departure_date = start_date if start_date else datetime.now().strftime('%Y-%m-%d')
            
            flights = amadeus_search_flights(
                origin=origin_codes[0],
                destination=dest_codes[0], 
                departure_date=departure_date,
                adults=1,
                currency='INR'
            )
            
            if not flights:
                return jsonify({"response": f"I don't have any flight information available from {origin_name} to {dest_name} at the moment."})
            
            # Format flight information with HTML - use camelCase properties
            response = f"Here are the available flights from {origin_name} to {dest_name}:<br><br>"
            for flight in flights[:3]:  # Limit to 3 flights
                price = flight.get('price', 'N/A')
                airline = flight.get('airline', 'Unknown Airline')
                departure = flight.get('departureTime', 'N/A')
                flight_num = flight.get('flightNumber', 'N/A')
                
                # Format the departure time for display
                try:
                    if departure != 'N/A':
                        from datetime import datetime
                        dt = datetime.fromisoformat(departure.replace('Z', '+00:00'))
                        departure = dt.strftime('%H:%M')
                except:
                    departure = 'N/A'
                
                response += f"• <strong>{airline} {flight_num}</strong>: ₹{price:,.0f} - Departure: {departure}<br>"
            
            return jsonify({"response": response})
            
        except Exception as e:
            print(f"Error getting flight data: {str(e)}")
            return jsonify({"response": f"Sorry, I encountered an error while searching for flights from {origin if origin else 'your location'} to {destination if destination else 'your destination'}."})
    
    # If question is about hotels
    elif any(word in message_lower for word in ['hotel', 'accommodation', 'stay', 'lodging', 'room']):
        if not destination:
            return jsonify({"response": "Please specify a destination to search for hotels."})
        
        try:
            # Use existing Amadeus API function (currently mock data)
            from datetime import datetime, timedelta
            check_in = start_date if start_date else datetime.now().strftime('%Y-%m-%d')
            check_out = end_date if end_date else (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            
            hotels = amadeus_search_hotels(
                city_name=destination,
                check_in=check_in,
                check_out=check_out,
                adults=1
            )
            
            if not hotels:
                return jsonify({"response": f"I don't have any hotel information available for {destination} at the moment."})
            
            # Format hotel information with HTML
            response = f"Here are the available hotels in {destination}:<br><br>"
            for hotel in hotels[:3]:  # Limit to 3 hotels
                name = hotel.get('name', 'Unknown Hotel')
                price = hotel.get('price', 'N/A')
                rating = hotel.get('rating', 'N/A')
                response += f"• <strong>{name}</strong>: ₹{price}/night - Rating: {rating}/5<br>"
            
            return jsonify({"response": response})
            
        except Exception as e:
            print(f"Error getting hotel data: {str(e)}")
            return jsonify({"response": f"Sorry, I encountered an error while searching for hotels in {destination}."})

    # For other questions, use the enhanced Gemini API
    # Using gemini-1.5-flash as gemini-pro has been deprecated
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    # Enhanced travel context prompt
    date_context = ""
    if start_date and end_date:
        date_context = f"\nThe user is planning to visit from {start_date} to {end_date}. Please consider this date range when providing travel advice, especially for seasonal activities, weather, and events."

    data = {
        "contents": [{
            "parts": [{
                "text": f"""You are a friendly and expert AI travel assistant for a travel planning platform.
Your user is planning a trip with the following details:
- Destination: {destination if destination else 'Not specified'}
- Travel Dates: {start_date} to {end_date if end_date else 'Not specified'}

Your primary goal is to provide helpful, detailed, and practical travel advice.
- Focus on the Indian travel context (e.g., visa requirements, cultural tips, pricing in INR ₹).
- If asked for an itinerary, provide a clear, day-by-day plan with specific suggestions for activities, sights, and food.
- Be conversational and engaging, but keep your answers informative and well-structured.
- If the destination is not specified, ask the user where they would like to go.
- Format your response properly with clear paragraphs and bullet points where appropriate.
- Provide detailed, comprehensive answers rather than brief responses, unless the question is straightforward.

{date_context}

User's question: "{user_message}"

Please provide a detailed, helpful response that addresses their question thoroughly."""
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2048,
            "stopSequences": [],
            "candidateCount": 1
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        
        # Log detailed error information
        if response.status_code != 200:
            print(f"Gemini API Error - Status: {response.status_code}")
            print(f"Response: {response.text}")
            error_msg = "Sorry, the AI assistant is temporarily unavailable. "
            if response.status_code == 404:
                error_msg += "The API endpoint might have changed or the API key is invalid."
            elif response.status_code == 429:
                error_msg += "Too many requests. Please try again in a minute."
            elif response.status_code >= 500:
                error_msg += "The AI service is experiencing issues. Please try again later."
            else:
                error_msg += f"Error code: {response.status_code}"
            return jsonify({"response": error_msg})
        
        if response.status_code == 200:
            response_data = response.json()
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
                
                # Clean up and format the response
                ai_response = ai_response.replace('**', '<strong>').replace('**', '</strong>')
                ai_response = ai_response.replace('*', '•')
                ai_response = ai_response.replace('\n\n', '<br><br>')
                ai_response = ai_response.replace('\n', '<br>')
                
                # Check if response seems incomplete and try to complete it
                if len(ai_response.strip()) < 100 or ai_response.strip().endswith('•') or ai_response.strip().endswith(','):
                    # Make another request to get a more complete response
                    data['contents'][0]['parts'][0]['text'] = f"{data['contents'][0]['parts'][0]['text']}\n\nPlease provide a complete, detailed response of at least 200 words."
                    response = requests.post(api_url, headers=headers, json=data)
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'candidates' in response_data and len(response_data['candidates']) > 0:
                            ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
                            ai_response = ai_response.replace('**', '<strong>').replace('**', '</strong>')
                            ai_response = ai_response.replace('*', '•')
                            ai_response = ai_response.replace('\n\n', '<br><br>')
                            ai_response = ai_response.replace('\n', '<br>')
                
                return jsonify({"response": ai_response})
            else:
                print(f"No candidates in Gemini response: {response_data}")
                return jsonify({"response": "Sorry, I couldn't generate a response. Please try again."})
        else:
            return jsonify({"response": "Sorry, I encountered an error. Please try again later."})
    
    except requests.exceptions.Timeout:
        print(f"Gemini API Timeout")
        return jsonify({"response": "The AI assistant is taking too long to respond. Please try a shorter question."})
    except requests.exceptions.RequestException as e:
        print(f"Gemini API Request Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text[:500]}")
        return jsonify({"response": f"Sorry, I encountered a network error. The AI service might be unavailable."})
    except Exception as e:
        print(f"Unexpected error in chatbot: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"response": f"Sorry, an unexpected error occurred. Please try again."})

@app.route('/search', methods=['POST'])
def search_all():
    try:
        # Extract parameters
        origin_code = request.form.get('startPointCode')
        dest_code = request.form.get('destinationCode')
        destination = request.form.get('destination', '').strip()
        departure_date = request.form.get('startDate')
        return_date = request.form.get('endDate')
        adults = int(request.form.get('adults', '1'))
        travel_class = request.form.get('travelClass', 'ECONOMY')

        results = {
            "flights": [],
            "hotels": []
        }

        # Search Flights
        if origin_code and dest_code and departure_date:
             flights = amadeus_search_flights(
                origin=origin_code,
                destination=dest_code,
                departure_date=departure_date,
                return_date=return_date if return_date else None,
                adults=adults,
                travel_class=travel_class,
                currency='INR'
            )
             if flights:
                 results["flights"] = flights[:3]

        # Search Hotels
        if destination:
            dest_base = destination.split(",")[0].strip()
            hotels = amadeus_search_hotels(
                city_name=dest_base,
                check_in=departure_date,
                check_out=return_date,
                adults=adults
            )
            if hotels:
                results["hotels"] = hotels[:3]
        
        return jsonify(results)

    except Exception as e:
        print(f"Error in /search: {str(e)}")
        return jsonify({"error": str(e)}), 500

import os, sys
REQUIRED_ENV = ["AMADEUS_CLIENT_ID","AMADEUS_CLIENT_SECRET","GEMINI_API_KEY","SECRET_KEY"]
missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
if missing:
    print(f"[BOOT][ERROR] Missing: {', '.join(missing)}", file=sys.stderr)

if __name__ == '__main__':
    app.run(debug=True)