import unittest
from datetime import datetime

from main import (
    get_min_price_for_destination,
    MIN_PRICE_CACHE,
    MIN_PRICE_CACHE_LOCK,
)


class TestMinPriceCaching(unittest.TestCase):
    def setUp(self):
        with MIN_PRICE_CACHE_LOCK:
            MIN_PRICE_CACHE.clear()

    def test_min_price_is_cached(self):
        call_count = {"count": 0}

        def fake_fetch(city_name, check_in, check_out, adults):
            call_count["count"] += 1
            return [
                {"price": 1500},
                {"price": 2200},
            ]

        first = get_min_price_for_destination("Paris", fetcher=fake_fetch, days=2)
        initial_calls = call_count["count"]
        second = get_min_price_for_destination("Paris", fetcher=fake_fetch, days=2)

        self.assertEqual(first, 1500)
        self.assertEqual(second, 1500)
        # Should not invoke the fetcher again after the first computation
        self.assertEqual(call_count["count"], initial_calls)

    def test_min_price_handles_no_results(self):
        def empty_fetch(city_name, check_in, check_out, adults):
            return []

        price = get_min_price_for_destination("Nowhere", fetcher=empty_fetch, days=1)
        self.assertIsNone(price)


if __name__ == "__main__":
    unittest.main()
