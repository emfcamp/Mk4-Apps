"""Tests for http"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "sleep"]

import unittest, sleep, time

class TestSleep(unittest.TestCase):

    def test_sleep(self):
        sleep_secs = 5
        time_before = time.ticks_ms()
        time_after = time_before + 1000 * sleep_secs
        sleep.sleep(sleep_secs)
        self.assertTrue(time.ticks_ms() >= time_after)

    def test_sleep_ms(self):
        sleep_ms = 3000
        time_before = time.ticks_ms()
        time_after = time_before + sleep_ms
        sleep.sleep_ms(sleep_ms)
        self.assertTrue(time.ticks_ms() >= time_after)


if __name__ == '__main__':
    unittest.main()
