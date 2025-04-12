import unittest

from main import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_valid_h1(self):
        markdown = "# Valid Title"
        self.assertEqual(extract_title(markdown), "Valid Title")

    def test_no_h1_raises_exception(self):
        markdown = "This is not a header"
        with self.assertRaises(Exception):
            extract_title(markdown)

    def test_whitespace_around_h1(self):
        markdown = "   #   Spaced Title   "
        self.assertEqual(extract_title(markdown), "Spaced Title")
