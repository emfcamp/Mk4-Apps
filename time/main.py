"""An NTP time app"""
___name___         = "NTP time"
___license___      = "MIT"
___dependencies___ = ["ntp", "wifi"]
___categories___   = ["EMF"]

# borrowed from https://github.com/micropython/micropython/blob/master/esp8266/scripts/ntptime.py

import ugfx, ntp, wifi
# initialize screen
ugfx.init()
ugfx.clear()

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600

host = "pool.ntp.org"

# set the RTC using time from ntp
# print out RTC datetime

wifi.nic()
while
ugfx.text(5, 5, repr(ntp.get_NTP_time()), ugfx.BLACK)
