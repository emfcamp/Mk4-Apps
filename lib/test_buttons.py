"""Tests for icons lib"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "buttons"]

import unittest, ugfx, time
from buttons import *

class TestButtons(unittest.TestCase):

    def test_is_pressed(self):
        self.assertFalse(is_pressed(Buttons.BTN_9))

    def test_is_triggered(self):
        self.assertFalse(is_triggered(Buttons.BTN_9))



if __name__ == '__main__':
    unittest.main()
