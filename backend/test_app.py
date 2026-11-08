import unittest

from app import MAX_WORK_UNITS, app


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_demo_work_returns_checksum(self):
        response = self.client.get("/api/demo/work?units=4")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"units": 4, "checksum": 14})

    def test_demo_work_rejects_invalid_or_unbounded_units(self):
        invalid = self.client.get("/api/demo/work?units=many")
        too_large = self.client.get(f"/api/demo/work?units={MAX_WORK_UNITS + 1}")

        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(too_large.status_code, 400)

    def test_metrics_endpoint_is_available(self):
        self.client.get("/healthz")
        response = self.client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertIn("app_http_requests_total", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
