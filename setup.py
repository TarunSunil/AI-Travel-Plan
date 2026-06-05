#!/usr/bin/env python3
"""
Setup script for Travel Planner application
This script helps install dependencies and bootstrap a local .env file.
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

def install_requirements():
    """Install Python dependencies from requirements.txt"""
    req = Path("requirements.txt")
    if not req.exists():
        print("❌ requirements.txt not found")
        sys.exit(1)
    print("📦 Installing dependencies from requirements.txt ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req)])
    print("✅ Dependencies installed")

def check_env_file():
    """Check if .env file exists and create if needed"""
    env_file = Path(".env")
    env_example = Path("sample.env")
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env file from template...")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created. Please update it with your API keys (Gemini + optional travel APIs).")
        else:
            print("❌ sample.env file not found")
            return False
    else:
        print("✅ .env file exists")
    return True

def main():
    """Main setup function"""
    print("🚀 Travel Planner Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_requirements()
    
    # Check environment file
    if not check_env_file():
        print("❌ Setup failed: Environment file not configured")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with your Gemini API key (required)")
    print("2. Run the application: python main.py")
    print("3. Open http://localhost:5000 in your browser")

if __name__ == "__main__":
    main() 
