# Supabase PostgreSQL Migration Guide

## Overview

This guide will help you migrate from SQLite to Supabase PostgreSQL for better scalability, cloud hosting, and performance.

## Benefits of Supabase

- ✅ **Free Tier**: 500MB database, unlimited API requests
- ✅ **Cloud-hosted**: No local database files
- ✅ **Real-time**: Built-in real-time subscriptions
- ✅ **Backups**: Automatic daily backups
- ✅ **Scalable**: Easy to upgrade as your app grows
- ✅ **PostgreSQL**: Full PostgreSQL features

## Setup Instructions

### 1. Create Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up for a free account
3. Click "New Project"
4. Fill in:
   - **Project name**: `travel-planner` (or your preferred name)
   - **Database password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your users
   - **Pricing plan**: Free

### 2. Get Connection Details

Once your project is created:

1. Go to **Project Settings** (gear icon)
2. Click on **Database** in the sidebar
3. Note down:
   - **Host**: `db.xxx.supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: The password you set earlier

4. Go to **Project Settings** > **API**
5. Note down:
   - **Project URL**: `https://xxx.supabase.co`
   - **Anon public key**: `eyJhbGc...`

### 3. Update Environment Variables

Add these to your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key
DATABASE_URL=postgresql://postgres:your_password@db.your-project.supabase.co:5432/postgres

# Existing variables (keep these)
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_key
# ... other variables
```

**Important**: Replace `your-project`, `your_password`, and `your_anon_public_key` with your actual values.

### 4. Install PostgreSQL Driver

Update your `requirements.txt`:

```txt
Flask==3.0.0
python-dotenv==1.0.0
requests==2.31.0
google-generativeai==0.3.2
waitress==2.1.2
Flask-Limiter==3.5.0
pytest==8.0.0
pytest-flask==1.3.0
psycopg2-binary==2.9.9  # Add this for PostgreSQL support
```

Install the new dependency:

```powershell
pip install psycopg2-binary
```

### 5. Initialize Database

Run the initialization script:

```powershell
python supabase_db.py
```

You should see:
```
🚀 Initializing Supabase PostgreSQL database...
============================================================
✓ Flights table created/verified
✓ Hotels table created/verified
✓ Min prices table created/verified
✓ API cache table created/verified
✓ Indexes created/verified

✅ Database initialized successfully!
```

### 6. Update main.py (Optional - Gradual Migration)

You can migrate gradually:

**Option A: Replace completely**
Replace this line in `main.py`:
```python
from database import init_database, cache_flight, cache_hotel
```

With:
```python
from supabase_db import init_database, cache_flight, cache_hotel
```

**Option B: Use both databases (for testing)**
```python
# Keep SQLite for local testing
from database import init_database as init_sqlite_db
# Add Supabase for production
from supabase_db import init_database as init_supabase_db

# In your initialization code:
if os.getenv('USE_SUPABASE', 'false').lower() == 'true':
    init_supabase_db()
else:
    init_sqlite_db()
```

## Verification

### Test Connection

Create a test script `test_supabase.py`:

```python
from supabase_db import get_db_connection

try:
    conn = get_db_connection()
    print("✅ Connection successful!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version['version']}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:
```powershell
python test_supabase.py
```

### Check Tables in Supabase Dashboard

1. Go to Supabase dashboard
2. Click on **Table Editor** in the sidebar
3. You should see:
   - `flights`
   - `hotels`
   - `min_prices`
   - `api_cache`

## Data Migration (Optional)

If you have existing SQLite data you want to migrate:

```python
# migrate_data.py
import sqlite3
from supabase_db import cache_flight, cache_hotel

# Connect to old SQLite database
sqlite_conn = sqlite3.connect('travel_planner.db')
cursor = sqlite_conn.cursor()

# Migrate flights
cursor.execute("SELECT origin, destination, price, date, airline FROM flights")
for row in cursor.fetchall():
    cache_flight(*row)
    print(f"Migrated flight: {row[0]} -> {row[1]}")

# Migrate hotels
cursor.execute("SELECT name, location, price_per_night, rating FROM hotels")
for row in cursor.fetchall():
    cache_hotel(*row)
    print(f"Migrated hotel: {row[0]}")

sqlite_conn.close()
print("✅ Migration complete!")
```

## Troubleshooting

### Connection Errors

**Error**: `OperationalError: could not connect to server`

- Check your DATABASE_URL is correct
- Verify the password doesn't contain special characters (URL encode if needed)
- Check if Supabase project is active (not paused)

**Error**: `NameError: name 'psycopg2' is not defined`

- Install the driver: `pip install psycopg2-binary`

**Error**: `SSL connection error`

- Add `?sslmode=require` to your DATABASE_URL:
  ```
  DATABASE_URL=postgresql://postgres:password@host:5432/postgres?sslmode=require
  ```

### Performance Tips

1. **Use connection pooling** (for production):
   ```python
   from psycopg2 import pool
   connection_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)
   ```

2. **Add more indexes** if queries are slow:
   ```sql
   CREATE INDEX idx_hotels_location ON hotels(location);
   ```

3. **Monitor usage** in Supabase dashboard under **Database** > **Usage**

## Cost Considerations

### Free Tier Limits
- 500 MB database space
- 2 GB data transfer/month
- Unlimited API requests
- 7 days of log retention

### When to Upgrade
- If you exceed 500MB storage
- If you need more than 2GB data transfer
- If you want longer log retention

## Security Best Practices

1. ✅ **Never commit** `.env` file (already in `.gitignore`)
2. ✅ **Use Row Level Security** (RLS) in Supabase:
   ```sql
   ALTER TABLE flights ENABLE ROW LEVEL SECURITY;
   ```
3. ✅ **Rotate database password** periodically
4. ✅ **Use environment-specific databases** (dev/staging/prod)

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

## Rollback Plan

If you need to rollback to SQLite:

1. Keep the old `database.py` file
2. Change imports in `main.py` back to `from database import ...`
3. Your SQLite file `travel_planner.db` is still there

## Support

If you encounter issues:

1. Check Supabase project logs in dashboard
2. Verify all environment variables are set correctly
3. Test connection with the test script above
4. Check Supabase status page: [status.supabase.com](https://status.supabase.com)
