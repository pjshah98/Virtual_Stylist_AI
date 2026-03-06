import unittest

from app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_presets(self):
        res = self.client.get("/api/presets")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) > 0)

    def test_recommend(self):
        res = self.client.post(
            "/api/recommend",
            json={
                "top": "Any",
                "bottom": "Any",
                "shoes": "Any",
                "colors": ["Blue"],
                "style": "Streetwear",
                "season": "Fall",
                "limit": 5,
                "seed": 123,
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("outfits", data)
        self.assertEqual(len(data["outfits"]), 5)


if __name__ == "__main__":
    unittest.main()

