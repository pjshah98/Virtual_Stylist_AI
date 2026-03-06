import unittest

from app.services.color_service import ColorService


class ColorEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.colors = ColorService()

    def test_complementary_rule(self):
        self.assertIn("Orange", self.colors.get_harmonious_colors("Blue", mode="complementary"))
        self.assertIn("Green", self.colors.get_harmonious_colors("Red", mode="complementary"))
        self.assertIn("Yellow", self.colors.get_harmonious_colors("Purple", mode="complementary"))

    def test_analogous(self):
        palette = self.colors.get_harmonious_colors("Blue", mode="analogous", include_neutrals=False)
        self.assertIn("Blue", palette)
        self.assertTrue(len(palette) >= 2)


if __name__ == "__main__":
    unittest.main()

