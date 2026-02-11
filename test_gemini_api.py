"""
Test Gemini API Key
This script tests if your Gemini API key is valid and working.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"✓ Found API Key: {GEMINI_API_KEY[:20]}...")

# Test API endpoints with different models
models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-latest",
    "gemini-2.5-pro"
]

headers = {"Content-Type": "application/json"}
body = {
    "contents": [{
        "parts": [{
            "text": "Hello, respond with just 'OK' if you're working."
        }]
    }]
}

print("\n" + "="*50)
print("Testing Gemini API Models")
print("="*50 + "\n")

working_models = []

for model in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    try:
        print(f"Testing {model}...", end=" ")
        response = requests.post(url, headers=headers, json=body, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                result = data['candidates'][0]['content']['parts'][0]['text']
                print(f"✓ WORKS - Response: {result.strip()}")
                working_models.append(model)
            else:
                print(f"⚠ Response OK but no content")
        elif response.status_code == 404:
            print(f"✗ Not found (model may not exist or API key doesn't have access)")
        elif response.status_code == 400:
            print(f"✗ Bad request - {response.json().get('error', {}).get('message', '')}")
        elif response.status_code == 403:
            print(f"✗ Forbidden - API key might be invalid or doesn't have permission")
        elif response.status_code == 429:
            print(f"✗ Rate limited - too many requests")
        else:
            print(f"✗ Error {response.status_code}: {response.text[:100]}")
    
    except requests.exceptions.Timeout:
        print(f"✗ Timeout - API took too long to respond")
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {str(e)[:50]}")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)[:50]}")

print("\n" + "="*50)
print("Summary")
print("="*50)

if working_models:
    print(f"\n✓ SUCCESS: {len(working_models)} model(s) working:")
    for model in working_models:
        print(f"  - {model}")
    print(f"\n✓ Your Gemini API key is VALID!")
    print(f"\nRecommendation: Use '{working_models[0]}' in your main.py")
else:
    print(f"\n✗ FAILURE: No models working")
    print("\nPossible reasons:")
    print("1. Invalid API key - Get a new one from https://aistudio.google.com/app/apikey")
    print("2. API key doesn't have Gemini API access")
    print("3. Quota exceeded or billing not enabled")
    print("4. Region restrictions")
    print("\nTo fix:")
    print("1. Go to https://aistudio.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Replace GEMINI_API_KEY in .env file")
    print("4. Make sure Gemini API is enabled for your project")

print("\n" + "="*50 + "\n")
