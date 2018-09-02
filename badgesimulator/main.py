"""This app creates a real EMF badge experience"""

___name___         = "EMF 2018 badge simulator"
___license___      = "MIT"
___categories___   = ["EMF"]
___dependencies___ = ["sleep", "app"]

import ugfx, app
from time import sleep
from tilda import Buttons

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)

ugfx.Label(10, 10, 240, 15, "EMF2018")
ugfx.Label(10, 40, 240, 15, "TiLDA Mk4")
ugfx.Label(10, 80, 240, 15, "Error")
ugfx.Label(10, 110, 240, 15, "Something went wrong :(")

while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    sleep(2)

ugfx.clear()
app.restart_to_default()
