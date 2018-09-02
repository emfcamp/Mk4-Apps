"""Accidentally created etcher sketch..."""

___name___         = "Sketchy Etch"
___title___        = "Sketchy Etch"
___license___      = "MIT"
___dependencies___ = ["ugfx_helper"]
___categories___   = ["Games"]

import ugfx, ugfx_helper, app
from tilda import Buttons
from time import sleep

ugfx_helper.init()
ugfx.clear()

ugfx.area(0, 0, ugfx.width(), ugfx.height(), ugfx.BLACK)
			

i = int(ugfx.width() / 2)
j = int(ugfx.height() / 2)
while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    changed = False

    if Buttons.is_pressed(Buttons.JOY_Right) and (i < (ugfx.width() - 1)):
        i += 1
        changed = True
    elif Buttons.is_pressed(Buttons.JOY_Left) and (i > 0):
        i -= 1
        changed = True
		
    if Buttons.is_pressed(Buttons.JOY_Down) and (j < (ugfx.height() - 1)):
        j += 1
        changed = True
    elif Buttons.is_pressed(Buttons.JOY_Up) and (j > 0):
        j -= 1
        changed = True
	
    if changed:
        ugfx.area((i - 1) if i > 0 else 0, (j - 1) if j > 0 else 0, 3 if (i > 0 and i < (ugfx.width() - 1)) else 2, 3 if (j > 0 and j < (ugfx.height() - 1)) else 2, ugfx.WHITE)
	
    sleep(0.05)

ugfx.clear()
app.restart_to_default()
