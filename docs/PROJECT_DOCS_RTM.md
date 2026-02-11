# Project Documentation, Test Plan & RTM
**Project Name:** AI Travel Planner
**Version:** 1.0
**Date:** November 27, 2025
**Author:** Tarun Sunil

---

## 1. Executive Summary

The **AI Travel Planner** is a sophisticated web-based application designed to revolutionize the travel planning experience. By integrating real-time data from the Amadeus API with the generative capabilities of Google's Gemini AI, the platform offers users a seamless interface to search for flights, discover hotels, and generate personalized travel itineraries. The system is built on a robust Flask backend with a responsive vanilla JavaScript frontend, ensuring performance and accessibility.

---

## 2. System Architecture

### 2.1 High-Level Architecture
The application follows a standard Model-View-Controller (MVC) pattern, adapted for a modern web application structure.

*   **Frontend (View/Controller):**
    *   **HTML5/CSS3:** Provides the structure and styling.
    *   **JavaScript (Vanilla):** Handles user interactions, form validation, and asynchronous API calls (`fetch`).
    *   **Firebase SDK:** Manages client-side authentication.

*   **Backend (Model/Controller):**
    *   **Python (Flask):** Serves as the REST API and web server.
    *   **Routes:** Handles HTTP requests for search, chat, and static files.
    *   **Services:** Dedicated modules for external API integration (`amadeus_api.py`) and data processing.

*   **Data Layer (Model):**
    *   **SQLite:** Stores local cache of flight/hotel data and minimum prices to reduce API costs and improve latency.
    *   **In-Memory Cache:** Python dictionaries used for short-term caching of frequent queries.

*   **External Services:**
    *   **Amadeus API:** Source for live flight and hotel offers.
    *   **Google Gemini AI:** Engine for the "Travel Buddy" chatbot.
    *   **Firebase Auth:** Identity provider for secure user management.

### 2.2 Directory Structure
```
d:\code\Travel-Planner\
├── main.py                 # Entry point, Flask app, and route definitions
├── amadeus_api.py          # Wrapper for Amadeus Flight & Hotel APIs
├── city_data.py            # Static data for supported cities and airport codes
├── database.py             # SQLite database initialization and schema definition
├── requirements.txt        # Python dependencies
├── static/
│   ├── app.js              # Main frontend logic (event listeners, API calls)
│   ├── styles.css          # Global styles
│   └── ...                 # Images and other assets
├── templates/
│   ├── index.html          # Main dashboard
│   ├── login.html          # Login page
│   └── signup.html         # Registration page
└── ...
```

---

## 3. Detailed Component Analysis

### 3.1 Backend Modules

#### `main.py`
*   **Role:** The core application server.
*   **Key Functions:**
    *   `index()`, `login()`, `signup()`: Serve HTML templates.
    *   `search_all()`: **[NEW]** Aggregates flight and hotel search results into a single response.
    *   `chatbot()`: Interfaces with Gemini AI to generate travel advice.
    *   `get_min_prices()`: Retrieves cached minimum prices for budget estimation.
*   **Configuration:** Loads environment variables (`.env`) for API keys and secrets.

#### `amadeus_api.py`
*   **Role:** Handles all communications with the Amadeus Travel API.
*   **Key Features:**
    *   **Token Management:** Automatically fetches and refreshes OAuth2 access tokens.
    *   **Retry Logic:** Implements exponential backoff for `429 Too Many Requests` errors.
    *   **Data Normalization:** Converts raw API responses into a simplified JSON structure for the frontend.
*   **Endpoints Used:**
    *   `/v2/shopping/flight-offers`
    *   `/v1/reference-data/locations/hotels/by-city`
    *   `/v3/shopping/hotel-offers`

#### `database.py`
*   **Role:** Manages the SQLite database `travel_planner.db`.
*   **Schema:**
    *   `flights`: Stores flight offers (origin, destination, price, airline).
    *   `hotels`: Stores hotel details (name, location, price, rating).
    *   `min_prices`: Caches minimum costs for route pairs to speed up UI tooltips.
    *   `api_cache`: Generic cache for API responses.
*   **Utility:** Includes `populate_sample_data()` to seed the DB with fallback data for testing.

#### `city_data.py`
*   **Role:** Provides static reference data to reduce API dependency for static information.
*   **Content:** Dictionary `AVAILABLE_CITIES` mapping city names to IATA codes (e.g., "New York" -> "NYC", "JFK").

### 3.2 Frontend Modules

#### `static/app.js`
*   **Role:** Orchestrates the user experience.
*   **Key Workflows:**
    *   **Initialization:** Loads city options into dropdowns on page load.
    *   **Search:** Captures form data, validates dates, calls `/search`, and renders results dynamically.
    *   **Chat:** Sends user messages to `/chatbot` and appends AI responses to the chat window.
    *   **Budget Tooltip:** Updates the "Daily Budget" tooltip with minimum price data based on selected destination.

---

## 4. API Documentation (Internal)

### 4.1 `POST /search`
*   **Description:** Combined search for flights and hotels.
*   **Request Body:**
    ```json
    {
      "startPointCode": "DEL",
      "destinationCode": "BOM",
      "destination": "Mumbai",
      "startDate": "2025-12-01",
      "endDate": "2025-12-05",
      "adults": 1
    }
    ```
*   **Response:**
    ```json
    {
      "flights": [{ "airline": "IndiGo", "price": 4500, ... }],
      "hotels": [{ "name": "Taj", "price": 12000, ... }]
    }
    ```

### 4.2 `POST /chatbot`
*   **Description:** Generates AI travel advice.
*   **Request Body:**
    ```json
    {
      "message": "Plan a 3-day trip to Goa",
      "destination": "Goa"
    }
    ```
*   **Response:**
    ```json
    {
      "response": "Here is a 3-day itinerary for Goa..."
    }
    ```

---

## 5. Requirement Traceability Matrix (RTM)

| Req ID | Requirement Description | Test Case ID | Test Case Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | System shall allow users to search for flights by Origin, Destination, and Date. | **TC01** | Validate Amadeus Flight Search API – Positive Case | High | Pass |
| **REQ-02** | System shall allow users to log in using Google Authentication. | **TC02** | Validate Authentication (Google Login) – Positive Case | High | Pass |
| **REQ-03** | System shall generate a travel itinerary based on user prompts. | **TC03** | Validate Itinerary Generation via Gemini AI | Medium | Pass |
| **REQ-04** | System shall handle API rate limits without crashing. | **TC04** | API Error Handling – Rate Limit (429) | Medium | Pass |
| **REQ-05** | System shall validate user input in the search form (e.g., empty fields). | **TC05** | UI – Validate Form Field Validation | Low | Pass |
| **REQ-06** | System shall display hotel options for the selected destination. | **TC06** | Validate Hotel Search Functionality | Medium | Pass |
| **REQ-07** | System shall prevent "End Date" from being earlier than "Start Date". | **TC07** | Validate Date Range Logic | Medium | Pass |
| **REQ-08** | System shall provide fallback data if external APIs fail. | **TC08** | Validate Database Fallback Mechanism | Low | Pass |

---

## 6. Test Plan & Execution

### 6.1 Test Strategy
*   **Unit Testing:** `tests/` folder contains scripts like `test_amadeus_api.py` to verify individual components.
*   **Integration Testing:** Manual verification of the flow from Frontend -> Flask -> Amadeus/Gemini.
*   **UI Testing:** Verifying responsiveness and error states in Chrome DevTools.

### 6.2 Test Cases Detail

#### TC01: Flight Search
*   **Input:** Origin: DEL, Dest: BOM, Date: Future.
*   **Expected:** List of flights with prices in INR.
*   **Actual:** JSON response received, UI populated.

#### TC03: AI Itinerary
*   **Input:** "Plan a trip to Paris".
*   **Expected:** Detailed day-wise plan.
*   **Actual:** Gemini returns structured text, rendered as HTML in chat.

#### TC04: Rate Limiting
*   **Input:** Rapid refresh of search.
*   **Expected:** Backend logs show "Retrying in X seconds".
*   **Actual:** `_request_with_retry` in `amadeus_api.py` handles 429s correctly.

---

## 7. Installation & Setup

1.  **Clone Repository:** `git clone <repo_url>`
2.  **Install Dependencies:** `pip install -r requirements.txt`
3.  **Environment Setup:** Create `.env` with:
    *   `AMADEUS_CLIENT_ID`
    *   `AMADEUS_CLIENT_SECRET`
    *   `GEMINI_API_KEY`
    *   `SECRET_KEY`
4.  **Initialize Database:** Run `python database.py` to create tables and seed data.
5.  **Run Application:** `python main.py`
6.  **Access:** Open `http://localhost:5000` in a browser.
