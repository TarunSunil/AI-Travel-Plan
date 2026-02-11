# Bug Report: Search Fails for Invalid Date Range

**Bug ID:** BUG-001
**Title:** Search returns 500 Internal Server Error when End Date is before Start Date
**Severity:** Medium
**Priority:** High
**Environment:** Windows 10, Chrome 120.0, Localhost (Dev)

**Description:**
When a user selects an "End Date" that is chronologically before the "Start Date" in the search form, the API returns a 500 Internal Server Error instead of a graceful 400 Bad Request validation error.

**Steps to Reproduce:**
1. Open the Travel Planner application (`http://localhost:5000`).
2. Select "Delhi" as Origin.
3. Select "Mumbai" as Destination.
4. Set Start Date to "2025-12-01".
5. Set End Date to "2025-11-01" (a past date relative to start).
6. Click "Search".

**Expected Result:**
The application should display a user-friendly error message: "End date must be after start date" and the API should return `400 Bad Request`.

**Actual Result:**
The application shows a generic error, and the console logs show a 500 Internal Server Error from the `/search` endpoint.

**Screenshots:**
errors already taken care off.
