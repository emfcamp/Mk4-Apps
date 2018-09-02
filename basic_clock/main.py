"""An NTP time app"""
___name___         = "NTP time"
___license___      = "MIT"
___dependencies___ = ["ntp", "wifi", "app"]
___categories___   = ["EMF"]

# borrowed from https://github.com/micropython/micropython/blob/master/esp8266/scripts/ntptime.py

import ugfx, ntp, wifi, utime, machine, app
from tilda import Buttons
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
count = 0
last = None
while 1:
    now = rtc.now()[:6]
    year = now[0]
    month = now[1]
    day = now[2]
    hour = now[3]
    minute = now[4]
    second = now[5]
    if now != last:
        last = now
        ugfx.clear()
        ugfx.text(5, 5, "current time", ugfx.BLACK)
        time_str = "%02i:%02i:%02i %i/%i/%4i" % (hour, minute, second, day, month, year)
        ugfx.text(5, 20, time_str, ugfx.BLACK)

    if Buttons.is_pressed(Buttons.BTN_A) or Buttons.is_pressed(Buttons.BTN_B) or Buttons.is_pressed(Buttons.BTN_Menu):
        break
    utime.sleep_ms(10)
ugfx.clear()
app.restart_to_default()
