"""
Pre-defined city data that works with Amadeus test API
"""

AVAILABLE_CITIES = {
    "New York": {
        "city_code": "NYC",
        "country": "United States",
        "airports": [
            {"name": "John F. Kennedy", "code": "JFK"},
            {"name": "LaGuardia", "code": "LGA"},
            {"name": "Newark", "code": "EWR"}
        ]
    },
    "London": {
        "city_code": "LON",
        "country": "United Kingdom",
        "airports": [
            {"name": "Heathrow", "code": "LHR"},
            {"name": "Gatwick", "code": "LGW"},
            {"name": "Stansted", "code": "STN"},
            {"name": "Luton", "code": "LTN"}
        ]
    },
    "Paris": {
        "city_code": "PAR",
        "country": "France",
        "airports": [
            {"name": "Charles de Gaulle", "code": "CDG"},
            {"name": "Orly", "code": "ORY"},
            {"name": "Beauvais Tille", "code": "BVA"}
        ]
    },
    "Tokyo": {
        "city_code": "TYO",
        "country": "Japan",
        "airports": [
            {"name": "Haneda", "code": "HND"},
            {"name": "Narita", "code": "NRT"}
        ]
    },
    "Sydney": {
        "city_code": "SYD",
        "country": "Australia",
        "airports": [
            {"name": "Kingsford Smith", "code": "SYD"}
        ]
    },
    "Dubai": {
        "city_code": "DXB",
        "country": "United Arab Emirates",
        "airports": [
            {"name": "Dubai International", "code": "DXB"},
            {"name": "Al Maktoum", "code": "DWC"}
        ]
    },
    "Singapore": {
        "city_code": "SIN",
        "country": "Singapore",
        "airports": [
            {"name": "Changi", "code": "SIN"}
        ]
    },
    "San Francisco": {
        "city_code": "SFO",
        "country": "United States",
        "airports": [
            {"name": "San Francisco International", "code": "SFO"},
            {"name": "Oakland", "code": "OAK"}
        ]
    },
    "Mumbai": {
        "city_code": "BOM",
        "country": "India",
        "airports": [
            {"name": "Chhatrapati Shivaji", "code": "BOM"}
        ]
    },
    "Delhi": {
        "city_code": "DEL",
        "country": "India",
        "airports": [
            {"name": "Indira Gandhi", "code": "DEL"}
        ]
    }
}

def get_city_info(city_name):
    """Get city information from the predefined list"""
    # Handle cases where the city name includes country or airports
    if " - " in city_name:
        city_name = city_name.split(" - ")[0]  # Get the part before any dashes
    if "," in city_name:
        city_name = city_name.split(",")[0]  # Get the part before any commas
    
    # Remove any surrounding whitespace and convert to title case
    city_name = city_name.strip().title()
    print(f"Looking up city info for: {city_name}")
    
    # Try to find the city in our database
    city_info = AVAILABLE_CITIES.get(city_name)
    if city_info:
        print(f"Found city info: {city_info}")
    else:
        print(f"No city info found for: {city_name}")
    return city_info

def get_available_cities():
    """Get list of all available cities"""
    return list(AVAILABLE_CITIES.keys())

def get_airport_codes(city_name):
    """Get list of airport codes for a city"""
    city = AVAILABLE_CITIES.get(city_name.title())
    if city:
        return [airport["code"] for airport in city["airports"]]
    return []

def format_city_info(city_name):
    """Format city information for display"""
    city = get_city_info(city_name)  # Use get_city_info to handle various formats
    if city:
        return f"{city_name.title()}, {city['country']}"  # Simpler format for UI display
    return None
