"""Base libarary for test cases"""

___license___ = "MIT"

import sys

class SkipTest(Exception):
    """Indicates a test has been skipped"""

class FailTest(Exception):
    """Inidcates a failing test"""
    def __init__(self, message=None):
        self.message = message

class TestCase(object):
    def run(self):
        test_class = type(self).__name__
        self.setUpClass()
        self.count_pass = 0
        self.count_fail = 0
        self.count_skip = 0
        for method in dir(self):
            if not method.startswith("test"):
                continue
            try:
                self.setUp()
                getattr(self, method)()
                self.tearDown()
                print("%s.%s [PASS]" % (test_class, method))
                self.count_pass += 1
            except SkipTest as e:
                print("%s.%s [SKIP]" % (test_class, method))
                self.count_skip += 1
            except FailTest as e:
                print("%s.%s [FAIL]" % (test_class, method))
                print(e.message + "\n")
                self.count_fail += 1
            except Exception as e:
                print("%s.%s [FATAL]" % (test_class, method))
                sys.print_exception(e)
                print("")
                self.count_fail += 1
        self.tearDownClass()
        return self.count_fail == 0

    def run_standalone(self):
        self.run()
        print_result(self.count_pass, self.count_fail, self.count_skip)

    def runSingle(self, function):
        print(self)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def setUpClass(self):
        pass

    def tearDownClass(self):
        pass

    def assertEqual(self, actual, expected):
        if not actual == expected:
            raise FailTest("Expected %s to equal %s" % (actual, expected))

    def assertTrue(self, actual):
        self.assertEqual(actual, True)

    def assertFalse(self, actual):
        self.assertEqual(actual, False)

    def skip(self):
        raise SkipTest()

def print_result(count_pass, count_fail, count_skip):
    print("PASS: %s    FAIL: %s    SKIP: %s" % (count_pass, count_fail, count_skip))
