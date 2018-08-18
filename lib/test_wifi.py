"""Tests for wifi"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "wifi"]

import unittest, wifi

class TestWifi(unittest.TestCase):

    def test_connect(self):
        wifi.connect()
        self.assertTrue(wifi.is_connected())

if __name__ == '__main__':
    unittest.main()
