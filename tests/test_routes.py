import unittest
from app import create_app

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_landing_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_stylist_route(self):
        response = self.client.get("/stylist")
        self.assertEqual(response.status_code, 200)

    def test_api_recommendations(self):
        response = self.client.post(
            "/api/recommendations",
            json={"top": "Any", "bottom": "Any", "shoes": "Any", "colors": ["Black"], "limit": 3},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("outfits", payload)
        self.assertTrue(len(payload["outfits"]) > 0)


if __name__ == "__main__":
    unittest.main()
