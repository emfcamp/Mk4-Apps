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
ugfx.orientation(270)
while 1:
    ugfx.text(5, 5, "current time", ugfx.BLACK)
    year = rtc.now()[0]
    month = rtc.now()[1]
    day = rtc.now()[2]
    hour = rtc.now()[3]
    minute = rtc.now()[4]
    second = rtc.now()[5]
    time_str = "%02i:%02i:%02i %i/%i/%4i" % (hour, minute, second, day, month, year)
    ugfx.text(5, 20, time_str, ugfx.BLACK)
    utime.sleep(1)
    ugfx.clear()
