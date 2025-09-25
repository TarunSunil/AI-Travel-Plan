import sqlite3
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection using SQLite"""
    db_path = os.path.join(os.path.dirname(__file__), 'travel_planner.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = None
    try:
        print("Initializing database...")
        conn = get_db_connection()
        cursor = conn.cursor()

        # Drop existing tables if they exist
        cursor.execute('DROP TABLE IF EXISTS flights')
        cursor.execute('DROP TABLE IF EXISTS hotels')
        cursor.execute('DROP TABLE IF EXISTS min_prices')
        cursor.execute('DROP TABLE IF EXISTS api_cache')

        print("Old tables dropped successfully")

        # Create new tables with all required fields
        cursor.execute('''
            CREATE TABLE flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                price REAL NOT NULL,
                date DATE NOT NULL,
                airline TEXT NOT NULL
            )
        ''')
        print("Created flights table")

        cursor.execute('''
            CREATE TABLE hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                price_per_night REAL NOT NULL,
                rating REAL NOT NULL
            )
        ''')
        print("Created hotels table")

        cursor.execute('''
            CREATE TABLE min_prices (
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                min_flight_price REAL NOT NULL,
                min_hotel_price REAL NOT NULL,
                PRIMARY KEY (origin, destination)
            )
        ''')
        print("Created min_prices table")

        cursor.execute('''
            CREATE TABLE api_cache (
                route_key TEXT NOT NULL,
                data_type TEXT NOT NULL,
                response_data TEXT NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                PRIMARY KEY (route_key, data_type)
            )
        ''')
        print("Created api_cache table")

        conn.commit()
        print("Database initialized successfully")
        return conn
    except sqlite3.Error as e:
        print(f"Database error during initialization: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        print(f"Error during database initialization: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

    # Create tables
    cursor.execute('''
        CREATE TABLE flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            price REAL NOT NULL,
            date DATE NOT NULL,
            airline TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            price_per_night REAL NOT NULL,
            rating REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE min_prices (
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            min_flight_price REAL NOT NULL,
            min_hotel_price REAL NOT NULL,
            PRIMARY KEY (origin, destination)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE api_cache (
            route_key TEXT NOT NULL,
            data_type TEXT NOT NULL,
            response_data TEXT NOT NULL,
            last_updated TIMESTAMP NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            PRIMARY KEY (route_key, data_type)
        )
    ''')

    conn.commit()
    return conn

def populate_sample_data(conn):
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM flights')
    cursor.execute('DELETE FROM hotels')
    cursor.execute('DELETE FROM min_prices')
    
    # Get current date for more relevant flight dates
    today = datetime.datetime.now()
    
    # Insert expanded flights data with future dates
    flights_data = [
        # New York routes
        ("New York", "Paris", 450, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Air France"),
        ("New York", "London", 400, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "British Airways"),
        ("New York", "Tokyo", 850, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Japan Airlines"),
        ("New York", "Sydney", 950, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Qantas"),
        ("New York", "Dubai", 750, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Emirates"),
        ("New York", "Singapore", 900, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("New York", "San Francisco", 350, (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "United Airlines"),
        ("New York", "Mumbai", 950, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Air India"),
        ("New York", "Delhi", 920, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Emirates"),
        
        # London routes
        ("London", "Paris", 120, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "EasyJet"),
        ("London", "New York", 420, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "British Airways"),
        ("London", "Tokyo", 780, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Japan Airlines"),
        ("London", "Dubai", 380, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "Emirates"),
        ("London", "Singapore", 650, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("London", "San Francisco", 580, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "British Airways"),
        ("London", "Sydney", 980, (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d"), "Qantas"),
        ("London", "Mumbai", 650, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "British Airways"),
        ("London", "Delhi", 640, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "British Airways"),
        
        # Paris routes
        ("Paris", "New York", 460, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Air France"),
        ("Paris", "London", 130, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Air France"),
        ("Paris", "Tokyo", 800, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Air France"),
        ("Paris", "Dubai", 420, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Emirates"),
        ("Paris", "Singapore", 750, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Paris", "San Francisco", 620, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Air France"),
        ("Paris", "Mumbai", 700, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Air France"),
        ("Paris", "Delhi", 680, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Air France"),
        
        # Tokyo routes
        ("Tokyo", "New York", 870, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Japan Airlines"),
        ("Tokyo", "London", 790, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "British Airways"),
        ("Tokyo", "Singapore", 450, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Tokyo", "Paris", 820, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Air France"),
        ("Tokyo", "Dubai", 680, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Emirates"),
        ("Tokyo", "San Francisco", 750, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Japan Airlines"),
        ("Tokyo", "Mumbai", 720, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Japan Airlines"),
        ("Tokyo", "Delhi", 700, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Japan Airlines"),
        
        # San Francisco routes
        ("San Francisco", "New York", 360, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "United Airlines"),
        ("San Francisco", "London", 590, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "British Airways"),
        ("San Francisco", "Tokyo", 760, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Japan Airlines"),
        ("San Francisco", "Paris", 630, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Air France"),
        ("San Francisco", "Dubai", 890, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Emirates"),
        ("San Francisco", "Singapore", 850, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("San Francisco", "Mumbai", 920, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "United Airlines"),
        ("San Francisco", "Delhi", 900, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "United Airlines"),
        
        # Sydney routes
        ("Sydney", "New York", 970, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Qantas"),
        ("Sydney", "London", 990, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "British Airways"),
        ("Sydney", "Singapore", 550, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Sydney", "Dubai", 780, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Emirates"),
        ("Sydney", "Mumbai", 820, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Qantas"),
        ("Sydney", "Delhi", 800, (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d"), "Qantas"),
        
        # Dubai routes
        ("Dubai", "New York", 760, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Emirates"),
        ("Dubai", "London", 390, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Emirates"),
        ("Dubai", "Paris", 430, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Emirates"),
        ("Dubai", "Tokyo", 690, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Emirates"),
        ("Dubai", "Singapore", 480, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Emirates"),
        ("Dubai", "Sydney", 790, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Emirates"),
        ("Dubai", "San Francisco", 880, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Emirates"),
        ("Dubai", "Mumbai", 320, (today + datetime.timedelta(days=6)).strftime("%Y-%m-%d"), "Emirates"),
        ("Dubai", "Delhi", 310, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Emirates"),
        
        # Singapore routes
        ("Singapore", "New York", 910, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Singapore", "London", 660, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Singapore", "Tokyo", 460, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Singapore", "Paris", 760, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Singapore", "Dubai", 490, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Singapore", "Sydney", 560, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Singapore", "San Francisco", 860, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Singapore", "Mumbai", 420, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Singapore", "Delhi", 430, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        
        # Mumbai routes
        ("Mumbai", "New York", 960, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Air India"),
        ("Mumbai", "London", 650, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "British Airways"),
        ("Mumbai", "Dubai", 320, (today + datetime.timedelta(days=6)).strftime("%Y-%m-%d"), "Emirates"),
        ("Mumbai", "Singapore", 420, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Mumbai", "Paris", 700, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Air India"),
        ("Mumbai", "Tokyo", 720, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Air India"),
        ("Mumbai", "San Francisco", 920, (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d"), "Air India"),
        ("Mumbai", "Sydney", 820, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Air India"),
        ("Mumbai", "Delhi", 120, (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "Air India"),
        
        # Delhi routes
        ("Delhi", "New York", 930, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Air India"),
        ("Delhi", "London", 640, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "British Airways"),
        ("Delhi", "Dubai", 310, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Emirates"),
        ("Delhi", "Singapore", 430, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        ("Delhi", "Paris", 670, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Air India"),
        ("Delhi", "Tokyo", 700, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "Air India"),
        ("Delhi", "San Francisco", 900, (today + datetime.timedelta(days=16)).strftime("%Y-%m-%d"), "Air India"),
        ("Delhi", "Sydney", 800, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Air India"),
        ("Delhi", "Mumbai", 120, (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "Air India")
    ]
    
    cursor.executemany('INSERT INTO flights (origin, destination, price, date, airline) VALUES (?, ?, ?, ?, ?)', 
                      flights_data)
    
    # Insert expanded hotels data
    hotels_data = [
        # Paris hotels
        ("Grand Plaza Paris", "Paris", 200, 4.5),
        ("Ritz Paris", "Paris", 500, 4.9),
        ("Le Bristol", "Paris", 450, 4.8),
        ("Hotel de Crillon", "Paris", 550, 4.9),
        ("Shangri-La Paris", "Paris", 480, 4.7),
        
        # London hotels
        ("The Savoy", "London", 450, 4.8),
        ("Royal Court Hotel", "London", 180, 4.3),
        ("The Ritz London", "London", 500, 4.9),
        ("Claridge's", "London", 520, 4.9),
        ("The Dorchester", "London", 480, 4.8),
        
        # New York hotels
        ("The Plaza", "New York", 400, 4.7),
        ("Empire State Hotel", "New York", 250, 4.6),
        ("St. Regis New York", "New York", 500, 4.8),
        ("Four Seasons New York", "New York", 550, 4.9),
        ("The Peninsula New York", "New York", 520, 4.8),
        
        # Tokyo hotels
        ("Park Hyatt Tokyo", "Tokyo", 400, 4.8),
        ("Mandarin Oriental", "Tokyo", 450, 4.9),
        ("The Peninsula", "Tokyo", 500, 4.9),
        ("Aman Tokyo", "Tokyo", 600, 5.0),
        ("Hoshinoya Tokyo", "Tokyo", 550, 4.8),
        
        # Dubai hotels
        ("Burj Al Arab", "Dubai", 1000, 5.0),
        ("Atlantis The Palm", "Dubai", 500, 4.8),
        ("Emirates Palace", "Dubai", 600, 4.9),
        ("One&Only Royal Mirage", "Dubai", 450, 4.7),
        ("Jumeirah Beach Hotel", "Dubai", 380, 4.6),
        
        # Singapore hotels
        ("Marina Bay Sands", "Singapore", 450, 4.8),
        ("Raffles Singapore", "Singapore", 400, 4.9),
        ("The Fullerton", "Singapore", 350, 4.7),
        ("Capella Singapore", "Singapore", 500, 4.9),
        ("Shangri-La Singapore", "Singapore", 380, 4.7),
        
        # San Francisco hotels
        ("Fairmont San Francisco", "San Francisco", 380, 4.7),
        ("The Ritz-Carlton", "San Francisco", 450, 4.8),
        ("Palace Hotel", "San Francisco", 320, 4.6),
        ("Four Seasons San Francisco", "San Francisco", 420, 4.7),
        ("St. Regis San Francisco", "San Francisco", 400, 4.7),
        
        # Sydney hotels
        ("Park Hyatt Sydney", "Sydney", 550, 4.9),
        ("Four Seasons Sydney", "Sydney", 450, 4.8),
        ("The Langham Sydney", "Sydney", 420, 4.7),
        ("Shangri-La Sydney", "Sydney", 380, 4.6),
        ("InterContinental Sydney", "Sydney", 350, 4.5),
        
        # Mumbai hotels
        ("The Taj Mahal Palace", "Mumbai", 350, 4.8),
        ("The Oberoi Mumbai", "Mumbai", 320, 4.7),
        ("Four Seasons Mumbai", "Mumbai", 280, 4.6),
        ("The Leela Mumbai", "Mumbai", 250, 4.5),
        
        # Delhi hotels
        ("The Oberoi New Delhi", "Delhi", 340, 4.8),
        ("The Leela Palace Delhi", "Delhi", 310, 4.7),
        ("Taj Palace Delhi", "Delhi", 290, 4.6),
        ("The Imperial New Delhi", "Delhi", 270, 4.5)
    ]
    
    cursor.executemany('INSERT INTO hotels (name, location, price_per_night, rating) VALUES (?, ?, ?, ?)',
                      hotels_data)
    
    # Insert expanded minimum prices
    min_prices_data = [
        # New York routes
        ("New York", "Paris", 450, 180),
        ("New York", "London", 400, 160),
        ("New York", "Tokyo", 850, 350),
        ("New York", "Dubai", 750, 450),
        ("New York", "Singapore", 900, 300),
        ("New York", "San Francisco", 350, 300),
        ("New York", "Sydney", 950, 350),
        ("New York", "Mumbai", 950, 250),
        ("New York", "Delhi", 920, 270),
        
        # London routes
        ("London", "Paris", 120, 150),
        ("London", "New York", 420, 200),
        ("London", "Tokyo", 780, 350),
        ("London", "Dubai", 380, 450),
        ("London", "Singapore", 650, 300),
        ("London", "San Francisco", 580, 300),
        ("London", "Sydney", 980, 350),
        ("London", "Mumbai", 650, 250),
        ("London", "Delhi", 640, 270),
        
        # Paris routes
        ("Paris", "New York", 460, 200),
        ("Paris", "London", 130, 160),
        ("Paris", "Tokyo", 800, 350),
        ("Paris", "Dubai", 420, 380),
        ("Paris", "Singapore", 750, 300),
        ("Paris", "San Francisco", 620, 300),
        ("Paris", "Mumbai", 700, 250),
        ("Paris", "Delhi", 680, 270),
        
        # Tokyo routes
        ("Tokyo", "New York", 870, 200),
        ("Tokyo", "London", 790, 160),
        ("Tokyo", "Singapore", 450, 300),
        ("Tokyo", "Paris", 820, 180),
        ("Tokyo", "Dubai", 680, 380),
        ("Tokyo", "San Francisco", 750, 300),
        ("Tokyo", "Mumbai", 720, 250),
        ("Tokyo", "Delhi", 700, 270),
        
        # San Francisco routes
        ("San Francisco", "New York", 360, 200),
        ("San Francisco", "London", 590, 160),
        ("San Francisco", "Tokyo", 760, 350),
        ("San Francisco", "Paris", 630, 180),
        ("San Francisco", "Dubai", 890, 380),
        ("San Francisco", "Singapore", 850, 300),
        ("San Francisco", "Mumbai", 920, 250),
        ("San Francisco", "Delhi", 900, 270),
        
        # Sydney routes
        ("Sydney", "New York", 970, 200),
        ("Sydney", "London", 990, 160),
        ("Sydney", "Singapore", 550, 300),
        ("Sydney", "Dubai", 780, 380),
        ("Sydney", "Mumbai", 820, 250),
        ("Sydney", "Delhi", 800, 270),
        
        # Dubai routes
        ("Dubai", "New York", 760, 200),
        ("Dubai", "London", 390, 160),
        ("Dubai", "Paris", 430, 180),
        ("Dubai", "Tokyo", 690, 350),
        ("Dubai", "Singapore", 480, 300),
        ("Dubai", "Sydney", 790, 350),
        ("Dubai", "San Francisco", 880, 300),
        ("Dubai", "Mumbai", 320, 250),
        ("Dubai", "Delhi", 310, 270),
        
        # Singapore routes
        ("Singapore", "New York", 910, 200),
        ("Singapore", "London", 660, 160),
        ("Singapore", "Tokyo", 460, 350),
        ("Singapore", "Paris", 760, 180),
        ("Singapore", "Dubai", 490, 380),
        ("Singapore", "Sydney", 560, 350),
        ("Singapore", "San Francisco", 860, 300),
        ("Singapore", "Mumbai", 420, 250),
        ("Singapore", "Delhi", 430, 270),
        
        # Mumbai routes
        ("Mumbai", "New York", 960, 200),
        ("Mumbai", "London", 650, 160),
        ("Mumbai", "Dubai", 320, 380),
        ("Mumbai", "Singapore", 420, 300),
        ("Mumbai", "Paris", 700, 180),
        ("Mumbai", "Tokyo", 720, 350),
        ("Mumbai", "San Francisco", 920, 300),
        ("Mumbai", "Sydney", 820, 350),
        ("Mumbai", "Delhi", 120, 270),
        
        # Delhi routes
        ("Delhi", "New York", 930, 200),
        ("Delhi", "London", 640, 160),
        ("Delhi", "Dubai", 310, 380),
        ("Delhi", "Singapore", 430, 300),
        ("Delhi", "Paris", 670, 180),
        ("Delhi", "Tokyo", 700, 350),
        ("Delhi", "San Francisco", 900, 300),
        ("Delhi", "Sydney", 800, 350),
        ("Delhi", "Mumbai", 120, 250)
    ]
    
    cursor.executemany('INSERT INTO min_prices (origin, destination, min_flight_price, min_hotel_price) VALUES (?, ?, ?, ?)',
                      min_prices_data)
    
    conn.commit()

if __name__ == '__main__':
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Initialize database tables
        cursor.execute('DROP TABLE IF EXISTS flights')
        cursor.execute('DROP TABLE IF EXISTS hotels')
        cursor.execute('DROP TABLE IF EXISTS min_prices')
        cursor.execute('DROP TABLE IF EXISTS api_cache')
        
        print("Old tables dropped successfully")
        
        # Create new tables with all required fields
        cursor.execute('''
            CREATE TABLE flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                price REAL NOT NULL,
                date DATE NOT NULL,
                airline TEXT NOT NULL
            )
        ''')
        print("Created flights table")

        cursor.execute('''
            CREATE TABLE hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                price_per_night REAL NOT NULL,
                rating REAL NOT NULL
            )
        ''')
        print("Created hotels table")

        cursor.execute('''
            CREATE TABLE min_prices (
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                min_flight_price REAL NOT NULL,
                min_hotel_price REAL NOT NULL,
                PRIMARY KEY (origin, destination)
            )
        ''')
        print("Created min_prices table")

        cursor.execute('''
            CREATE TABLE api_cache (
                route_key TEXT NOT NULL,
                data_type TEXT NOT NULL,
                response_data TEXT NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                PRIMARY KEY (route_key, data_type)
            )
        ''')
        print("Created api_cache table")
        
        # Populate with sample data
        populate_sample_data(conn)
        
        conn.commit()
        print("Database initialized and populated successfully")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()