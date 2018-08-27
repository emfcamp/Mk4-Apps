"""Tests for badge_store lib"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "badge_store", "shared/test/file.txt"]

import unittest, os
from lib.badge_store import *
from ospath import *

class TestBadgeStore(unittest.TestCase):

    def setUpClass(self):
        self.store = BadgeStore(repo="emfcamp/Mk4-Apps", ref="ee144e8")
        self.download_file = "shared/test/download.txt"

    def tearDownClass(self):
        self._remove_download_file()

    def test_get_all_apps(self):
        response = self.store.get_all_apps()
        self.assertEqual(response["System"], ['badge_store', 'launcher', 'settings'])

    def test_categories(self):
        categories = self.store.get_categories()
        self.assertEqual(set(categories), set(["System", "homescreen"]))

    def test_get_apps(self):
        apps = self.store.get_apps("System")
        self.assertEqual(set(apps), set(['badge_store', 'settings', 'launcher']))

    def test_get_app(self):
        response = self.store.get_app("launcher")
        self.assertEqual(response["description"], "Launcher for apps currently installed")

    def test_get_hash(self):
        self.assertEqual(get_hash("shared/test/file.txt"), "182d04f8ee")
        self.assertEqual(get_hash("does/not/exist.txt"), None)

    def test_install_integration(self):
        self._remove_download_file()
        store = BadgeStore(url="http://badge.marekventur.com", repo="emfcamp/Mk4-Apps", ref="dont-delete-test-download-branch")
        for installer in store.install(["launcher"]):
            if installer.path == "shared/test/download.txt":
                installer.download()

        with open(self.download_file, "rt") as response:
            self.assertIn("I'm a download test", response.read())

    def test_bootstrap_integration(self):
        self._remove_download_file()
        store = BadgeStore(url="http://badge.marekventur.com")
        installers = store.bootstrap()
        self.assertTrue(len(installers) > 0)

    def _remove_download_file(self):
        if isdir(self.download_file) or isfile(self.download_file):
            os.remove(self.download_file)


if __name__ == '__main__':
    unittest.main()
