"""Launcher for apps currently installed"""

___name___         = "Speed Launcher"
___license___      = "WTFPL"
___categories___   = ["System", "Launcher"]
___dependencies___ = ["app", "ugfx_helper"]
___launchable___   = False
___bootstrapped___ = False

import ugfx_helper, ugfx, math, buttons
from app import *
from tilda import Buttons

APPS_PER_PAGE = 12
EMF_PURPLE = 0x800080

ugfx_helper.init()
ugfx.clear(ugfx.html_color(EMF_PURPLE))

ugfx.set_default_font(ugfx.FONT_SMALL)
style = ugfx.Style()
style.set_enabled([ugfx.WHITE, ugfx.html_color(EMF_PURPLE), ugfx.html_color(EMF_PURPLE), ugfx.html_color(EMF_PURPLE)])
style.set_background(ugfx.html_color(EMF_PURPLE))
ugfx.set_default_style(style)

loadMsg = ugfx.Label(0, 90, ugfx.width(), 20, "Loading apps...", justification=ugfx.Label.CENTER)

# Load apps in a colourList
all_apps = [{"title": a.title, "app": a} for a in get_apps()]

# Sort apps by alphabetical order
all_apps.sort(key=lambda a: a['title'])
total_pages = math.ceil(len(all_apps) / APPS_PER_PAGE)

ugfx.clear(ugfx.html_color(EMF_PURPLE))

keypad = [
    Buttons.BTN_1,
    Buttons.BTN_2,
    Buttons.BTN_3,
    Buttons.BTN_4,
    Buttons.BTN_5,
    Buttons.BTN_6,
    Buttons.BTN_7,
    Buttons.BTN_8,
    Buttons.BTN_9,
    Buttons.BTN_Star,
    Buttons.BTN_0,
    Buttons.BTN_Hash
]

keypadLabels = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "*",
    "0",
    "#"
]

def showPage():
    global current_page
    # avoid out of bounds errors
    current_page = max(1, min(current_page, total_pages))
    
    start = (current_page - 1) * APPS_PER_PAGE
    end = start + APPS_PER_PAGE
    apps_on_current_page = all_apps[start:end]

    # Refresh page
    ugfx.clear(ugfx.html_color(EMF_PURPLE))

    # Write current page number and arrows
    ugfx.Label(0, 20, ugfx.width(), 20, "Page {} of {}".format(current_page, total_pages), justification=ugfx.Label.CENTER)

    if current_page > 1:
        ugfx.fill_polygon(10, 16, [[0, 10], [15, 20], [15, 0]], ugfx.WHITE)
        
    if current_page < total_pages:
        ugfx.fill_polygon(ugfx.width() - 30, 16, [[0, 0], [15, 10], [0, 20]], ugfx.WHITE)
    
    # Write app numbers and names
    i = 0
    yOffset = 45
    xOffset = 0
    for a in apps_on_current_page:
        # xOffset = (i % 3) * 8  # offset lines to match the physical layout of the keypad
        ugfx.area(20 + xOffset, yOffset + 2, 20, 20, ugfx.WHITE)
        ugfx.text(23 + xOffset, yOffset + 3, keypadLabels[i] + " ", EMF_PURPLE)

        ugfx.Label(46 + xOffset, yOffset + 3, ugfx.width(), 20, a['title'], justification=ugfx.Label.LEFT)
        yOffset = yOffset + 22
        i = i + 1

    while True:
        for key in keypad:
            keyIndex = keypad.index(key)
            if buttons.is_pressed(key) and (keyIndex < len(apps_on_current_page)):
                apps_on_current_page[keyIndex]['app'].boot()
                break

        if buttons.is_triggered(Buttons.JOY_Right) and (current_page is not total_pages):
            current_page = current_page + 1
            return
        if buttons.is_triggered(Buttons.JOY_Left) and (current_page is not 1):
            current_page = current_page - 1
            return
    
current_page = 1

while True:
    showPage()
