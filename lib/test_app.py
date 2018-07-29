"""Tests for app lib"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "app"]

import unittest
from app import *

class TestApp(unittest.TestCase):

    def test_app_object(self):
        app = App("badge_store")
        self.assertEqual(app, App("badge_store"))
        self.assertEqual(app.folder_path, "badge_store")
        self.assertEqual(app.main_path, "badge_store/main.py")
        self.assertEqual(app.loadable, True)
        self.assertIn("TiLDA MK4", app.description)
        self.assertEqual(app.title, "Badge Store")
        self.assertTrue(app.matches_category("System"))
        self.assertFalse(app.matches_category("Something"))
        self.assertTrue(app.attributes["bootstrapped"], True)
        self.assertTrue(app.get_attribute("bootstrapped"), True)
        self.assertTrue(app.get_attribute("foobar", "default"), "default")

    def test_app_object_with_non_existent_app(self):
        app = App("asdfghj")
        self.assertEqual(app.folder_path, "asdfghj")
        self.assertEqual(app.loadable, False)

        with self.assertRaises(Exception) as context:
            app.title
        self.assertIn("File asdfghj/main.py not found in on badge", str(context.exception))

    def test_get_categories(self):
        categories = get_categories()
        self.assertIn("System", categories)

    def test_get_apps(self):
        apps = get_apps()
        self.assertIn(App("badge_store"), apps)


if __name__ == '__main__':
    unittest.main()
