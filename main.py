from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'travel_planner.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/get_min_prices', methods=['POST'])
def get_min_prices():
    start_point = request.form['startPoint']
    destination = request.form['destination']
    
    conn = get_db()
    cursor = conn.cursor()
    
    result = cursor.execute('''
        SELECT min_flight_price, min_hotel_price 
        FROM min_prices 
        WHERE origin = ? AND destination = ?
    ''', (start_point, destination)).fetchone()
    
    conn.close()
    
    if result:
        return jsonify({
            "minFlightPrice": result['min_flight_price'],
            "minHotelPrice": result['min_hotel_price']
        })
    return jsonify({"error": "Invalid location combination"})

@app.route('/search_flights', methods=['POST'])
def search_flights():
    try:
        start_point = request.form['startPoint']
        destination = request.form['destination']
        start_date = request.form.get('startDate', '')
        
        # Add default response for unavailable routes
        default_flights = {
            'Dubai': [
                {'airline': 'Emirates', 'origin': start_point, 'destination': 'Dubai', 'price': 800, 'date': start_date or '2024-02-01'},
                {'airline': 'Etihad Airways', 'origin': start_point, 'destination': 'Dubai', 'price': 850, 'date': start_date or '2024-02-02'}
            ],
            'Singapore': [
                {'airline': 'Singapore Airlines', 'origin': start_point, 'destination': 'Singapore', 'price': 900, 'date': start_date or '2024-02-01'},
                {'airline': 'Qatar Airways', 'origin': start_point, 'destination': 'Singapore', 'price': 950, 'date': start_date or '2024-02-02'}
            ]
        }
        
        conn = get_db()
        cursor = conn.cursor()
        
        flights = cursor.execute('''
            SELECT * FROM flights 
            WHERE origin = ? AND destination = ?
        ''', (start_point, destination)).fetchall()
        
        conn.close()
        
        flight_list = []
        if not flights and destination in default_flights:
            flight_list = default_flights[destination]
        else:
            for flight in flights:
                flight_dict = dict(flight)
                if start_date:
                    flight_dict['display_date'] = start_date
                flight_list.append(flight_dict)
        
        return jsonify(flight_list)
    except Exception as e:
        print(f"Error in search_flights: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/search_hotels', methods=['POST'])
def search_hotels():
    try:
        destination = request.form['destination']
        try:
            budget = int(request.form['budget'])
        except (ValueError, TypeError):
            budget = 1000
        
        # Add default hotels for destinations not in database
        default_hotels = {
            'Dubai': [
                {'name': 'Burj Al Arab', 'location': 'Dubai', 'price_per_night': 900, 'rating': 5.0},
                {'name': 'Atlantis The Palm', 'location': 'Dubai', 'price_per_night': 500, 'rating': 4.8},
                {'name': 'Address Downtown', 'location': 'Dubai', 'price_per_night': 400, 'rating': 4.7}
            ],
            'Singapore': [
                {'name': 'Marina Bay Sands', 'location': 'Singapore', 'price_per_night': 550, 'rating': 4.8},
                {'name': 'Raffles Hotel', 'location': 'Singapore', 'price_per_night': 450, 'rating': 4.9},
                {'name': 'Fullerton Bay Hotel', 'location': 'Singapore', 'price_per_night': 380, 'rating': 4.7}
            ]
        }
        
        conn = get_db()
        cursor = conn.cursor()
        
        hotels = cursor.execute('''
            SELECT * FROM hotels 
            WHERE location = ? AND price_per_night <= ?
        ''', (destination, budget)).fetchall()
        
        conn.close()
        
        hotel_list = []
        if not hotels and destination in default_hotels:
            # Filter default hotels based on budget
            hotel_list = [hotel for hotel in default_hotels[destination] if hotel['price_per_night'] <= budget]
        else:
            hotel_list = [dict(hotel) for hotel in hotels]
        
        return jsonify(hotel_list)
    except Exception as e:
        print(f"Error in search_hotels: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.form['message']
    destination = request.form.get('destination', '').strip()
    start_date = request.form.get('startDate', '')
    end_date = request.form.get('endDate', '')

    if not GEMINI_API_KEY:
        return jsonify({"response": "API key is missing. Please check your configuration."})

    # Check if the question is about flights or hotels
    message_lower = user_message.lower()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get relevant flights and hotels data from database
    if any(word in message_lower for word in ['flight', 'airline', 'fly', 'flying', 'airport']):
        flights = cursor.execute('''
            SELECT * FROM flights 
            WHERE destination = ?
        ''', (destination,)).fetchall()
        
        if not flights:
            conn.close()
            return jsonify({"response": f"I don't have any flight information available for {destination} at the moment."})
        
        # Format flight information
        response = f"Here are the available flights to {destination}:<br><br>"
        for flight in flights:
            response += f"• {flight['airline']}: ${flight['price']} on {flight['date']}<br>"
        conn.close()
        return jsonify({"response": response})
    
    # If question is about hotels
    elif any(word in message_lower for word in ['hotel', 'accommodation', 'stay', 'lodging', 'room']):
        hotels = cursor.execute('''
            SELECT * FROM hotels 
            WHERE location = ?
        ''', (destination,)).fetchall()
        
        if not hotels:
            conn.close()
            return jsonify({"response": f"I don't have any hotel information available for {destination} at the moment."})
        
        # Format hotel information
        response = f"Here are the available hotels in {destination}:<br><br>"
        for hotel in hotels:
            response += f"• {hotel['name']}: ${hotel['price_per_night']}/night, Rating: {hotel['rating']}/5<br>"
        conn.close()
        return jsonify({"response": response})

    conn.close()
    # For other questions, use the Gemini API
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    # Add date context to the prompt if dates are provided
    date_context = ""
    if start_date and end_date:
        date_context = f"\nThe user is planning to visit from {start_date} to {end_date}. Please consider this date range when providing travel advice, especially for seasonal activities, weather, and events."

    data = {
        "contents": [{
            "parts": [{
                "text": f"""You are a helpful travel assistant. The user's question is: {user_message}
The destination is: {destination}{date_context}

Please provide a helpful response about travel, destinations, or tourism in general. If the user mentions a specific destination, focus on that destination. If not, provide general travel advice.

Please format your response in a clean, readable way:
1. Use proper spacing between paragraphs
2. Use bullet points for lists
3. Keep paragraphs short and focused
4. Use bold text sparingly for important points
5. Avoid excessive formatting or special characters
6. Make the response concise and easy to read
7. If providing an itinerary, make sure to complete all days and include a conclusion"""
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
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        
        if response.status_code == 200:
            response_data = response.json()
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
                # Clean up the response formatting
                ai_response = ai_response.replace('**', '')
                ai_response = ai_response.replace('*', '•')
                ai_response = ai_response.replace('\n\n', '<br><br>')
                ai_response = ai_response.replace('\n', '<br>')
                
                # If the response seems incomplete (ends with a bullet point or mid-sentence)
                if ai_response.strip().endswith('•') or ai_response.strip().endswith(','):
                    # Make another request to complete the response
                    data['contents'][0]['parts'][0]['text'] = f"Complete this response: {ai_response}"
                    response = requests.post(api_url, headers=headers, json=data)
                    response_data = response.json()
                    if 'candidates' in response_data and len(response_data['candidates']) > 0:
                        completion = response_data['candidates'][0]['content']['parts'][0]['text']
                        ai_response += completion
            else:
                print(f"Unexpected API response format: {response_data}")
                ai_response = "I couldn't generate a response. Please try again."
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            ai_response = "Sorry, I encountered an error. Please try again."
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")
        ai_response = "Sorry, I encountered an error. Please try again."
    except Exception as e:
        print(f"General Error: {str(e)}")
        ai_response = "Sorry, I encountered an error. Please try again."

    return jsonify({"response": ai_response})


if __name__ == '__main__':
    app.run(debug=True)
