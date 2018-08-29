"""Tests for ntp"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "ntp", "wifi", "ugfx_helper"]

import unittest, wifi, ntp, machine, ugfx_helper

class TestWifi(unittest.TestCase):

    def setUpClass(self):
        ugfx_helper.init()
        wifi.connect()

    def tearDownClass(self):
        ugfx_helper.deinit()

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
