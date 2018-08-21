"""Tests for hall effect sensor"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "hall_effect"]

import unittest, hall_effect, speaker

class TestHallEffect(unittest.TestCase):

    def test_hall(self):
        flux = hall_effect.get_flux()
        self.assertTrue(flux > 0)
        self.assertTrue(flux < 4000)

if __name__ == '__main__':
    unittest.main()
