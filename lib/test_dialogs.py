"""Tests for app lib

Very limited at the moment since we can't test the main input dialogs"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "dialogs", "sleep"]

import unittest, ugfx
from machine import Pin
from dialogs import *
from sleep import *

class TestDialogs(unittest.TestCase):

    def setUpClass(self):
        ugfx.init()
        Pin(Pin.PWM_LCD_BLIGHT).on()

    def tearDownClass(self):
        Pin(Pin.PWM_LCD_BLIGHT).off()

    def test_app_object(self):
        count_max = 10
        with WaitingMessage("Testing...", "Foo") as c:
            for i in range(1, count_max):
                sleep_ms(100)
                c.text = "%d/%d" % (i, count_max)

        print("done")



if __name__ == '__main__':
    unittest.main()
