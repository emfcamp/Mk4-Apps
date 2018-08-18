"""Tests for http"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "sleep"]

import unittest, sleep

class TestSleep(unittest.TestCase):

    def test_sleep(self):
        sleep.sleep_ms(100)

if __name__ == '__main__':
    unittest.main()
