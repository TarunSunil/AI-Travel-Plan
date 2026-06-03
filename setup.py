#!/usr/bin/env python3
"""
Setup script for Travel Planner application
This script helps initialize the database and set up the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print("✅ Python version is compatible")

def check_dependencies():
    """Check if required dependencies are installed"""
    required = ['flask', 'dotenv', 'requests', 'waitress', 'flask_limiter']
    for module in required:
        try:
            __import__(module)
            print(f"✅ {module} found")
        except ImportError:
            print(f"❌ {module} missing — installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])

def check_env_file():
    """Check if .env file exists and create if needed"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env file from template...")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created. Please update it with your database credentials and API keys.")
        else:
            print("❌ env.example file not found")
            return False
    else:
        print("✅ .env file exists")
    return True

def check_database_connection():
    """Test database connection"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your database configuration in .env file")
        return False

def initialize_database():
    """Initialize the database with tables and sample data"""
    try:
        print("🗄️  Initializing database...")
        from database import init_db, populate_sample_data
        conn = init_db()
        populate_sample_data(conn)
        conn.close()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Travel Planner Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    check_dependencies()
    
    # Check environment file
    if not check_env_file():
        print("❌ Setup failed: Environment file not configured")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("❌ Setup failed: Cannot connect to database")
        print("Please ensure PostgreSQL is running and credentials are correct")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Setup failed: Database initialization failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with your Gemini API key")
    print("2. Run the application: python main.py")
    print("3. Open http://localhost:5000 in your browser")

if __name__ == "__main__":
    main() 
