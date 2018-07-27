"""Base libarary for test cases

See https://github.com/python/cpython/blob/master/Lib/unittest/case.py for
some of the code copied here
"""

___license___ = "MIT"

import sys, ugfx

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
        ugfx.clear(0xFFFFFF)
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

    def assertRaises(self, expected_exception, *args, **kwargs):
        context = _AssertRaisesContext(expected_exception, self)
        return context.handle('assertRaises', args, kwargs)

    def assertIn(self, sub, actual):
        if not sub in actual:
            raise FailTest("Expected %s to be in %s" % (sub, actual))

    def skip(self):
        raise SkipTest()

def print_result(count_pass, count_fail, count_skip):
    print("PASS: %s    FAIL: %s    SKIP: %s" % (count_pass, count_fail, count_skip))

###########################################
#### Bits copied straight from cpython ####
###########################################

class _BaseTestCaseContext:

    def __init__(self, test_case):
        self.test_case = test_case

    def _raiseFailure(self, standardMsg):
        msg = self.test_case._formatMessage(self.msg, standardMsg)
        raise self.test_case.failureException(msg)

class _AssertRaisesBaseContext(_BaseTestCaseContext):

    def __init__(self, expected, test_case, expected_regex=None):
        _BaseTestCaseContext.__init__(self, test_case)
        self.expected = expected
        self.test_case = test_case
        if expected_regex is not None:
            expected_regex = re.compile(expected_regex)
        self.expected_regex = expected_regex
        self.obj_name = None
        self.msg = None

    def handle(self, name, args, kwargs):
        """
        If args is empty, assertRaises/Warns is being used as a
        context manager, so check for a 'msg' kwarg and return self.
        If args is not empty, call a callable passing positional and keyword
        arguments.
        """
        try:
            if not _is_subtype(self.expected, self._base_type):
                raise TypeError('%s() arg 1 must be %s' %
                                (name, self._base_type_str))
            if args and args[0] is None:
                warnings.warn("callable is None",
                              DeprecationWarning, 3)
                args = ()
            if not args:
                self.msg = kwargs.pop('msg', None)
                if kwargs:
                    warnings.warn('%r is an invalid keyword argument for '
                                  'this function' % next(iter(kwargs)),
                                  DeprecationWarning, 3)
                return self

            callable_obj, *args = args
            try:
                self.obj_name = callable_obj.__name__
            except AttributeError:
                self.obj_name = str(callable_obj)
            with self:
                callable_obj(*args, **kwargs)
        finally:
            # bpo-23890: manually break a reference cycle
            self = None



class _AssertRaisesContext(_AssertRaisesBaseContext):
    """A context manager used to implement TestCase.assertRaises* methods."""

    _base_type = BaseException
    _base_type_str = 'an exception type or tuple of exception types'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            if self.obj_name:
                self._raiseFailure("{} not raised by {}".format(exc_name,
                                                                self.obj_name))
            else:
                self._raiseFailure("{} not raised".format(exc_name))
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        # store exception
        self.exception = exc_value
        if self.expected_regex is None:
            return True

        expected_regex = self.expected_regex
        if not expected_regex.search(str(exc_value)):
            self._raiseFailure('"{}" does not match "{}"'.format(
                     expected_regex.pattern, str(exc_value)))
        return True

def _is_subtype(expected, basetype):
    if isinstance(expected, tuple):
        return all(_is_subtype(e, basetype) for e in expected)
    return isinstance(expected, type) and issubclass(expected, basetype)
