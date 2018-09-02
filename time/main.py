"""An NTP time app"""
___name___         = "NTP time"
___license___      = "MIT"
___dependencies___ = ["ntp", "wifi"]
___categories___   = ["EMF"]

# borrowed from https://github.com/micropython/micropython/blob/master/esp8266/scripts/ntptime.py

import ugfx, ntp, wifi, sleep
# initialize screen
ugfx.init()
ugfx.clear()



# set the RTC using time from ntp
# print out RTC datetime

if not wifi.is_connected():
    wifi.connect(show_wait_message=True)
else:
    ntp.set_NTP_time()
    ugfx.text(5, 5, repr(ntp.get_NTP_time()), ugfx.BLACK)
