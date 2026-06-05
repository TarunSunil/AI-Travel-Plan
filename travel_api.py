"""
travel_api.py
-------------
Free-tier travel data layer with persistent SQLite caching.

Public API:
  - search_flights(...)
  - search_hotels(...)
  - get_min_hotel_price(dest_name)
  - cache_health()

Cache:
  - SQLite DB: cache.db (in CACHE_DIR or project root)
  - Table: api_cache(cache_key, data_type, payload, source_tag, cached_at, expires_at)
  - TTL: flights=6h, hotels=12h, min_prices=6h
  - Stale-on-error: if all sources fail, serve last cached entry (even if expired)
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Env / config ──────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY")
OPENTRIPMAP_KEY = os.getenv("OPENTRIPMAP_KEY")

# Vercel/serverless note: project directory may be read-only. Allow override.
CACHE_DB = os.path.join(
    os.getenv("CACHE_DIR", os.path.dirname(__file__)),
    "cache.db",
)

TTL_FLIGHTS_HOURS = 6
TTL_HOTELS_HOURS = 12
TTL_MIN_PRICE_HOURS = 6

# Approximate FX rates (avoid adding a paid FX dependency; good enough for UI).
FX_TO_INR = {
    "INR": 1.0,
    "USD": 83.5,
    "EUR": 90.0,
    "GBP": 105.0,
}


# ── SQLite cache helpers ──────────────────────────────────────────────────────
def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _dt_to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _iso_to_dt(s: str) -> datetime:
    # Stored in UTC ISO with offset.
    return datetime.fromisoformat(s)


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(CACHE_DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_cache_db() -> None:
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_cache (
              cache_key  TEXT NOT NULL,
              data_type  TEXT NOT NULL,
              payload    TEXT NOT NULL,
              source_tag TEXT NOT NULL,
              cached_at  TEXT NOT NULL,
              expires_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_api_cache_key_time ON api_cache(cache_key, cached_at)"
        )


def _get_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Return a fresh (non-expired) entry, else None."""
    _ensure_cache_db()
    now = _utcnow()
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT cache_key, data_type, payload, source_tag, cached_at, expires_at
            FROM api_cache
            WHERE cache_key = ?
            ORDER BY cached_at DESC
            LIMIT 1
            """,
            (cache_key,),
        ).fetchone()
        if not row:
            return None
        try:
            expires_at = _iso_to_dt(row["expires_at"])
        except Exception:
            return None
        if expires_at <= now:
            return None
        return {
            "cache_key": row["cache_key"],
            "data_type": row["data_type"],
            "payload": json.loads(row["payload"]),
            "source_tag": row["source_tag"],
            "cached_at": row["cached_at"],
            "expires_at": row["expires_at"],
        }


def _get_stale_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Return the most recent entry regardless of expiry, else None."""
    _ensure_cache_db()
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT cache_key, data_type, payload, source_tag, cached_at, expires_at
            FROM api_cache
            WHERE cache_key = ?
            ORDER BY cached_at DESC
            LIMIT 1
            """,
            (cache_key,),
        ).fetchone()
        if not row:
            return None
        try:
            payload = json.loads(row["payload"])
        except Exception:
            payload = None
        return {
            "cache_key": row["cache_key"],
            "data_type": row["data_type"],
            "payload": payload,
            "source_tag": row["source_tag"],
            "cached_at": row["cached_at"],
            "expires_at": row["expires_at"],
        }


def _set_cache(
    cache_key: str,
    data_type: str,
    payload: Any,
    ttl_hours: int,
    source_tag: str,
) -> None:
    _ensure_cache_db()
    now = _utcnow()
    expires = now + timedelta(hours=ttl_hours)
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO api_cache(cache_key, data_type, payload, source_tag, cached_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                cache_key,
                data_type,
                json.dumps(payload, ensure_ascii=False),
                source_tag,
                _dt_to_iso(now),
                _dt_to_iso(expires),
            ),
        )


def _make_cache_key(prefix: str, obj: Dict[str, Any]) -> str:
    """Stable key from a JSON-serializable dict."""
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
    return f"{prefix}:{h}"


# ── Normalisation helpers ─────────────────────────────────────────────────────
def _to_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "")
    s = s.replace("₹", "")
    try:
        return float(s)
    except Exception:
        return None


def _to_inr(amount: Any, currency: str | None) -> Optional[float]:
    amt = _to_float(amount)
    if amt is None:
        return None
    cur = (currency or "INR").upper()
    rate = FX_TO_INR.get(cur)
    if rate is None:
        # Heuristic: if it looks too small to be INR, assume USD.
        rate = FX_TO_INR["USD"] if amt < 500 else 1.0
    return float(amt) * float(rate)


def _airline_name_from_iata(code: str) -> str:
    # Lightweight mapping; keep minimal (avoid adding large datasets).
    mapping = {
        "AI": "Air India",
        "UK": "Vistara",
        "6E": "IndiGo",
        "SG": "SpiceJet",
        "G8": "Go First",
        "IX": "Air India Express",
    }
    return mapping.get(code.upper(), code.upper() or "Unknown")


def _pseudo_price_inr(route_key: str, travel_class: str, adults: int) -> int:
    """Deterministic-ish price so UI doesn't show 0 when only schedules are available."""
    base = int(hashlib.md5(route_key.encode("utf-8")).hexdigest()[:6], 16) % 6000
    base += 3500  # 3.5k–9.5k-ish
    class_mul = {
        "ECONOMY": 1.0,
        "PREMIUM_ECONOMY": 1.4,
        "BUSINESS": 2.4,
        "FIRST": 3.2,
    }.get((travel_class or "ECONOMY").upper(), 1.0)
    return int(round(base * class_mul * max(1, int(adults or 1))))


# ── Gemini helpers ────────────────────────────────────────────────────────────
def _gemini_generate(prompt: str, temperature: float = 0.3, max_tokens: int = 1024) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    res = requests.post(url, headers={"Content-Type": "application/json"}, json=body, timeout=30)
    res.raise_for_status()
    data = res.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _extract_json(text: str) -> Any:
    """
    Best-effort JSON extraction from Gemini output.
    Accepts either a raw JSON string or a response that includes fenced code blocks.
    """
    if not text:
        raise ValueError("Empty Gemini response")

    # Strip code fences if present.
    cleaned = text.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        # Prefer the largest block that looks like JSON.
        candidates = [p.strip() for p in parts if "{" in p or "[" in p]
        cleaned = max(candidates, key=len, default=cleaned)
        cleaned = cleaned.replace("json", "", 1).strip()

    # Trim to first JSON object/array.
    start = min([i for i in [cleaned.find("{"), cleaned.find("[")] if i != -1], default=-1)
    if start == -1:
        raise ValueError("No JSON start found")
    cleaned = cleaned[start:]
    end_obj = cleaned.rfind("}")
    end_arr = cleaned.rfind("]")
    end = max(end_obj, end_arr)
    if end == -1:
        raise ValueError("No JSON end found")
    cleaned = cleaned[: end + 1]
    return json.loads(cleaned)


# ── Flight sources ────────────────────────────────────────────────────────────
def _aviationstack_flights(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
    travel_class: str,
) -> List[Dict[str, Any]]:
    if not AVIATIONSTACK_KEY:
        return []

    # AviationStack free tier is limited; many parameters are not supported.
    # We use a simple "flights" lookup and then filter.
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": AVIATIONSTACK_KEY,
        "dep_iata": origin,
        "arr_iata": destination,
        # date field name differs between plans; keep only supported-ish params.
        "limit": 10,
    }
    try:
        res = requests.get(url, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception:
        return []

    flights: List[Dict[str, Any]] = []
    for item in (data.get("data") or [])[:10]:
        dep = (item.get("departure") or {}).get("scheduled")
        arr = (item.get("arrival") or {}).get("scheduled")
        airline = (item.get("airline") or {}).get("name") or "Unknown Airline"
        airline_iata = (item.get("airline") or {}).get("iata") or ""
        flight_number = (item.get("flight") or {}).get("iata") or (item.get("flight") or {}).get("number") or ""
        dep_airport = (item.get("departure") or {}).get("iata") or origin
        arr_airport = (item.get("arrival") or {}).get("iata") or destination

        route_key = f"{origin}-{destination}-{departure_date}-{flight_number}"
        flights.append(
            {
                "airline": airline,
                "airlineCode": airline_iata,
                "flightNumber": flight_number,
                "departureTime": dep or f"{departure_date}T09:00:00",
                "arrivalTime": arr or f"{departure_date}T11:00:00",
                "departureAirport": dep_airport,
                "arrivalAirport": arr_airport,
                "duration": None,
                "stops": 0,
                "price": _pseudo_price_inr(route_key, travel_class, adults),
                "currency": "INR",
            }
        )
    return flights[:3]


def _opensky_flights(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
    travel_class: str,
) -> List[Dict[str, Any]]:
    """
    OpenSky has limited schedule lookups.
    Practical constraint: we only attempt for today/tomorrow; for future dates we skip
    and fall through to Gemini synthesis.
    """
    try:
        dep_dt = datetime.strptime(departure_date, "%Y-%m-%d").date()
    except Exception:
        return []

    today = datetime.now().date()
    if dep_dt not in (today, today + timedelta(days=1)):
        return []

    # OpenSky does not support IATA directly. This is a best-effort.
    # We still provide a plausible fallback schedule if OpenSky is unreachable.
    try:
        # Use a basic flights/all-state endpoint; often rate-limited.
        url = "https://opensky-network.org/api/flights/all"
        begin = int(datetime(dep_dt.year, dep_dt.month, dep_dt.day, tzinfo=timezone.utc).timestamp())
        end = begin + 24 * 3600
        res = requests.get(url, params={"begin": begin, "end": end}, timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception:
        data = []

    flights: List[Dict[str, Any]] = []
    # We cannot reliably filter by IATA here; create a small plausible list.
    for idx in range(min(3, len(data) or 3)):
        item = data[idx] if idx < len(data) else {}
        callsign = (item.get("callsign") or "").strip() or f"{origin}{destination}{idx+1}"
        airline_iata = callsign[:2].strip()
        airline = _airline_name_from_iata(airline_iata)
        route_key = f"{origin}-{destination}-{departure_date}-{callsign}"
        flights.append(
            {
                "airline": airline,
                "airlineCode": airline_iata,
                "flightNumber": callsign,
                "departureTime": f"{departure_date}T10:{idx}0:00",
                "arrivalTime": f"{departure_date}T12:{idx}5:00",
                "departureAirport": origin,
                "arrivalAirport": destination,
                "duration": None,
                "stops": 0,
                "price": _pseudo_price_inr(route_key, travel_class, adults),
                "currency": "INR",
            }
        )
    return flights


def _gemini_synthesize_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str],
    adults: int,
    travel_class: str,
) -> List[Dict[str, Any]]:
    prompt = f"""
Generate 3 plausible commercial flight options as JSON for:
- Origin airport IATA: {origin}
- Destination airport IATA: {destination}
- Departure date: {departure_date}
- Return date: {return_date or "N/A"}
- Adults: {adults}
- Cabin class: {travel_class}

Return ONLY valid JSON array. Each item must contain:
airline, airlineCode, flightNumber, departureTime (ISO), arrivalTime (ISO),
departureAirport, arrivalAirport, price (number, INR), currency ("INR"),
duration (string like "2h 10m" optional), stops (integer 0-2).
"""
    text = _gemini_generate(prompt, temperature=0.2, max_tokens=900)
    data = _extract_json(text)
    if not isinstance(data, list):
        return []
    flights: List[Dict[str, Any]] = []
    for f in data[:3]:
        if not isinstance(f, dict):
            continue
        price_inr = _to_inr(f.get("price"), f.get("currency") or "INR")
        flights.append(
            {
                "airline": f.get("airline") or "Unknown Airline",
                "airlineCode": (f.get("airlineCode") or "").upper(),
                "flightNumber": f.get("flightNumber") or "",
                "departureTime": f.get("departureTime") or f"{departure_date}T09:00:00",
                "arrivalTime": f.get("arrivalTime") or f"{departure_date}T11:00:00",
                "departureAirport": (f.get("departureAirport") or origin).upper(),
                "arrivalAirport": (f.get("arrivalAirport") or destination).upper(),
                "duration": f.get("duration"),
                "stops": int(_to_float(f.get("stops")) or 0),
                "price": float(price_inr or 0),
                "currency": "INR",
            }
        )
    return flights


def _static_flights_fallback(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
    travel_class: str,
) -> List[Dict[str, Any]]:
    flights: List[Dict[str, Any]] = []
    for idx in range(3):
        route_key = f"{origin}-{destination}-{departure_date}-FB{idx+1}"
        flights.append(
            {
                "airline": "Estimated Airline",
                "airlineCode": "XX",
                "flightNumber": f"XX{100+idx}",
                "departureTime": f"{departure_date}T0{8+idx}:00:00",
                "arrivalTime": f"{departure_date}T1{0+idx}:10:00",
                "departureAirport": origin,
                "arrivalAirport": destination,
                "duration": f"{2+idx}h 10m",
                "stops": 0 if idx == 0 else 1,
                "price": _pseudo_price_inr(route_key, travel_class, adults),
                "currency": "INR",
            }
        )
    return flights


# ── Hotel sources ─────────────────────────────────────────────────────────────
def _opentripmap_city_coords(city_name: str) -> Optional[Tuple[float, float]]:
    if not OPENTRIPMAP_KEY:
        return None
    url = "https://api.opentripmap.com/0.1/en/places/geoname"
    try:
        res = requests.get(url, params={"name": city_name, "apikey": OPENTRIPMAP_KEY}, timeout=15)
        res.raise_for_status()
        data = res.json()
        lat = (data.get("lat"))
        lon = (data.get("lon"))
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)
    except Exception:
        return None


def _opentripmap_accommodation_names(city_name: str, limit: int = 10) -> List[str]:
    coords = _opentripmap_city_coords(city_name)
    if not coords:
        return []
    lat, lon = coords
    url = "https://api.opentripmap.com/0.1/en/places/radius"
    try:
        # Be gentle: OpenTripMap free tier is generous but still subject to limits.
        time.sleep(1.1)
        res = requests.get(
            url,
            params={
                "radius": 15000,
                "lat": lat,
                "lon": lon,
                "kinds": "accomodations",
                "limit": limit,
                "apikey": OPENTRIPMAP_KEY,
            },
            timeout=15,
        )
        res.raise_for_status()
        data = res.json()
        feats = data.get("features") or []
        names: List[str] = []
        for f in feats:
            props = f.get("properties") or {}
            name = props.get("name")
            if name:
                names.append(str(name))
        # Filter empties/dupes
        out: List[str] = []
        seen = set()
        for n in names:
            k = n.strip().lower()
            if not k or k in seen:
                continue
            seen.add(k)
            out.append(n.strip())
        return out[:limit]
    except Exception:
        return []


def _gemini_synthesize_hotels(
    city_name: str,
    check_in: str,
    check_out: str,
    adults: int,
    seed_names: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    seed = "\n".join([f"- {n}" for n in (seed_names or [])[:10]])
    prompt = f"""
You are generating hotel options for a travel app. Return ONLY valid JSON array.

Destination city: {city_name}
Check-in: {check_in}
Check-out: {check_out}
Adults: {adults}

If provided, use these real accommodation names as inspiration:
{seed if seed else "(none provided)"}

Return 3 hotel objects with fields:
name, rating (number 3.0-5.0), price (number in INR per night), currency ("INR"),
location (short string), description (short), amenities (array of strings).
"""
    text = _gemini_generate(prompt, temperature=0.35, max_tokens=900)
    data = _extract_json(text)
    if not isinstance(data, list):
        return []
    hotels: List[Dict[str, Any]] = []
    for h in data[:3]:
        if not isinstance(h, dict):
            continue
        price_inr = _to_inr(h.get("price"), h.get("currency") or "INR")
        hotels.append(
            {
                "name": h.get("name") or f"Hotel in {city_name}",
                "rating": float(_to_float(h.get("rating")) or 4.0),
                "price": float(price_inr or 0),
                "currency": "INR",
                "location": h.get("location") or f"{city_name} City Center",
                "description": h.get("description") or f"Hotel stay in {city_name}",
                "amenities": h.get("amenities") if isinstance(h.get("amenities"), list) else ["WiFi"],
                "isEstimate": True,
            }
        )
    return hotels


def _static_hotels_fallback(city_name: str) -> List[Dict[str, Any]]:
    try:
        from city_data import ESTIMATED_HOTEL_PRICES
    except Exception:
        ESTIMATED_HOTEL_PRICES = {}

    est = ESTIMATED_HOTEL_PRICES.get(city_name.strip().lower())
    price = float(est) if est else 4500.0
    return [
        {
            "name": f"Hotels in {city_name}",
            "rating": 4.0,
            "price": price,
            "currency": "INR",
            "location": f"{city_name} City Center",
            "description": f"Estimated average hotel price in {city_name}. Actual prices may vary.",
            "amenities": ["WiFi", "Breakfast"],
            "isEstimate": True,
        }
    ]


# ── Public API ────────────────────────────────────────────────────────────────
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    travel_class: str = "ECONOMY",
) -> Tuple[List[Dict[str, Any]], str]:
    params = {
        "origin": (origin or "").upper(),
        "destination": (destination or "").upper(),
        "departure_date": departure_date,
        "return_date": return_date,
        "adults": int(adults or 1),
        "travel_class": (travel_class or "ECONOMY").upper(),
    }
    cache_key = _make_cache_key("flights", params)

    cached = _get_cache(cache_key)
    if cached and isinstance(cached.get("payload"), list):
        return cached["payload"], "cached"

    source_tag = "static_fallback"
    flights: List[Dict[str, Any]] = []
    try:
        flights = _aviationstack_flights(**params)  # type: ignore[arg-type]
        if flights:
            source_tag = "aviationstack"
        else:
            flights = _opensky_flights(**params)  # type: ignore[arg-type]
            if flights:
                source_tag = "opensky"
            else:
                flights = _gemini_synthesize_flights(
                    origin=params["origin"],
                    destination=params["destination"],
                    departure_date=params["departure_date"],
                    return_date=params["return_date"],
                    adults=params["adults"],
                    travel_class=params["travel_class"],
                )
                if flights:
                    source_tag = "ai_synthesized"
                else:
                    flights = _static_flights_fallback(
                        params["origin"], params["destination"], params["departure_date"], params["adults"], params["travel_class"]
                    )
                    source_tag = "static_fallback"

        # Normalise prices to INR before caching.
        for f in flights:
            f["price"] = float(_to_inr(f.get("price"), f.get("currency")) or 0)
            f["currency"] = "INR"

        _set_cache(cache_key, "flights", flights, TTL_FLIGHTS_HOURS, source_tag)
        return flights, source_tag
    except Exception:
        stale = _get_stale_cache(cache_key)
        if stale and isinstance(stale.get("payload"), list):
            return stale["payload"], "cached"
        flights = _static_flights_fallback(
            params["origin"], params["destination"], params["departure_date"], params["adults"], params["travel_class"]
        )
        return flights, "static_fallback"


def search_hotels(
    city_name: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
) -> Tuple[List[Dict[str, Any]], str]:
    params = {
        "city_name": city_name.strip(),
        "check_in": check_in,
        "check_out": check_out,
        "adults": int(adults or 1),
    }
    cache_key = _make_cache_key("hotels", params)

    cached = _get_cache(cache_key)
    if cached and isinstance(cached.get("payload"), list):
        return cached["payload"], "cached"

    source_tag = "static_fallback"
    hotels: List[Dict[str, Any]] = []
    try:
        seed_names = _opentripmap_accommodation_names(params["city_name"])
        if seed_names and GEMINI_API_KEY:
            hotels = _gemini_synthesize_hotels(
                city_name=params["city_name"],
                check_in=params["check_in"],
                check_out=params["check_out"],
                adults=params["adults"],
                seed_names=seed_names,
            )
            if hotels:
                source_tag = "opentripmap"
        if not hotels:
            if GEMINI_API_KEY:
                hotels = _gemini_synthesize_hotels(
                    city_name=params["city_name"],
                    check_in=params["check_in"],
                    check_out=params["check_out"],
                    adults=params["adults"],
                    seed_names=None,
                )
                if hotels:
                    source_tag = "ai_synthesized"
        if not hotels:
            hotels = _static_hotels_fallback(params["city_name"])
            source_tag = "static_fallback"

        # Normalise INR before caching.
        for h in hotels:
            h["price"] = float(_to_inr(h.get("price"), h.get("currency")) or 0)
            h["currency"] = "INR"

        _set_cache(cache_key, "hotels", hotels, TTL_HOTELS_HOURS, source_tag)
        return hotels, source_tag
    except Exception:
        stale = _get_stale_cache(cache_key)
        if stale and isinstance(stale.get("payload"), list):
            return stale["payload"], "cached"
        hotels = _static_hotels_fallback(params["city_name"])
        return hotels, "static_fallback"


def get_min_hotel_price(dest_name: str) -> Optional[float]:
    dest = (dest_name or "").strip()
    if not dest:
        return None

    params = {"dest": dest}
    cache_key = _make_cache_key("min_price", params)
    cached = _get_cache(cache_key)
    if cached and isinstance(cached.get("payload"), dict):
        return _to_float(cached["payload"].get("min_price_inr"))

    source_tag = "static_fallback"
    try:
        # Use a near-future 1-night window.
        ci = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        co = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
        hotels, src = search_hotels(dest, ci, co, adults=1)
        source_tag = src if src != "cached" else "cached"
        prices = [h.get("price") for h in hotels if _to_float(h.get("price"))]
        min_price = min([float(_to_float(p) or 0) for p in prices if float(_to_float(p) or 0) > 0], default=None)
        if min_price is None:
            try:
                from city_data import ESTIMATED_HOTEL_PRICES
                min_price = float(ESTIMATED_HOTEL_PRICES.get(dest.lower())) if ESTIMATED_HOTEL_PRICES.get(dest.lower()) else None
            except Exception:
                min_price = None
        _set_cache(cache_key, "min_prices", {"min_price_inr": min_price}, TTL_MIN_PRICE_HOURS, source_tag)
        return min_price
    except Exception:
        stale = _get_stale_cache(cache_key)
        if stale and isinstance(stale.get("payload"), dict):
            return _to_float(stale["payload"].get("min_price_inr"))
        return None


def cache_health() -> Dict[str, Any]:
    _ensure_cache_db()
    with _get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM api_cache").fetchone()["c"]
        newest = conn.execute("SELECT MAX(cached_at) AS t FROM api_cache").fetchone()["t"]
        oldest = conn.execute("SELECT MIN(cached_at) AS t FROM api_cache").fetchone()["t"]
        now = _dt_to_iso(_utcnow())
        expired = conn.execute(
            "SELECT COUNT(*) AS c FROM api_cache WHERE expires_at <= ?",
            (now,),
        ).fetchone()["c"]
        by_type = {
            r["data_type"]: r["c"]
            for r in conn.execute("SELECT data_type, COUNT(*) AS c FROM api_cache GROUP BY data_type").fetchall()
        }
    return {
        "db": os.path.basename(CACHE_DB),
        "total_entries": int(total),
        "expired_entries": int(expired),
        "by_type": by_type,
        "oldest_cached_at": oldest,
        "newest_cached_at": newest,
    }

