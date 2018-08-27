"""Tests for ntp"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "ntp", "wifi"]

import unittest, wifi, ntp, machine

class TestWifi(unittest.TestCase):

    def setUpClass(self):
        wifi.connect()

    def test_get_time(self):
        t = ntp.get_NTP_time()
        self.assertTrue(t > 588699276)
        self.assertTrue(t < 1851003302) # 27 August 2028

    def test_set_time(self):
        ntp.set_NTP_time()
        rtc = machine.RTC()
        self.assertTrue(rtc.now()[0] >= 2018)
        self.assertTrue(rtc.now()[0] <= 2028)

if __name__ == '__main__':
    unittest.main()
