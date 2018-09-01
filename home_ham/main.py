"""Amateur Radio homescreen

This is a modified version of the default homescreen that allows you to set a callsign
"""

___name___         = "Amateur Radio Homescreen"
___license___      = "MIT"
___categories___   = ["Homescreens"]
___dependencies___ = ["homescreen", "shared/sponsors.png"]

import ugfx
from homescreen import *
import time
from tilda import Buttons

# We ❤️ our sponsors
init()
ugfx.clear()

# Padding for name
intro_height = 30
name_height = 60
status_height = 20
callsign_height = 50
info_height = 30
logo_path = "home_ham/emf_ham.png"
logo_width = 200

# Maximum length of name before downscaling
max_name = 8

# Background stuff

ugfx.clear(ugfx.html_color(0xffffff))

# Colour stuff
style = ugfx.Style()
style.set_enabled([ugfx.BLACK, ugfx.html_color(0xffffff), ugfx.html_color(0xffffff), ugfx.html_color(0xffffff)])
style.set_background(ugfx.html_color(0xffffff))
ugfx.set_default_style(style)

ugfx.orientation(90)
# Logo stuff
ugfx.display_image(
    int((ugfx.width() - logo_width) / 2),
    30,
    logo_path
)



# Draw for people to see
# Draw introduction
ugfx.set_default_font(ugfx.FONT_TITLE)
# Process name
name_setting = name("Set your name in the settings app")
callsign_setting = callsign("Set your callsign in the settings app")
if len(name_setting) <= max_name:
    ugfx.set_default_font(ugfx.FONT_NAME)
else:
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
# Draw name
ugfx.Label(0, 220 ,ugfx.width(), name_height, name_setting, justification=ugfx.Label.CENTER)



# Title
if len(callsign_setting) <= max_name:
    ugfx.set_default_font(ugfx.FONT_NAME)
else:
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
# Draw callsign
ugfx.Label(0, 270, ugfx.width(), callsign_height, callsign_setting, justification=ugfx.Label.CENTER)

ugfx.set_default_font(ugfx.FONT_SMALL)
# Draw for wearer to see
ugfx.orientation(270)
status = ugfx.Label(0, 300, ugfx.width(), status_height, "", justification=ugfx.Label.CENTER)

# update loop
while True:
    text = "";
    value_wifi_strength = wifi_strength()
    value_battery = battery()
    if value_wifi_strength:
        text += "Wi-Fi: %s%%, " % int(value_wifi_strength)
    if value_battery:
        text += "Battery: %s%%" % int(value_battery)
    status.text(text)
    sleep_or_exit(0.5)

app.restart_to_default()
