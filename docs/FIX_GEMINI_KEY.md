# URGENT: Fix Gemini API Key (Chatbot Not Working)

## Problem
```
Request Error: 404 Client Error: Not Found for url: 
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-latest:generateContent?key=AIzaSyCQQ41Drqlzlr-3qUa2wasrBF0RB80iptU
```

**Your current Gemini API key is INVALID** (404 = Not Found)

## Why This Happens
- Key was deleted or revoked
- Key expired
- Wrong API endpoint
- API quota exceeded

## Fix Steps

### Step 1: Get New API Key
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Select your Google Cloud project (or create new one)
4. Copy the new API key

### Step 2: Update .env File
```bash
# Open .env file
# Replace the GEMINI_API_KEY line:

GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE
```

### Step 3: Restart Flask
```powershell
# Press CTRL+C to stop current server
# Then restart:
python main.py
```

### Step 4: Test Chatbot
1. Open browser: http://127.0.0.1:5000
2. Scroll to "Travel Buddy" section
3. Type: "Tell me about Tokyo"
4. Should get AI response

## Alternative: Verify Current Key

Try this command to check if key works:
```powershell
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-latest:generateContent?key=AIzaSyCQQ41Drqlzlr-3qUa2wasrBF0RB80iptU" `
  -H "Content-Type: application/json" `
  -d '{\"contents\":[{\"parts\":[{\"text\":\"test\"}]}]}'
```

If you get 404, key is definitely invalid.

## Free Tier Limits
- **60 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

Check usage: https://aistudio.google.com/app/prompts
