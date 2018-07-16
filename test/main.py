"""This app's purpose is to run a series of tests against library code

Once successful it displays and prints 'ok' on the screen.

Please make sure that all tests pass before sending a PR. You can easily
do this by running "tilda_tools test". Thank you for keeping all the
tests green! *face-throwing-a-kiss-emoji*
"""

___license___      = "MIT"
___categories___   = ["Development"]
___name___         = "Integration test app"
___dependencies___ = ["unittest", "test_database", "test_http"]

# Add all tests that need to be run here:
import test_database
import test_http

# run
import sys, unittest

count_pass = 0
count_fail = 0
count_skip = 0
log = ""

for name, module in sys.modules.items():
    if not name.startswith("test"):
        continue
    for element_name in dir(module):
        element = getattr(module, element_name)
        if not isinstance(element, type):
            continue
        if not issubclass(element, unittest.TestCase):
            continue
        test_case = element()
        test_case.run()
        count_pass += test_case.count_pass
        count_fail += test_case.count_fail
        count_skip += test_case.count_skip

unittest.print_result(count_pass, count_fail, count_skip)



