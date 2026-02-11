"""
Supabase PostgreSQL database module for Travel Planner.
Replaces SQLite with cloud-based PostgreSQL database.

Setup Instructions:
1. Create a free Supabase account at https://supabase.com
2. Create a new project
3. Get your connection details from Project Settings > Database
4. Add to .env file:
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
   DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """
    Create and return a PostgreSQL database connection.
    
    Returns:
        psycopg2 connection object
    """
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set. Please configure Supabase connection.")
    
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        raise


def init_database():
    """
    Initialize database tables if they don't exist.
    Creates tables for flights, hotels, min_prices, and api_cache.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create flights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flights (
                id SERIAL PRIMARY KEY,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                date DATE NOT NULL,
                airline TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Flights table created/verified")
        
        # Create hotels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotels (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                price_per_night DECIMAL(10, 2) NOT NULL,
                rating DECIMAL(3, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Hotels table created/verified")
        
        # Create min_prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS min_prices (
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                min_flight_price DECIMAL(10, 2),
                min_hotel_price DECIMAL(10, 2),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (origin, destination)
            )
        ''')
        print("✓ Min prices table created/verified")
        
        # Create api_cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_cache (
                route_key TEXT NOT NULL,
                data_type TEXT NOT NULL,
                response_data TEXT NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                PRIMARY KEY (route_key, data_type)
            )
        ''')
        print("✓ API cache table created/verified")
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_flights_date 
            ON flights(date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_flights_route 
            ON flights(origin, destination)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_api_cache_expires 
            ON api_cache(expires_at)
        ''')
        print("✓ Indexes created/verified")
        
        conn.commit()
        print("\n✅ Database initialized successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def cache_flight(origin, destination, price, date, airline):
    """Cache flight data in database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO flights (origin, destination, price, date, airline)
            VALUES (%s, %s, %s, %s, %s)
        ''', (origin, destination, price, date, airline))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error caching flight: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def cache_hotel(name, location, price_per_night, rating):
    """Cache hotel data in database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO hotels (name, location, price_per_night, rating)
            VALUES (%s, %s, %s, %s)
        ''', (name, location, price_per_night, rating))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error caching hotel: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def update_min_prices(origin, destination, min_flight_price=None, min_hotel_price=None):
    """Update minimum prices for a route."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO min_prices (origin, destination, min_flight_price, min_hotel_price, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (origin, destination) 
            DO UPDATE SET 
                min_flight_price = COALESCE(EXCLUDED.min_flight_price, min_prices.min_flight_price),
                min_hotel_price = COALESCE(EXCLUDED.min_hotel_price, min_prices.min_hotel_price),
                updated_at = EXCLUDED.updated_at
        ''', (origin, destination, min_flight_price, min_hotel_price, datetime.now()))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error updating min prices: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_min_prices(origin, destination):
    """Get minimum prices for a route."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT min_flight_price, min_hotel_price 
            FROM min_prices 
            WHERE origin = %s AND destination = %s
        ''', (origin, destination))
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        cursor.close()
        conn.close()


def cache_api_response(route_key, data_type, response_data, ttl_hours=6):
    """Cache API response data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        from datetime import timedelta
        now = datetime.now()
        expires_at = now + timedelta(hours=ttl_hours)
        
        cursor.execute('''
            INSERT INTO api_cache (route_key, data_type, response_data, last_updated, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (route_key, data_type)
            DO UPDATE SET
                response_data = EXCLUDED.response_data,
                last_updated = EXCLUDED.last_updated,
                expires_at = EXCLUDED.expires_at
        ''', (route_key, data_type, response_data, now, expires_at))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error caching API response: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_cached_api_response(route_key, data_type):
    """Get cached API response if not expired."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT response_data 
            FROM api_cache 
            WHERE route_key = %s 
            AND data_type = %s 
            AND expires_at > %s
        ''', (route_key, data_type, datetime.now()))
        result = cursor.fetchone()
        return result['response_data'] if result else None
    finally:
        cursor.close()
        conn.close()


def cleanup_expired_cache():
    """Remove expired cache entries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            DELETE FROM api_cache WHERE expires_at < %s
        ''', (datetime.now(),))
        deleted = cursor.rowcount
        conn.commit()
        print(f"Cleaned up {deleted} expired cache entries")
    except psycopg2.Error as e:
        print(f"Error cleaning cache: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    """Run database initialization when script is executed directly."""
    print("🚀 Initializing Supabase PostgreSQL database...")
    print("=" * 60)
    init_database()
    print("=" * 60)
    print("\n✨ Database setup complete!")
    print("\n📝 Next steps:")
    print("1. Update main.py to use supabase_db instead of database")
    print("2. Test the connection with your application")
    print("3. Migrate any existing SQLite data if needed")
