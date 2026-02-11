# Critical API Issues - October 5, 2025

## 🔴 ISSUE 1: Hotels Returning 0 Results

### Root Causes
1. **Rate Limiting (429)**: `"Too many requests"` - Parallel min-price scan (30 concurrent requests) exceeds Amadeus Test API limits
2. **No Rooms Available (400)**: `"NO ROOMS AVAILABLE AT REQUESTED PROPERTY"` - Most hotels have no availability for selected dates
3. **API Query Overload**: 30+ simultaneous hotel searches triggered by min-price endpoint

### Evidence from Logs
```
Hotel list API response status: 200
Hotel list data: 131 hotels found  ✅ Tokyo has hotels
Fetching offers for 5 hotels...
Hotel offers API response status: 429  ❌ Rate limited
Hotel offers API response status: 400  ❌ No rooms available
```

### Impact
- Users see "No hotels available" even when 131 hotels exist
- Rate limiting prevents legitimate searches from working
- Min-price endpoint triggers 30x parallel hotel lookups → API throttling

---

## 🔴 ISSUE 2: All Flight Prices Are Identical (₹67,097)

### Root Cause
**Duplicate Flight Data**: All 3 displayed flights are the SAME flight (CA carrier)
- Flight 1: CA, 20:25→14:25, ₹67,097
- Flight 2: CA, 17:40→11:55, ₹67,097  
- Flight 3: CA, 17:40→11:55, ₹67,097 (duplicate of #2)

### Evidence from Image
```
Available Flights:
CA  20:25 BDS → 14:25 BDS  ₹67,097
CA  17:40 LHR → 11:55 NRT  ₹67,097
CA  17:40 LHR → 11:55 NRT  ₹67,097  ← EXACT DUPLICATE
```

### Why This Happens
- Amadeus Test API has limited flight variety for certain routes
- Same flight offer repeated multiple times in API response
- No deduplication logic in code

---

## 🔴 ISSUE 3: Chatbot Not Working

### Root Cause
**Invalid Gemini API Key**: 404 error indicates key is revoked/expired/invalid

### Evidence from Logs
```
Request Error: 404 Client Error: Not Found for url: 
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-latest:generateContent?key=AIzaSyCQQ41Drqlzlr-3qUa2wasrBF0RB80iptU
```

### Impact
- Travel Buddy returns empty responses
- Users can't get AI recommendations

---

## 🔴 ISSUE 4: Amadeus API Rate Limiting

### Current Usage Pattern
```
Min-Price Endpoint:
- Searches 30 dates in parallel (8 workers)
- Each date = 1 hotel search
- Total: 30 API calls in ~5 seconds

User Search:
- 1 hotel search per destination
- If min-price ran recently: 31 API calls in quick succession
```

### Amadeus Test API Limits (Free Tier)
- **Rate Limit**: ~10 requests per second
- **Monthly Quota**: 1,000 free calls (then paid)
- **Burst Protection**: Throttles rapid parallel requests

### Why We're Getting 429 Errors
1. Min-price triggers 30 hotel searches instantly
2. ThreadPoolExecutor (8 workers) sends 8 simultaneous requests
3. Amadeus throttles after ~10 requests/second
4. Remaining 20+ requests get 429 errors

---

## ✅ SOLUTIONS

### Solution 1: Disable Aggressive Min-Price Scanning
**Immediate Fix** - Reduce parallel load

```python
# main.py - Reduce from 30 to 7 days
def get_min_price_for_destination(dest_name, fetcher=amadeus_search_hotels, days=7):  # Was 30
    # ...existing code...
```

### Solution 2: Add Rate Limiting with Delays
**Add backoff between requests**

```python
import time

def _collect_prices_for_date(dest_name, check_date, fetcher):
    time.sleep(0.5)  # 500ms delay between requests
    # ...existing code...
```

### Solution 3: Fix Gemini API Key
**Regenerate or use correct key**

1. Go to: https://aistudio.google.com/app/apikey
2. Create new API key
3. Update `.env`:
   ```
   GEMINI_API_KEY=YOUR_NEW_KEY_HERE
   ```

### Solution 4: Deduplicate Flight Results
**Remove duplicate flights by unique identifier**

```python
def search_flights(...):
    # After processing flights
    seen = set()
    unique_flights = []
    for flight in flights:
        key = f"{flight['airline']}{flight['flightNumber']}{flight['departureTime']}"
        if key not in seen:
            seen.add(key)
            unique_flights.append(flight)
    return unique_flights[:3]
```

### Solution 5: Use Production API (Long-term)
**Upgrade to Amadeus Production**
- Better rate limits (1,000+ req/second)
- More hotel inventory
- Better availability
- Costs: ~$0.01-0.05 per API call

---

## 🎯 RECOMMENDED ACTION PLAN

### Priority 1: Emergency Fixes (Do NOW)
1. ✅ Reduce min-price scan from 30 to 7 days
2. ✅ Add 0.5s delay between hotel searches
3. ✅ Fix Gemini API key
4. ✅ Add flight deduplication

### Priority 2: UX Improvements
5. Disable min-price endpoint temporarily (comment out)
6. Show loading states for slow searches
7. Add retry logic with exponential backoff

### Priority 3: Production Readiness
8. Upgrade to Amadeus Production API
9. Add request caching layer (Redis)
10. Implement proper rate limiting middleware

---

## 📊 TEST RESULTS AFTER FIX

### Expected Improvements
- ✅ Hotels: Should return results (when available)
- ✅ Flights: No duplicate prices
- ✅ Chatbot: Working responses
- ✅ Rate Limits: Fewer 429 errors

### What Won't Change
- ❌ "NO ROOMS AVAILABLE" (400) errors will persist
  - This is Test API data limitation
  - Try dates 60+ days in future
  - Or upgrade to Production API

---

## 🔍 HOW TO VERIFY FIXES

### Test 1: Check Flight Variety
```
Search: London → Tokyo, Dec 24-29
Expected: 3 different flights with different prices
Current: 3 flights, all ₹67,097 (same price)
```

### Test 2: Check Hotel Availability
```
Search: Tokyo, Dec 24-29
Check logs for:
- "Hotel list data: 131 hotels found" ✅
- "Hotel offers API response status: 200" ✅ (not 429)
- "Successfully parsed hotel: ..." ✅
```

### Test 3: Check Chatbot
```
Ask: "Tell me about Tokyo"
Expected: AI response with recommendations
Current: Empty response
```

### Test 4: Rate Limit Check
```
Load page → Min-price should complete without errors
Check logs for 429 errors: Should be 0
```
