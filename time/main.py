"""An NTP time app"""
___name___         = "NTP time"
___license___      = "MIT"
___dependencies___ = ["ntp", "wifi"]
___categories___   = ["EMF"]

# borrowed from https://github.com/micropython/micropython/blob/master/esp8266/scripts/ntptime.py

import ugfx, ntp, wifi, utime, machine
# initialize screen
ugfx.init()
ugfx.clear()



# set the RTC using time from ntp
# print out RTC datetime

if not wifi.is_connected():
    wifi.connect(show_wait_message=True)
ntp.set_NTP_time()
rtc = machine.RTC()
ugfx.text(5, 5, repr(rtc.now()), ugfx.BLACK)
