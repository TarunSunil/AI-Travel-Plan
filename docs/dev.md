# Development Notes (October 5, 2025)

## Temporary / Debug Code to Remove Before Production
- None introduced in this iteration. All logic committed today is production-ready and relies solely on live Amadeus data.

## Follow-Up Items for Engineers
- Monitor cache hit rate and adjust TTL if Amadeus quota pressure persists.
- Add full integration tests for flight/hotel endpoints once sandbox fixtures are available.
- Monitor Amadeus rate limits after deployment; parallel requests increase concurrency.
