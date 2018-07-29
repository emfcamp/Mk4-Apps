"""Tests for metadata_reader"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "metadata_reader"]
___foo___          = "bar"
___flag___         = True
___list___         = ["a", "b", "c"]

import unittest
from metadata_reader import read_metadata

class TestMetadataReader(unittest.TestCase):
    def test_reader(self):
        with open("lib/test_metadata_reader.py", "rt") as file:
            data = read_metadata(file)
            self.assertIn("Tests for", data["doc"])
            self.assertEqual(data["foo"], "bar")
            self.assertEqual(data["flag"], True)
            self.assertEqual(data["list"], ["a", "b", "c"])


if __name__ == '__main__':
    unittest.main()
