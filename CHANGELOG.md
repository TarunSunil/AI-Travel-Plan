# Changelog

All notable changes to the Travel Planner project are documented here.

## [3.0.0] - 2026-06-05

### 🔄 Travel Data Layer
- **Replaced**: Amadeus API with free-tier multi-source data layer
- **Added**: AviationStack (500 req/month) for real flight schedules
- **Added**: OpenSky Network (no key, truly free) as secondary flight source
- **Added**: OpenTripMap (5000 req/day) for real hotel/POI discovery
- **Added**: Gemini AI synthesis as intelligent fallback for both flights and hotels
- **Added**: Static hardcoded fallback as last resort

### 💾 Caching
- **Added**: Persistent SQLite cache (`cache.db`) surviving app restarts
- **Added**: TTL-based cache (flights: 6h, hotels: 12h, min-prices: 6h)
- **Added**: Stale-on-error: serves last valid cache when all APIs are down
- **Added**: Source tagging per cached entry (live/ai_synthesized/cached/static_fallback)

### ✨ New Features
- **Added**: `/api/health` endpoint with API key status and cache statistics
- **Added**: Data source badges on flight/hotel cards (Live / AI / Cached / Est.)
- **Added**: Travel class selector (Economy, Premium Economy, Business, First)
- **Added**: Passengers count selector (1–4 adults)
- **Added**: Budget filter with over-budget warning on hotel cards
- **Added**: Non-stop vs stops indicator on flight cards
- **Added**: Auto-advance return date when departure date is selected
- **Added**: Same-origin/destination validation in frontend

### 🗑️ Removed
- **Removed**: `amadeus_api.py` dependency
- **Removed**: `/flight_status` route (unused in UI)
- **Removed**: In-memory `MIN_PRICE_CACHE` threading logic (replaced by `cache.db`)

## [2.0.0] - 2026-01-30

### 🔒 Security
- **Fixed**: SECRET_KEY now required in .env (no fallback to random generation)
- **Added**: XSS protection with HTML sanitization throughout frontend
- **Added**: Comprehensive input validation module (validation.py)
- **Added**: Rate limiting on all API endpoints (Flask-Limiter)
- **Added**: Server-side validation for dates, budgets, passenger counts, city codes

### ⚡ Performance
- **Improved**: Reduced min-price API calls from 7 to 3 days (40% reduction)
- **Added**: Debug logging wrapper (DEV_MODE flag) to disable logs in production
- **Optimized**: API request patterns to reduce rate limiting

### 🧪 Testing
- **Added**: pytest infrastructure with comprehensive test suite
- **Added**: Unit tests for validation module (20+ tests)
- **Added**: Integration tests for Flask routes
- **Added**: Test fixtures for sample data

### 🗄️ Database
- **Added**: Supabase PostgreSQL support module (supabase_db.py)
- **Added**: Complete migration guide (docs/SUPABASE_MIGRATION.md)
- **Fixed**: Removed duplicate table creation code in database.py (45 lines)
- **Added**: PostgreSQL driver support (psycopg2-binary)

### 📦 Dependencies
- **Added**: Flask-Limiter 3.5.0 (rate limiting)
- **Added**: pytest 8.0.0 (testing)
- **Added**: pytest-flask 1.3.0 (Flask testing)
- **Added**: psycopg2-binary 2.9.9 (PostgreSQL)
- **Updated**: Standardized on pnpm for JavaScript dependencies

### 🧹 Code Quality
- **Removed**: Dead files (temp_test.ps1, tempCodeRunnerFile.cpp, etc.)
- **Removed**: Deprecated test files (direct_api_test.py, test_amadeus_api.py)
- **Fixed**: Removed 45 lines of duplicate code in database.py
- **Improved**: Code organization and structure

### 📚 Documentation
- **Added**: docs/ folder with organized documentation
- **Added**: IMPLEMENTATION_SUMMARY.md (comprehensive improvements summary)
- **Added**: docs/SUPABASE_MIGRATION.md (cloud database migration guide)
- **Added**: docs/README.md (documentation index)
- **Moved**: 19 documentation files from root to docs/ folder
- **Updated**: README.md with new features and setup instructions
- **Updated**: sample.env with Supabase configuration

### 🛠️ Configuration
- **Added**: pytest.ini (test configuration)
- **Added**: tests/conftest.py (test fixtures)
- **Updated**: requirements.txt with new dependencies
- **Updated**: .gitignore (already properly configured)

### 🚀 Deployment
- **Improved**: Production readiness checklist
- **Added**: Environment variable validation
- **Added**: Database migration tooling

## [1.0.0] - Initial Release

### Features
- Firebase authentication (email/password, Google, GitHub)
- Flight search via Amadeus API
- Hotel search functionality
- AI travel assistant with Gemini AI
- Budget planning tools
- Interactive chat interface
- Multi-city support (10+ cities)
- Responsive design
- Real-time pricing
- Date range planning

---

**Version Format**: [Major.Minor.Patch]
- **Major**: Breaking changes
- **Minor**: New features (backwards compatible)
- **Patch**: Bug fixes (backwards compatible)
