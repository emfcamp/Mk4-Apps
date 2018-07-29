"""Tests for urlencode"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "urlencode"]

import unittest
from urlencode import *

class TestUrlencode(unittest.TestCase):

    def test_urlencode(self):
        self.assertEqual(
            urlencode({"täst":"!£$%(*&^%()", "l": "😃"}),
            "l=%F0%9F%98%83&t%C3%A4st=%21%C2%A3%24%25%28%2A%26%5E%25%28%29"
        )


if __name__ == '__main__':
    unittest.main()
