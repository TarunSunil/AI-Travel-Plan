# API Request-Response Comparison

**Endpoint:** `/search`
**Method:** `POST`

## Request

**Headers:**
- Content-Type: `application/x-www-form-urlencoded`

**Body (Form Data):**
```json
{
  "startPointCode": "DEL",
  "destinationCode": "BOM",
  "destination": "Mumbai, India",
  "startDate": "2025-11-28",
  "endDate": "2025-11-29",
  "adults": "1"
}
```

## Response

**Status:** `200 OK`

**Body (JSON):**
```json
{
    "flights": [
        {
            "airline": "Air India",
            "flightNumber": "AI887",
            "departureTime": "2025-11-28T07:00:00",
            "arrivalTime": "2025-11-28T09:15:00",
            "price": 4500.00,
            "currency": "INR"
        },
        {
            "airline": "IndiGo",
            "flightNumber": "6E5023",
            "departureTime": "2025-11-28T10:30:00",
            "arrivalTime": "2025-11-28T12:40:00",
            "price": 4200.00,
            "currency": "INR"
        }
    ],
    "hotels": [
        {
            "name": "Taj Mahal Tower",
            "rating": 5,
            "price": 18000.00,
            "currency": "INR",
            "address": "Apollo Bunder, Mumbai"
        },
        {
            "name": "Trident Nariman Point",
            "rating": 5,
            "price": 14500.00,
            "currency": "INR",
            "address": "Nariman Point, Mumbai"
        }
    ]
}
```

## Analysis
The request correctly sends the city codes and dates. The response aggregates both flight and hotel data into a single JSON object, allowing the frontend to render both sections simultaneously. The structure matches the expected schema for the new `/search` endpoint.
