import sqlite3
import os
import datetime

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), 'travel_planner.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Drop existing tables if they exist
    c.execute('DROP TABLE IF EXISTS flights')
    c.execute('DROP TABLE IF EXISTS hotels')
    c.execute('DROP TABLE IF EXISTS min_prices')

    # Create tables
    c.execute('''
        CREATE TABLE flights (
            id INTEGER PRIMARY KEY,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL,
            airline TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE hotels (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            price_per_night REAL NOT NULL,
            rating REAL NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE min_prices (
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            min_flight_price REAL NOT NULL,
            min_hotel_price REAL NOT NULL,
            PRIMARY KEY (origin, destination)
        )
    ''')

    conn.commit()
    return conn

def populate_sample_data(conn):
    c = conn.cursor()
    
    # Clear existing data
    c.execute('DELETE FROM flights')
    c.execute('DELETE FROM hotels')
    c.execute('DELETE FROM min_prices')
    
    # Get current date for more relevant flight dates
    today = datetime.datetime.now()
    
    # Insert expanded flights data with future dates
    flights_data = [
        # New York routes
        (1, "New York", "Paris", 450, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Air France"),
        (2, "New York", "London", 400, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "British Airways"),
        (3, "New York", "Tokyo", 850, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Japan Airlines"),
        (4, "New York", "Sydney", 950, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Qantas"),
        (5, "New York", "Dubai", 750, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Emirates"),
        (6, "New York", "Singapore", 900, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (7, "New York", "San Francisco", 350, (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "United Airlines"),
        (8, "New York", "Mumbai", 950, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Air India"),
        (9, "New York", "Delhi", 920, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Emirates"),
        
        # London routes
        (10, "London", "Paris", 120, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "EasyJet"),
        (11, "London", "New York", 420, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "British Airways"),
        (12, "London", "Tokyo", 780, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Japan Airlines"),
        (13, "London", "Dubai", 380, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "Emirates"),
        (14, "London", "Singapore", 650, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (15, "London", "San Francisco", 580, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "British Airways"),
        (16, "London", "Sydney", 980, (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d"), "Qantas"),
        (17, "London", "Mumbai", 650, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "British Airways"),
        (18, "London", "Delhi", 640, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "British Airways"),
        
        # Paris routes
        (19, "Paris", "New York", 460, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Air France"),
        (20, "Paris", "London", 130, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Air France"),
        (21, "Paris", "Tokyo", 800, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Air France"),
        (22, "Paris", "Dubai", 420, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Emirates"),
        (23, "Paris", "Singapore", 750, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (24, "Paris", "San Francisco", 620, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Air France"),
        (25, "Paris", "Mumbai", 700, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Air France"),
        (26, "Paris", "Delhi", 680, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Air France"),
        
        # Tokyo routes
        (27, "Tokyo", "New York", 870, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Japan Airlines"),
        (28, "Tokyo", "London", 790, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "British Airways"),
        (29, "Tokyo", "Singapore", 450, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (30, "Tokyo", "Paris", 820, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Air France"),
        (31, "Tokyo", "Dubai", 680, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Emirates"),
        (32, "Tokyo", "San Francisco", 750, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Japan Airlines"),
        (33, "Tokyo", "Mumbai", 720, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Japan Airlines"),
        (34, "Tokyo", "Delhi", 700, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Japan Airlines"),
        
        # San Francisco routes
        (35, "San Francisco", "New York", 360, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "United Airlines"),
        (36, "San Francisco", "London", 590, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "British Airways"),
        (37, "San Francisco", "Tokyo", 760, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Japan Airlines"),
        (38, "San Francisco", "Paris", 630, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Air France"),
        (39, "San Francisco", "Dubai", 890, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Emirates"),
        (40, "San Francisco", "Singapore", 850, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (41, "San Francisco", "Mumbai", 920, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "United Airlines"),
        (42, "San Francisco", "Delhi", 900, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "United Airlines"),
        
        # Sydney routes
        (43, "Sydney", "New York", 970, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Qantas"),
        (44, "Sydney", "London", 990, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "British Airways"),
        (45, "Sydney", "Singapore", 550, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (46, "Sydney", "Dubai", 780, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Emirates"),
        (47, "Sydney", "Mumbai", 820, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Qantas"),
        (48, "Sydney", "Delhi", 800, (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d"), "Qantas"),
        
        # Dubai routes
        (49, "Dubai", "New York", 760, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Emirates"),
        (50, "Dubai", "London", 390, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Emirates"),
        (51, "Dubai", "Paris", 430, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Emirates"),
        (52, "Dubai", "Tokyo", 690, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Emirates"),
        (53, "Dubai", "Singapore", 480, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Emirates"),
        (54, "Dubai", "Sydney", 790, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Emirates"),
        (55, "Dubai", "San Francisco", 880, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Emirates"),
        (56, "Dubai", "Mumbai", 320, (today + datetime.timedelta(days=6)).strftime("%Y-%m-%d"), "Emirates"),
        (57, "Dubai", "Delhi", 310, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Emirates"),
        
        # Singapore routes
        (58, "Singapore", "New York", 910, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (59, "Singapore", "London", 660, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (60, "Singapore", "Tokyo", 460, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (61, "Singapore", "Paris", 760, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (62, "Singapore", "Dubai", 490, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (63, "Singapore", "Sydney", 560, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (64, "Singapore", "San Francisco", 860, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (65, "Singapore", "Mumbai", 420, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (66, "Singapore", "Delhi", 430, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        
        # Mumbai routes
        (67, "Mumbai", "New York", 960, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Air India"),
        (68, "Mumbai", "London", 650, (today + datetime.timedelta(days=8)).strftime("%Y-%m-%d"), "British Airways"),
        (69, "Mumbai", "Dubai", 320, (today + datetime.timedelta(days=6)).strftime("%Y-%m-%d"), "Emirates"),
        (70, "Mumbai", "Singapore", 420, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (71, "Mumbai", "Paris", 700, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Air India"),
        (72, "Mumbai", "Tokyo", 720, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Air India"),
        (73, "Mumbai", "San Francisco", 920, (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d"), "Air India"),
        (74, "Mumbai", "Sydney", 820, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Air India"),
        (75, "Mumbai", "Delhi", 120, (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "Air India"),
        
        # Delhi routes
        (76, "Delhi", "New York", 930, (today + datetime.timedelta(days=11)).strftime("%Y-%m-%d"), "Air India"),
        (77, "Delhi", "London", 640, (today + datetime.timedelta(days=9)).strftime("%Y-%m-%d"), "British Airways"),
        (78, "Delhi", "Dubai", 310, (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Emirates"),
        (79, "Delhi", "Singapore", 430, (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Singapore Airlines"),
        (80, "Delhi", "Paris", 670, (today + datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "Air India"),
        (81, "Delhi", "Tokyo", 700, (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "Air India"),
        (82, "Delhi", "San Francisco", 900, (today + datetime.timedelta(days=16)).strftime("%Y-%m-%d"), "Air India"),
        (83, "Delhi", "Sydney", 800, (today + datetime.timedelta(days=13)).strftime("%Y-%m-%d"), "Air India"),
        (84, "Delhi", "Mumbai", 120, (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "Air India")
    ]
    
    c.executemany('INSERT INTO flights (id, origin, destination, price, date, airline) VALUES (?, ?, ?, ?, ?, ?)', 
                  flights_data)
    
    # Insert expanded hotels data
    hotels_data = [
        # Paris hotels
        (1, "Grand Plaza Paris", "Paris", 200, 4.5),
        (2, "Ritz Paris", "Paris", 500, 4.9),
        (3, "Le Bristol", "Paris", 450, 4.8),
        (4, "Hotel de Crillon", "Paris", 550, 4.9),
        (5, "Shangri-La Paris", "Paris", 480, 4.7),
        
        # London hotels
        (6, "The Savoy", "London", 450, 4.8),
        (7, "Royal Court Hotel", "London", 180, 4.3),
        (8, "The Ritz London", "London", 500, 4.9),
        (9, "Claridge's", "London", 520, 4.9),
        (10, "The Dorchester", "London", 480, 4.8),
        
        # New York hotels
        (11, "The Plaza", "New York", 400, 4.7),
        (12, "Empire State Hotel", "New York", 250, 4.6),
        (13, "St. Regis New York", "New York", 500, 4.8),
        (14, "Four Seasons New York", "New York", 550, 4.9),
        (15, "The Peninsula New York", "New York", 520, 4.8),
        
        # Tokyo hotels
        (16, "Park Hyatt Tokyo", "Tokyo", 400, 4.8),
        (17, "Mandarin Oriental", "Tokyo", 450, 4.9),
        (18, "The Peninsula", "Tokyo", 500, 4.9),
        (19, "Aman Tokyo", "Tokyo", 600, 5.0),
        (20, "Hoshinoya Tokyo", "Tokyo", 550, 4.8),
        
        # Dubai hotels
        (21, "Burj Al Arab", "Dubai", 1000, 5.0),
        (22, "Atlantis The Palm", "Dubai", 500, 4.8),
        (23, "Emirates Palace", "Dubai", 600, 4.9),
        (24, "One&Only Royal Mirage", "Dubai", 450, 4.7),
        (25, "Jumeirah Beach Hotel", "Dubai", 380, 4.6),
        
        # Singapore hotels
        (26, "Marina Bay Sands", "Singapore", 450, 4.8),
        (27, "Raffles Singapore", "Singapore", 400, 4.9),
        (28, "The Fullerton", "Singapore", 350, 4.7),
        (29, "Capella Singapore", "Singapore", 500, 4.9),
        (30, "Shangri-La Singapore", "Singapore", 380, 4.7),
        
        # San Francisco hotels
        (31, "Fairmont San Francisco", "San Francisco", 380, 4.7),
        (32, "The Ritz-Carlton", "San Francisco", 450, 4.8),
        (33, "Palace Hotel", "San Francisco", 320, 4.6),
        (34, "Four Seasons San Francisco", "San Francisco", 420, 4.7),
        (35, "St. Regis San Francisco", "San Francisco", 400, 4.7),
        
        # Sydney hotels
        (36, "Park Hyatt Sydney", "Sydney", 550, 4.9),
        (37, "Four Seasons Sydney", "Sydney", 450, 4.8),
        (38, "The Langham Sydney", "Sydney", 420, 4.7),
        (39, "Shangri-La Sydney", "Sydney", 380, 4.6),
        (40, "InterContinental Sydney", "Sydney", 350, 4.5),
        
        # Mumbai hotels
        (41, "The Taj Mahal Palace", "Mumbai", 350, 4.8),
        (42, "The Oberoi Mumbai", "Mumbai", 320, 4.7),
        (43, "Four Seasons Mumbai", "Mumbai", 280, 4.6),
        (44, "The Leela Mumbai", "Mumbai", 250, 4.5),
        
        # Delhi hotels
        (45, "The Oberoi New Delhi", "Delhi", 340, 4.8),
        (46, "The Leela Palace Delhi", "Delhi", 310, 4.7),
        (47, "Taj Palace Delhi", "Delhi", 290, 4.6),
        (48, "The Imperial New Delhi", "Delhi", 270, 4.5)
    ]
    
    c.executemany('INSERT INTO hotels (id, name, location, price_per_night, rating) VALUES (?, ?, ?, ?, ?)',
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
    
    c.executemany('INSERT INTO min_prices (origin, destination, min_flight_price, min_hotel_price) VALUES (?, ?, ?, ?)',
                  min_prices_data)
    
    conn.commit()

if __name__ == '__main__':
    conn = init_db()
    populate_sample_data(conn)
    conn.close()