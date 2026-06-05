import unittest
import os
import tempfile

# Ensure travel_api uses an isolated cache.db for this test module.
os.environ.setdefault("CACHE_DIR", tempfile.mkdtemp(prefix="travel_planner_test_cache_"))

import travel_api


class TestMinPriceCaching(unittest.TestCase):
    def setUp(self):
        # Clear sqlite cache between tests
        try:
            os.remove(os.path.join(os.environ["CACHE_DIR"], "cache.db"))
        except Exception:
            pass

    def test_min_price_is_cached(self):
        call_count = {"count": 0}

        def fake_search_hotels(city_name, check_in, check_out, adults=1):
            call_count["count"] += 1
            return ([
                {"price": 1500, "currency": "INR"},
                {"price": 2200, "currency": "INR"},
            ], "ai_synthesized")

        orig = travel_api.search_hotels
        travel_api.search_hotels = fake_search_hotels
        try:
            first = travel_api.get_min_hotel_price("Paris")
            initial_calls = call_count["count"]
            second = travel_api.get_min_hotel_price("Paris")
        finally:
            travel_api.search_hotels = orig

        self.assertEqual(first, 1500)
        self.assertEqual(second, 1500)
        # Should not invoke the fetcher again after the first computation
        self.assertEqual(call_count["count"], initial_calls)

    def test_min_price_handles_no_results(self):
        def empty_search_hotels(city_name, check_in, check_out, adults=1):
            return ([], "ai_synthesized")

        orig = travel_api.search_hotels
        travel_api.search_hotels = empty_search_hotels
        try:
            price = travel_api.get_min_hotel_price("Nowhere")
        finally:
            travel_api.search_hotels = orig
        self.assertIsNone(price)


if __name__ == "__main__":
    unittest.main()
