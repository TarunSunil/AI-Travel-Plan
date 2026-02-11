# Test Cases for AI Travel Planner

## TC01 – Validate Amadeus Flight Search API – Positive Case
*   **Description:** Verify that the flight search functionality returns valid results when correct parameters are provided.
*   **Pre-conditions:** Backend server is running, Amadeus API keys are valid.
*   **Input:**
    *   Source: "Delhi (DEL)"
    *   Destination: "Mumbai (BOM)"
    *   Start Date: [Future Date]
    *   End Date: [Future Date + 3 days]
    *   Adults: 1
*   **Steps:**
    1.  Navigate to the home page.
    2.  Select "Delhi" as the source and "Mumbai" as the destination.
    3.  Select valid future dates.
    4.  Click "Search".
*   **Expected Result:**
    *   API returns status `200 OK`.
    *   A list of available flights is displayed on the UI.
    *   Flight details (Airline, Time, Price) are visible.

## TC02 – Validate Authentication (Google Login) – Positive Case
*   **Description:** Verify that a user can successfully log in using their Google account.
*   **Pre-conditions:** Firebase Authentication is configured.
*   **Input:** Valid Google Account credentials.
*   **Steps:**
    1.  Navigate to the Login page.
    2.  Click on the "Sign in with Google" button.
    3.  Enter valid Google credentials in the popup window.
*   **Expected Result:**
    *   Authentication is successful.
    *   User is redirected to the main dashboard/home page.
    *   "Logout" button becomes visible.

## TC03 – Validate Itinerary Generation via Gemini AI
*   **Description:** Verify that the AI Chatbot generates a valid travel itinerary based on user preferences.
*   **Pre-conditions:** Gemini API key is valid.
*   **Input:**
    *   Message: "Plan a 3-day trip to Goa with a budget of 20000 INR"
*   **Steps:**
    1.  Navigate to the "Travel Buddy" (Chatbot) section.
    2.  Enter the prompt in the chat input field.
    3.  Click "Send".
*   **Expected Result:**
    *   AI processes the request.
    *   A structured itinerary (Day 1, Day 2, Day 3) is returned.
    *   Suggestions include activities and estimated costs within the budget.

## TC04 – API Error Handling – Rate Limit (429)
*   **Description:** Verify that the application handles API rate limits gracefully using exponential backoff.
*   **Pre-conditions:** Access to backend logs or network monitor.
*   **Input:** Rapid succession of search requests (e.g., 10 requests in 1 second).
*   **Steps:**
    1.  Trigger multiple search requests to the Amadeus API endpoint rapidly.
    2.  Observe the backend logs or network traffic.
*   **Expected Result:**
    *   The application detects `429 Too Many Requests` errors.
    *   The system automatically retries the request after a delay (exponential backoff).
    *   The user eventually sees results or a friendly "Please wait" message, rather than a crash.

## TC05 – UI – Validate Form Field Validation
*   **Description:** Verify that the search form prevents submission with empty or invalid fields.
*   **Pre-conditions:** None.
*   **Input:** Empty search form.
*   **Steps:**
    1.  Navigate to the home page.
    2.  Leave "Source" and "Destination" fields empty.
    3.  Click "Search".
*   **Expected Result:**
    *   Form is not submitted to the backend.
    *   An error message "Please select valid origin and destination" or similar is displayed.
    *   Browser validation prompts (if applicable) appear on required fields.
