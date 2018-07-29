"""Tests for app lib"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "ospath"]

import unittest
from ospath import *

class TestOsPath(unittest.TestCase):

    # todo: write more tests!

    def test_isdir(self):
        self.assertTrue(isdir("lib"))
        self.assertFalse(isdir("lib/ospath.py"))
        self.assertFalse(isdir("foo/bar/zzz"))

    def test_isfile(self):
        self.assertFalse(isfile("lib"))
        self.assertTrue(isfile("lib/ospath.py"))
        self.assertFalse(isfile("foo/bar/zzz"))

    def test_exists(self):
        self.assertTrue(exists("lib"))
        self.assertTrue(exists("lib/ospath.py"))
        self.assertFalse(exists("foo/bar/zzz"))

if __name__ == '__main__':
    unittest.main()
