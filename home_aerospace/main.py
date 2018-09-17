"""Default homescreen

Hackedup awful code for a london aerospace themed badge
"""

___name___         = "Aerospace Badge"
___license___      = "MIT"
___categories___   = ["Homescreens"]
___dependencies___ = ["homescreen", "wifi", "http", "ugfx_helper", "sleep"]
___launchable___   = False

import ugfx, random, time, wifi, http, math
from tilda import LED, Buttons
from machine import Neopix
from homescreen import *
import time


cycle = 0
#colourList = [0xff0000,0x00ff00]
colourList = [0xFF0000, 0xFFFFFF, 0x00FF00, 0x0000FF, 0xFFF000, 0xD800FF, 0xFF008F, 0x00FFF7]

n = Neopix()

# We ❤️ our sponsors
ugfx.display_image(0, 0, "home_aerospace/aerospace-logo.png")
wait = 5
while wait:
    wait-=1
    sleep_or_exit(0.5)

def ledChange():
    colourNum1 = colourList[random.randint(0,len(colourList)-1)]
    colourNum2 = colourList[random.randint(0,len(colourList)-1)]
    while colourNum1 == colourNum2:
        colourNum2 = colourList[random.randint(0,len(colourList)-1)]
    n.display([colourNum1,colourNum2])


# Padding for name
intro_height = 30
intro_text = "London Aerospace"
intro_width = 200
intro_position_left = 0
name_height = 60
status_height = 30
info_height = 30
tick = 0
logo_path = "home_aerospace/aerospace-logo.png"
logo_height = 250
logo_width = 250
aerospace_text = "London Aerospace Yo"

# Maximum length of name before downscaling
max_name = 8

# Background stuff
init()
ugfx.clear(ugfx.html_color(0xFFFFFF))

# Colour stuff
style = ugfx.Style()
style.set_enabled([ugfx.BLACK, ugfx.html_color(0xFFFFFF), ugfx.html_color(0xFFFFFF), ugfx.html_color(0xFFFFFF)])
style.set_background(ugfx.html_color(0xFFFFFF))
ugfx.set_default_style(style)

# Draw for people to see
ugfx.orientation(90)
# Logo stuff
ugfx.display_image(
    int((ugfx.width() - logo_width) / 2),
    int((ugfx.height() - logo_height) / 2 - 20),
    logo_path
)

# Draw introduction
ugfx.set_default_font(ugfx.FONT_TITLE)
intro_object = ugfx.Label(0, ugfx.height() - name_height - intro_height, ugfx.width(), intro_height, intro_text, justification=ugfx.Label.CENTER)
# Process name
name_setting = name("Set your name in the settings app")
if len(name_setting) <= max_name:
    ugfx.set_default_font(ugfx.FONT_NAME)
else:
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
# Draw name
ugfx.Label(0, ugfx.height() - name_height, ugfx.width(), name_height, name_setting, justification=ugfx.Label.CENTER)



# Draw for wearer to see
ugfx.orientation(270)
# Title
ugfx.set_default_font(ugfx.FONT_TITLE)
# info

ugfx.set_default_font(ugfx.FONT_SMALL)
status = ugfx.Label(0, ugfx.height() - 30, ugfx.width(), status_height, "", justification=ugfx.Label.CENTER)
status.text('BATTERY INCOMING')

# update loop
while True:
    text = "";

    if math.fmod(tick, 100) == 0:
        value_wifi_strength = wifi_strength()
        value_battery = battery()
        if value_wifi_strength:
            text += "Wi-Fi: %s%%, " % int(value_wifi_strength)
        if value_battery:
            text += "Battery: %s%%" % int(value_battery)
        status.text(text)
        tick +=1

    # if intro_position_left > -intro_width:
    #     intro_position_left -= 1
    #     intro_object.x(
    #         intro_position_left
    #     )
    # else:
    #     intro_object.x(0)
    #     intro_position_left = 0

    ledChange()

    sleep_or_exit(0.05)
