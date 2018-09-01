"""
Clone of the default homescreen for the Tilda Mk4.
Shows the EMF homescreen and a picture loaded on the badge alternately.
"""

___name___ = "Custom Image Home"
___license___ = "MIT"
___categories___ = ["Homescreens"]
___dependencies___ = ["homescreen", "shared/logo.png", "shared/sponsors.png"]
___launchable___ = False
___bootstrapped___ = True

import ugfx
from homescreen import *
import time
import os

# We ❤️ our sponsors
ugfx.display_image(0, 0, "shared/sponsors.png")
wait = 5
while wait:
    wait -= 1
    sleep_or_exit(0.5)


def drawEMFscreen():
    # Padding for name
    intro_height = 30
    intro_text = "Hi! I'm"
    name_height = 60
    status_height = 20
    info_height = 30
    logo_path = "shared/logo.png"
    logo_height = 150
    logo_width = 56

    # Maximum length of name before downscaling
    max_name = 8

    # Background stuff
    init()
    ugfx.clear(ugfx.html_color(0x800080))

    # Colour stuff
    style = ugfx.Style()
    style.set_enabled([ugfx.WHITE, ugfx.html_color(0x800080), ugfx.html_color(0x800080), ugfx.html_color(0x800080)])
    style.set_background(ugfx.html_color(0x800080))
    ugfx.set_default_style(style)

    # Logo stuff
    ugfx.display_image(
        int((ugfx.width() - logo_width) / 2),
        int((ugfx.height() - logo_height) / 2),
        logo_path
    )

    # Draw for people to see
    ugfx.orientation(90)
    # Draw introduction
    ugfx.set_default_font(ugfx.FONT_TITLE)
    ugfx.Label(0, ugfx.height() - name_height - intro_height, ugfx.width(), intro_height, intro_text,
               justification=ugfx.Label.CENTER)
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
    ugfx.Label(0, ugfx.height() - info_height * 2, ugfx.width(), info_height, "TiLDA Mk4",
               justification=ugfx.Label.CENTER)
    # info
    ugfx.Label(0, ugfx.height() - info_height, ugfx.width(), info_height, "Press MENU", justification=ugfx.Label.CENTER)

    ugfx.set_default_font(ugfx.FONT_SMALL)
    status = ugfx.Label(0, ugfx.height() - info_height * 2 - status_height, ugfx.width(), status_height, "",
                        justification=ugfx.Label.CENTER)

    text = ""
    value_wifi_strength = wifi_strength()
    value_battery = battery()
    if value_wifi_strength:
        text += "Wi-Fi: %s%%, " % int(value_wifi_strength)
    if value_battery:
        text += "Battery: %s%%" % int(value_battery)
    status.text(text)


def drawCustomImage():
    ugfx.clear()
    ugfx.orientation(90)
    ugfx.display_image(0, 0, 'customImage.png')

def drawHelpText():
    ugfx.clear()
    ugfx. Label(0, 110, ugfx.width(), 100, "Copy an image named\ncustomImage.png with a\n240x320 resolution to the\nbadge root directory\nand it will appear!")


try:
    f = open('customImage.png')
    customImage = True
    f.close()
except OSError:
    customImage = False

# update loop
while True:
    drawEMFscreen()
    wait = 20
    while wait:
        wait -= 1
        sleep_or_exit(0.5)
    if customImage:
        drawCustomImage()
    else:
        drawHelpText()
    wait = 20
    while wait:
        wait -= 1
        sleep_or_exit(0.5)