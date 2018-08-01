"""Tests for badge_store lib"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "badge_store", "shared/test/file.txt"]

import unittest
from lib.badge_store import *

class TestBadgeStore(unittest.TestCase):

    def setUpClass(self):
        self.store = BadgeStore(url="http://badge.marekventur.com", repo="emfcamp/Mk4-Apps", ref="ee144e8")

    def test_apps(self):
        response = self.store.get_apps()
        self.assertEqual(response["System"], ['badge_store', 'launcher', 'settings'])

    def test_categories(self):
        categories = self.store.get_categories()
        self.assertEqual(set(categories), set(["System", "homescreen"]))

    def test_app(self):
        response = self.store.get_app("launcher")
        self.assertEqual(response["description"], "Launcher for apps currently installed")

    def test_is_file_up_to_date(self):
        self.assertFalse(self.store._is_file_up_to_date("shared/test/file.txt", "1234567890"))
        self.assertFalse(self.store._is_file_up_to_date("does/not/exist.txt", "1234567890"))
        self.assertTrue(self.store._is_file_up_to_date("shared/test/file.txt", "182d04f8ee"))

    def test_install(self):
        installers = self.store.install(["launcher", "badge_store"])
        self.assertTrue(len(installers) > 0)

if __name__ == '__main__':
    unittest.main()
