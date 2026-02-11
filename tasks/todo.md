# Critical API Connection and Minimum Price Fixes

## Analysis Complete ✅
- [x] **Minimum Price Issue**: System shows flight prices but should show hotel prices per night
- [x] **API Connection Issue**: Price formatting conflicts between backend and frontend
- [x] **Hotel Data Issue**: Limited real hotel data from Amadeus API
- [x] **Data Flow Issue**: Multiple places where formatted strings break number parsing

## Implementation Plan

### Task 1: Fix Minimum Price Display for Hotels
- **Priority**: High - User expects hotel pricing information
- [ ] **Task 1.1**: Update /get_min_prices endpoint to calculate minimum hotel prices
- [ ] **Task 1.2**: Change frontend to display "Minimum Hotel Cost per night"
- [ ] **Task 1.3**: Use real hotel search data for minimum price calculation

### Task 2: Fix API Data Flow and Formatting
- **Priority**: Critical - Data not displaying due to formatting conflicts
- [ ] **Task 2.1**: Backend sends raw numeric data, frontend handles formatting
- [ ] **Task 2.2**: Fix property name consistency throughout data flow
- [ ] **Task 2.3**: Ensure real-time API data reaches frontend properly

### Task 3: Enhance Hotel API Integration
- **Priority**: Medium - Improve real hotel data availability
- [ ] **Task 3.1**: Optimize Amadeus hotel API calls
- [ ] **Task 3.2**: Improve fallback data quality when API unavailable
- [ ] **Task 3.3**: Add more real hotel data sources if needed

### Task 4: Test and Verify Data Flow
- [ ] **Task 4.1**: Test minimum hotel price calculation
- [ ] **Task 4.2**: Verify flight and hotel search returns real data
- [ ] **Task 4.3**: Confirm all formatting works end-to-end

### Task 5: Documentation
- [ ] **Task 5.1**: Update Changes.txt with comprehensive fix summary

# Critical Layout and Authentication Fixes

## Analysis Complete ✅
- [x] **Main Page Layout Issue**: Hotels section displaying "Available Flights" title and corrupted layout
- [x] **Login Page Errors**: Multiple function definition errors breaking entire page
- [x] **Signup Page Error**: Password toggle element ID mismatch
- [x] **Logout Button Placement**: CSS positioning needs adjustment

## Implementation Plan

### Task 1: Fix Critical Login Page Errors ⚠️ HIGHEST PRIORITY
- **File**: [`static/js/login.js`](static/js/login.js)
- **Priority**: Highest - The login page is completely broken
- [ ] **Task 1.1**: Remove duplicate `getErrorMessage` function declaration (line ~209)
- [ ] **Task 1.2**: Ensure `togglePassword` function is properly defined and accessible
- [ ] **Task 1.3**: Verify `signInWithGoogle` function exists and is not duplicated
- [ ] **Task 1.4**: Verify `signInWithGithub` function exists and is not duplicated
- [ ] **Task 1.5**: Test all login functions are clickable and functional

### Task 2: Fix Main Page Layout Issues
- **Files**: [`templates/index.html`](templates/index.html), [`static/app.js`](static/app.js), [`static/css/style.css`](static/css/style.css)
- **Priority**: High - Core search results display is broken
- [ ] **Task 2.1**: Fix hotels section HTML structure in [`templates/index.html`](templates/index.html)
  - Check line ~115-130 for corrupted "Hotels Within Budget" section
  - Ensure section has correct `id="hotels-list"` and proper structure
- [ ] **Task 2.2**: Fix hotel rendering logic in [`static/app.js`](static/app.js)
  - Find hotel rendering forEach loop (~line 280-320)
  - Fix font sizes and layout structure in hotel card HTML
- [ ] **Task 2.3**: Adjust logout button positioning in [`static/css/style.css`](static/css/style.css)
  - Move logout button to top-right outside title padding
  - Update header flexbox layout

### Task 3: Fix Signup Page Password Toggle Error
- **Files**: [`templates/signup.html`](templates/signup.html), [`static/js/signup.js`](static/js/signup.js)
- **Priority**: Medium - Functional bug affecting user experience
- [ ] **Task 3.1**: Check password field IDs in [`templates/signup.html`](templates/signup.html)
  - Verify password field has correct `id` attribute
  - Ensure confirm password field has correct `id` attribute
- [ ] **Task 3.2**: Update [`static/js/signup.js`](static/js/signup.js) line 168
  - Fix element selection in `togglePassword` function
  - Add null checks before accessing `classList`

### Task 4: Final Review and Documentation
- **Files**: [`Changes.txt`](Changes.txt), [`steps.md`](steps.md), [`dev.md`](dev.md)
- [ ] **Task 4.1**: Test complete user flow: Signup -> Logout -> Login -> Search -> View Results
- [ ] **Task 4.2**: Create [`steps.md`](steps.md) documenting the changes made
- [ ] **Task 4.3**: Create [`dev.md`](dev.md) for post-development notes and production cleanup
- [ ] **Task 4.4**: Update [`Changes.txt`](Changes.txt) with comprehensive fix summary
- [ ] **Task 4.5**: Add review section to this [`todo.md`](todo.md) file

# Performance and Real-Data Improvements (October 2025)

## New Tasks (High Priority)

### Task 6: Speed Up Minimum Hotel Cost Calculation
- [x] **Task 6.1**: Refactor /get_min_prices endpoint to parallelize hotel price lookups using ThreadPoolExecutor.
- [x] **Task 6.2**: Add in-memory caching for recent min-price queries to avoid repeated API calls for the same city/date window.

### Task 7: Always Fetch Real Data from Amadeus
- [x] **Task 7.1**: Refactor /search_flights to fetch 3 real flights from Amadeus (remove mock data fallback).
- [x] **Task 7.2**: Refactor /search_hotels to fetch 3 real hotels from Amadeus (remove mock data fallback).
- [x] **Task 7.3**: Ensure frontend displays only real Amadeus data for both flights and hotels.

### Task 8: Testing and Verification
- [x] **Task 8.1**: Test min-price endpoint for speed and correctness.
- [x] **Task 8.2**: Test hotel and flight search endpoints for real data (no mock data).

---

## Next Steps
- [ ] Check in with user for approval before implementing further improvements (loading indicators, error handling, etc.).

---

# Review Section (to be updated after implementation)
- Min-price endpoint now uses parallel lookups plus a 6-hour cache, cutting repeat latency and quota usage.
- Flight/hotel endpoints and chatbot rely solely on real Amadeus data; accompanying unit tests verify caching behavior.

## Hotel Availability Issue Analysis (October 5, 2025)

**Root cause of "No hotels found within your budget" message:**
1. Amadeus Test API returns empty results for many destinations/dates due to:
   - Limited hotel inventory in test environment
   - Specific date/location combinations not available
   - API quota/rate limits
2. Error message was misleading - no budget filtering logic exists

**Changes made:**
- Updated error message to "No hotels available for the selected dates"
- Added comprehensive debug logging to track API responses
- Added error logging with status codes

**Recommendations for better hotel coverage:**
- Production Amadeus API has much better inventory
- Google Places API as backup ($0.032/search, $200 free credit/month)
- TripAdvisor or Booking.com APIs (commercial partnerships required)

**Testing tips:**
- Search major cities (London, Paris, NYC, Tokyo) for better coverage
- Use dates 30+ days in future
- Check console logs for exact API responses

# User Experience and Quality Improvements

## New Tasks (High Priority)

### Task 9: Improve User Experience
- [ ] **Task 9.1**: Add loading indicators to the frontend for all async actions (flight/hotel search, min price scan, chatbot).
- [ ] **Task 9.2**: Add user-friendly error messages for API failures (frontend and backend).
- [ ] **Task 9.3**: Add a review section summarizing changes and improvements.
- [ ] **Task 9.4**: Update Changes.txt after each major change.