"""Tests for wifi"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "wifi"]

import unittest, wifi, ugfx
from machine import Pin

class TestWifi(unittest.TestCase):

    def setUpClass(self):
        ugfx.init()
        Pin(Pin.PWM_LCD_BLIGHT).on()

    def tearDownClass(self):
        Pin(Pin.PWM_LCD_BLIGHT).off()

    def test_connect(self):
        wifi.connect()
        self.assertTrue(wifi.is_connected(show_wait_message=True))

if __name__ == '__main__':
    unittest.main()
