"""Tests for http"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "speaker", "sleep"]

import unittest, speaker, ugfx_helper
from sleep import *

class TestSpeaker(unittest.TestCase):

    def tearDown(self):
        speaker.stop()

    def test_enabled(self):
        self.assertEqual(speaker.enabled(), True)
        speaker.enabled(False)
        self.assertEqual(speaker.enabled(), False)
        speaker.enabled(True)
        self.assertEqual(speaker.enabled(), True)

    def test_beep_and_stop(self):
        for f in range(50, 1000):
            speaker.frequency(f)
            self.assertEqual(speaker.frequency(), f)
            sleep_ms(1)
        speaker.stop()

    def test_note(self):
        for n in ["c", "d", "e", "f", "g", "a", "b", "c5"]:
            speaker.note(n)
            sleep_ms(100)

if __name__ == '__main__':
    unittest.main()
