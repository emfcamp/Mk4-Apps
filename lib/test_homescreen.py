"""Tests for hall effect sensor"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "homescreen", "database"]

import unittest, homescreen, database

class TestHomescreen(unittest.TestCase):

    def test_name(self):
        o = database.get("homescreen.name")
        database.delete("homescreen.name")
        self.assertEqual(homescreen.name("default"), "default")
        database.set("homescreen.name", "foo")
        self.assertEqual(homescreen.name("default"), "foo")
        database.set("homescreen.name", o)

    def test_time(self):
        self.assertIn(len(homescreen.time_as_string()), [4, 5])
        self.assertIn(len(homescreen.time_as_string(True)), [7, 8])

    def test_wifi_strength(self):
        # test that it doesn't throw an exception
        homescreen.wifi_strength()

if __name__ == '__main__':
    unittest.main()
