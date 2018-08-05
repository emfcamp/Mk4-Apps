"""Tests for random lib"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "random"]

import unittest
from random import *

class TestRandom(unittest.TestCase):

    def test_rand(self):
        for i in range(1, 100):
            r = rand()
            self.assertTrue(r>0)
            self.assertTrue(r<256)



if __name__ == '__main__':
    unittest.main()
