import unittest

from app.services.recommendation_service import RecommendationService


class RecommendationTestCase(unittest.TestCase):
    def test_returns_ranked_outfits(self):
        svc = RecommendationService()
        res = svc.recommend(
            {
                "top": "Any",
                "bottom": "Any",
                "shoes": "Any",
                "colors": ["Black"],
                "style": "Minimalist",
                "season": "Winter",
                "limit": 5,
                "seed": 999,
            }
        )
        outfits = res["outfits"]
        self.assertEqual(len(outfits), 5)
        scores = [o["score"] for o in outfits]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()

