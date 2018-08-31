"""Default homescreen

This is the default homescreen for the Tilda Mk4.
It gets automatically installed when a badge is
newly activated or reset.
"""

___name___         = "Homescreen (Default)"
___license___      = "MIT"
___categories___   = ["Homescreens"]
___dependencies___ = ["homescreen"]
___launchable___   = False
___bootstrapped___ = True

import ugfx
from homescreen import *
import time

init()
ugfx.clear()

# title
#ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
ugfx.Label(0, 20, ugfx.width(), 40, "TiLDA Mk4") # , justification=ugfx.Label.CENTERTOP

#ugfx.set_default_font(ugfx.FONT_NAME)
ugfx.Label(0, 60, ugfx.width(), 40, name("Set your name in the settings app")) # , justification=ugfx.Label.CENTERTOP

# info
ugfx.Label(0, 200, ugfx.width(), 40, "Press MENU") # , justification=ugfx.Label.CENTERTOP

#ugfx.set_default_font(ugfx.FONT_MEDIUM)
status = ugfx.Label(0, 130, ugfx.width(), 40, "") # , justification=ugfx.Label.CENTERTOP

# update loop
while True:
    text = "";
    value_wifi_strength = wifi_strength()
    value_battery = battery()
    if value_wifi_strength:
        text += "wifi: %s%%\n" % int(value_wifi_strength)
    if value_battery:
        text += "battery: %s%%\n" % int(value_battery)
    status.text(text)
    sleep_or_exit(0.5)
