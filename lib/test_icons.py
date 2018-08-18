"""Tests for icons lib"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "icons"]

import unittest, ugfx, time
from icons import *

class TestIcons(unittest.TestCase):

    # incomplete!
    # todo: fix me

    def setUp(self):
        ugfx.init()
        ugfx.clear()

#    def test_icon(self):
#        icon = Icon(44, 40, "Badge Store with", "badge_store/icon.gif")
#        icon.show()
#
#        for s in [True, False, True]:
#            icon.selected = s
#            time.sleep(0.1)
#
#        icon.__del__()
#
#    def test_icon_grid(self):
#        items = []
#        for i in range(50):
#            items.append({
#                "title": "App %s" % i
#            })
#        icon_grid = IconGrid(5, 5, items, None)



if __name__ == '__main__':
    unittest.main()
