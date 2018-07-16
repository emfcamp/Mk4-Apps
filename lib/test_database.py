"""This app's purpose is to run a series of tests against library code

Once successful it displays and prints 'ok' on the screen.

Please make sure that all tests pass before sending a PR. You can easily
do this by running "tilda_tools test". Thank you for keeping all the
tests green! *face-throwing-a-kiss-emoji*
"""

___license___      = "MIT"
___dependencies___ = ["unittest", "database"]

import database, unittest

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.filename = "test/tmp.testdb.json"
        self.database = database.Database(filename = self.filename)
        self._remove_test_db()

    def tearDown(self):
        self._remove_test_db();

    def test_convenience_get_default(self):
        self.assertEqual(
            database.get("does_not_exist", "default_value", filename=self.filename),
            "default_value"
        )

    def test_convenience_set_and_get(self):
        database.set("foo", "bar", filename=self.filename)
        self.assertEqual(database.get("foo", filename=self.filename), "bar")

    def test_convenience_delete(self):
        database.set("foo", "bar", filename=self.filename)
        database.delete("foo", filename=self.filename)
        self.assertEqual(database.get("foo", filename=self.filename), None)

    def test_get_default(self):
        self.assertEqual(
            self.database.get("does_not_exist", "default_value"),
            "default_value"
        )

    def test_set_and_get(self):
        self.database.set("foo", "bar")
        self.assertEqual(self.database.get("foo"), "bar")

    def test_delete(self):
        self.database.set("foo", "bar")
        self.database.delete("foo")
        self.assertEqual(self.database.get("foo"), None)

    def _remove_test_db(self):
        try:
            os.remove(self.filename)
        except Exception as e:
            pass

if __name__ == "__main__":
    TestDatabase().run_standalone()
