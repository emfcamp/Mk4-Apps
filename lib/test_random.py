"""Tests for random lib"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "random"]

import unittest
from random import *

class TestRandom(unittest.TestCase):

    def test_random(self):
        for i in range(1, 100):
            r = random()
            self.assertTrue(r>=0)
            self.assertTrue(r<=1)

    def test_randint(self):
        for i in range(1, 100):
            r = randint(500, 1000)
            self.assertTrue(r>=500)
            self.assertTrue(r<=1000)

    def test_randrange(self):
        for i in range(1, 100):
            r = randrange(10)
            self.assertTrue(r>=0)
            self.assertTrue(r<10)

    def test_shuffle(self):
        for i in range(1, 100):
            r = list(range(1, 10))
            shuffle(r)
            self.assertEqual(sum(r), 45)
            self.assertEqual(set(r), set(range(1, 10)))
            self.assertNotEqual(r, list(range(1, 10)))


if __name__ == '__main__':
    unittest.main()
