# Steps Log (October 5, 2025)

1. Parallelized the `/get_min_prices` hotel scan using `ThreadPoolExecutor` with 30 concurrent lookups capped at 8 workers.
2. Updated `amadeus_api.search_flights` to return only real Amadeus flight offers (no mock fallbacks) and limited responses to three entries.
3. Simplified `amadeus_api.search_hotels` to fetch up to three genuine hotel offers; removed mock hotel generation logic entirely.
4. Added local `datetime` imports inside chatbot helper branches to prevent `UnboundLocalError` when defaulting date ranges.
5. Implemented a six-hour in-memory cache for minimum hotel price lookups to reduce repeated Amadeus calls.
6. Added `tests/test_min_price_cache.py` to verify caching consistency and no redundant fetches.
