"""This app's purpose is to run a series of tests against library code

Once successful it displays and prints 'ok' on the screen.

Please make sure that all tests pass before sending a PR. You can easily
do this by running "tilda_tools test". Thank you for keeping all the
tests green! *face-throwing-a-kiss-emoji*
"""

___license___      = "MIT"
___dependencies___ = ["unittest"]

import unittest

class TestHttp(unittest.TestCase):

    def test_foo(self):
        pass


if __name__ == "__main__":
    TestHttp().run_standalone()
