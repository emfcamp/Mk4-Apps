"""Tests for app lib

Very limited at the moment since we can't test the main input dialogs"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "dialogs", "sleep", "ugfx_helper"]

import unittest, ugfx, ugfx_helper
from machine import Pin
from dialogs import *
from sleep import *

class TestDialogs(unittest.TestCase):

    def setUpClass(self):
        ugfx_helper.init()

    def tearDownClass(self):
        ugfx_helper.deinit()

    def test_waiting(self):
        count_max = 3
        with WaitingMessage("Testing...", "Foo") as c:
            for i in range(1, count_max):
                c.text = "%d/%d" % (i, count_max)

        print("done")

    def test_text(self):
        prompt_text("description")

    def test_option(self):
        print(prompt_option(["foo", "bar", "baz"]))



if __name__ == '__main__':
    unittest.main()
