"""Default homescreen

This is the default homescreen for the Tilda Mk4.
It gets automatically installed when a badge is
newly activated or reset.
"""

___name___         = "Homescreen (Default)"
___license___      = "GPL"
___categories___   = ["homescreen"]
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

# name
if name():
    #ugfx.set_default_font(ugfx.FONT_NAME)
    ugfx.Label(0, 60, ugfx.width(), 40, name()) # , justification=ugfx.Label.CENTERTOP
else:
    #ugfx.set_default_font(ugfx.FONT_MEDIUM)
    ugfx.Label(0, 60, ugfx.width(), 40, "Set your name in the settings app") # , justification=ugfx.Label.CENTERTOP

# info
ugfx.Label(0, 200, ugfx.width(), 40, "Press MENU") # , justification=ugfx.Label.CENTERTOP

#ugfx.set_default_font(ugfx.FONT_MEDIUM)
status = ugfx.Label(0, 130, ugfx.width(), 40, "") # , justification=ugfx.Label.CENTERTOP

# update loop
while True:
    status.text("wifi: %s%%\nbattery: %s%%" % (int(wifi_strength() * 100), int(battery() * 100)))
    sleep_or_exit(0.5)


