"""Tests for wifi"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "wifi", "ugfx_helper"]

import unittest, wifi, ugfx_helper
from machine import Pin

class TestWifi(unittest.TestCase):

    def setUpClass(self):
        ugfx_helper.init()

    def tearDownClass(self):
        ugfx_helper.deinit()

    def test_connect(self):
        wifi.connect(show_wait_message=True)
        self.assertTrue(wifi.is_connected())

if __name__ == '__main__':
    unittest.main()
