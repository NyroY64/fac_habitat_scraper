import unittest
from fac_scraper.utils import clean_url

class TestUtils(unittest.TestCase):
    def test_clean_url(self):
        self.assertEqual(clean_url("/test"), "https://www.fac-habitat.com/test")
        self.assertEqual(clean_url("https://www.fac-habitat.com/test"), "https://www.fac-habitat.com/test")
