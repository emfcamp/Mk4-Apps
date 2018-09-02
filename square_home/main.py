"""A home screen with squares that spin"""

___name___         = "Squares home"
___license___      = "MIT"
___dependencies___ = ["sleep", "app", "ugfx_helper", "buttons", "homescreen"]
___categories___   = ["Homescreens"]

import ugfx, os, time, sleep, ugfx_helper, math
from tilda import Buttons
from homescreen import *

width = 240
height = 320
ugfx_helper.init()

s = ugfx.Style()
s.set_background(ugfx.BLACK)
s.set_enabled([ugfx.WHITE, ugfx.html_color(0x800080), ugfx.html_color(0x800080), ugfx.html_color(0x800080)])
ugfx.set_default_style(s)

# This was taken from the stock home app
def draw_name():
    intro_text = "Hi! I'm"
    intro_height = 30
    name_height = 60
    max_name = 8

    ugfx.orientation(90)
    ugfx.set_default_font(ugfx.FONT_TITLE)
    # Process name
    name_setting = name("Set your name in the settings app")
    if len(name_setting) <= max_name:
        ugfx.set_default_font(ugfx.FONT_NAME)
    else:
        ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
    
    ugfx.Label(0, ugfx.height() - name_height - intro_height, ugfx.width(), intro_height, intro_text, justification=ugfx.Label.CENTER)
    ugfx.Label(0, ugfx.height() - name_height, ugfx.width(), name_height, name_setting, justification=ugfx.Label.CENTER)

    ugfx.orientation(270)

def go():
    ugfx.clear(ugfx.BLACK)
    draw_name()

    colors = [ugfx.WHITE, ugfx.GREEN, ugfx.YELLOW, ugfx.BLUE]

    ci = 0
    r = 70
    dr = 2
    d = 0.0
    dd = 0.1
    
    hOffset = 40

    while True:
        if (math.fabs(d) > 4):
            ugfx.clear(ugfx.BLACK)
            draw_name()

            dd = -dd
            d = 0
            ci += 1

            if (ci >= len(colors)):
                ci = 0

        px1 = math.floor(width / 2 +  r * math.sin(d))
        py1 = math.floor(height / 2 +  r * math.cos(d) + hOffset)

        px2 = math.floor(width / 2 + r * math.sin(d + math.pi / 2))
        py2 = math.floor(height / 2 + r * math.cos(d + math.pi / 2)  + hOffset)

        px3 = math.floor(width / 2 + r * math.sin(d + math.pi))
        py3 = math.floor(height / 2 + r * math.cos(d + math.pi)  + hOffset)

        px4 = math.floor(width / 2 + r * math.sin(d + (math.pi * 1.5)))
        py4 = math.floor(height / 2 + r * math.cos(d + (math.pi * 1.5))  + hOffset)

        ugfx.line(px1, py1, px2, py2, colors[ci])
        ugfx.line(px3, py3, px2, py2, colors[ci])
        ugfx.line(px3, py3, px4, py4, colors[ci])
        ugfx.line(px1, py1, px4, py4, colors[ci])

        d += dd
        r += dr

        if (r > 100):
            dr = -dr

        if (r < 30):
            dr = -dr

        sleep_or_exit(0.1)
    
go()
