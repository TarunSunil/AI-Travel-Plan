from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import sys
import re
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

from travel_api import (
    search_flights as tp_search_flights,
    search_hotels as tp_search_hotels,
    get_min_hotel_price,
    cache_health,
)
from city_data import (
    get_airport_codes,
    AVAILABLE_CITIES,
    ESTIMATED_HOTEL_PRICES,
)
# Active DB: SQLite via database.py
# To migrate to Supabase PostgreSQL → see docs/SUPABASE_MIGRATION.md
# and swap: from supabase_db import get_db_connection
from validation import (validate_date_range, validate_budget, validate_passenger_count,
                        validate_city_code, validate_travel_class, sanitize_string)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Set up static folder in the project directory (ensure it exists)
from pathlib import Path

# Use the local static folder
app = Flask(__name__, static_folder='static')

# Require SECRET_KEY - fail fast if not configured
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set. Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'")
app.secret_key = SECRET_KEY

# Required: Gemini (used by chatbot + synthesis fallbacks)
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable must be set (Gemini API key).")

# Optional free travel APIs (warn only)
if not os.getenv("AVIATIONSTACK_KEY"):
    print("[BOOT][WARN] AVIATIONSTACK_KEY missing — flight results may fall back to OpenSky/AI/static.", file=sys.stderr)
if not os.getenv("OPENTRIPMAP_KEY"):
    print("[BOOT][WARN] OPENTRIPMAP_KEY missing — hotel results may fall back to AI/static.", file=sys.stderr)

# CSRF protection for all POST routes (AJAX FormData includes csrf_token hidden inputs)
csrf = CSRFProtect(app)

# Inject firebase config into templates from environment variables
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY", ""),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId": os.getenv("FIREBASE_APP_ID", ""),
}


@app.context_processor
def inject_firebase_config():
    return {"firebase_config": FIREBASE_CONFIG}

# Configure rate limiting to prevent API abuse
REDIS_URL = os.getenv("REDIS_URL")
storage_uri = REDIS_URL if REDIS_URL else "memory://"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=storage_uri,
)

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
        # Free-tier mode: we return the predefined list only (no external lookups).
        all_cities = []
        for city_name, city_data in AVAILABLE_CITIES.items():
            all_cities.append({
                "name": city_name,
                "country": city_data.get("country", ""),
                "city_code": city_data.get("city_code", "")
            })
        return jsonify({"available_cities": all_cities})

    except Exception as e:
        print(f"Error in search_cities: {str(e)}")
        return jsonify({"error": str(e)}), 500


def _normalise_price(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "").replace("₹", "")
    m = re.search(r"[\d.]+", s)
    return float(m.group()) if m else None


def _fmt_time(iso_str):
    # Keep ISO for frontend; helper exists to match prior implementation plan.
    return iso_str


def _normalise_flights(flights):
    out = []
    for f in flights or []:
        out.append({
            "airline": f.get("airline") or "Unknown Airline",
            "airlineCode": (f.get("airlineCode") or ""),
            "flightNumber": f.get("flightNumber") or "",
            "departureTime": _fmt_time(f.get("departureTime") or "N/A"),
            "arrivalTime": _fmt_time(f.get("arrivalTime") or "N/A"),
            "departureAirport": (f.get("departureAirport") or ""),
            "arrivalAirport": (f.get("arrivalAirport") or ""),
            "price": _normalise_price(f.get("price")) or 0,
            "currency": "INR",
            "duration": f.get("duration"),
            "stops": int(_normalise_price(f.get("stops")) or 0),
        })
    return out


def _normalise_hotels(hotels):
    out = []
    for h in hotels or []:
        out.append({
            "name": h.get("name") or "Hotel",
            "location": h.get("location") or "",
            "price": _normalise_price(h.get("price")) or 0,
            "currency": "INR",
            "rating": _normalise_price(h.get("rating")) or 4.0,
            "description": h.get("description") or "",
            "amenities": h.get("amenities") if isinstance(h.get("amenities"), list) else [],
            "isEstimate": bool(h.get("isEstimate")),
        })
    return out


@app.route('/get_min_prices', methods=['POST'])
@limiter.limit("30 per minute")  # Higher limit as this uses cache
def get_min_prices():
    try:
        destination = request.form.get('destination', '').strip()

        if not destination:
            return jsonify({"error": "Destination is required"}), 400

        dest_name = destination.split(",")[0].strip()

        print(f"Getting min hotel prices for {dest_name}")

        min_price = get_min_hotel_price(dest_name)

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
        
        flights, _src = tp_search_flights(
            origin=origin_code,
            destination=dest_code,
            departure_date=departure_date,
            return_date=return_date if return_date else None,
            adults=adults,
            travel_class=travel_class,
        )

        flights = _normalise_flights(flights)[:3]
        if flights:
            return jsonify(flights)
        
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
        budget = request.form.get('budget', '').strip()
        
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
        
        hotels, _src = tp_search_hotels(
            city_name=dest_base,
            check_in=check_in_date,
            check_out=check_out_date,
            adults=adults,
        )
        hotels = _normalise_hotels(hotels)[:3]

        # Budget logic: mark over-budget entries; still return them (UI warns).
        budget_val = None
        if budget:
            is_valid, err = validate_budget(budget)
            if is_valid:
                budget_val = float(budget)

        if budget_val is not None:
            for h in hotels:
                h["overBudget"] = bool((h.get("price") or 0) > budget_val)

        if hotels:
            return jsonify(hotels)

        # Absolute fallback: estimated city price if available.
        dest_lower = dest_base.lower()
        if dest_lower in ESTIMATED_HOTEL_PRICES:
            estimated_price = ESTIMATED_HOTEL_PRICES[dest_lower]
            return jsonify([{
                "name": f"Hotels in {dest_base}",
                "rating": 4.0,
                "price": float(estimated_price),
                "currency": "INR",
                "location": f"{dest_base} City Center",
                "description": f"Estimated average hotel price in {dest_base}. Actual prices may vary.",
                "amenities": ["WiFi", "Breakfast"],
                "isEstimate": True,
                "overBudget": bool(budget_val is not None and float(estimated_price) > budget_val),
            }])

        return jsonify([])
    
    except Exception as e:
        print(f"Error in search_hotels: {str(e)}")
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
    
    # Get relevant flights/hotel data using travel_api
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
            departure_date = start_date if start_date else datetime.now().strftime('%Y-%m-%d')
            
            flights, _src = tp_search_flights(
                origin=origin_codes[0],
                destination=dest_codes[0],
                departure_date=departure_date,
                adults=1,
                travel_class="ECONOMY",
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
            check_in = start_date if start_date else datetime.now().strftime('%Y-%m-%d')
            check_out = end_date if end_date else (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            
            hotels, _src = tp_search_hotels(
                city_name=destination,
                check_in=check_in,
                check_out=check_out,
                adults=1,
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

    # For other questions, use Gemini directly
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

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
                ai_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', ai_response)
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
                            ai_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', ai_response)
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

        results = {"flights": [], "hotels": [], "meta": {}}

        flight_source = None
        hotel_source = None

        if origin_code and dest_code and departure_date:
            flights, flight_source = tp_search_flights(
                origin=origin_code,
                destination=dest_code,
                departure_date=departure_date,
                return_date=return_date if return_date else None,
                adults=adults,
                travel_class=travel_class,
            )
            results["flights"] = _normalise_flights(flights)[:3]

        if destination:
            dest_base = destination.split(",")[0].strip()
            hotels, hotel_source = tp_search_hotels(
                city_name=dest_base,
                check_in=departure_date,
                check_out=return_date,
                adults=adults,
            )
            hotels = _normalise_hotels(hotels)[:3]
            # Budget hint for UI (overBudget flag)
            budget = request.form.get("budget", "").strip()
            budget_val = None
            if budget:
                is_valid, _err = validate_budget(budget)
                if is_valid:
                    budget_val = float(budget)
            if budget_val is not None:
                for h in hotels:
                    h["overBudget"] = bool((h.get("price") or 0) > budget_val)
            results["hotels"] = hotels

        results["meta"] = {
            "flightSource": flight_source,
            "hotelSource": hotel_source,
        }
        return jsonify(results)

    except Exception as e:
        print(f"Error in /search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "ok",
        "api_keys": {
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "secret": bool(os.getenv("SECRET_KEY")),
            "aviationstack": bool(os.getenv("AVIATIONSTACK_KEY")),
            "opentripmap": bool(os.getenv("OPENTRIPMAP_KEY")),
        },
        "cache": cache_health(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })


REQUIRED_ENV = ["GEMINI_API_KEY", "SECRET_KEY"]
missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
if missing:
    print(f"[BOOT][ERROR] Missing: {', '.join(missing)}", file=sys.stderr)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(429)
def rate_limited(e):
    return jsonify({"error": "Too many requests. Please slow down."}), 429


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
