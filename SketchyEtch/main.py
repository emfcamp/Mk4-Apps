"""Accidentally created etcher sketch..."""

___name___         = "Sketchy-Etch"
___title___        = "Sketchy-Etch"
___license___      = "MIT"
___dependencies___ = ["ugfx_helper", "dialogs"]
___categories___   = ["Games"]

import ugfx, ugfx_helper, app, dialogs
from tilda import Buttons
from time import sleep

i = 0
j = 0

def reset():
    global i
    global j
    i = int(ugfx.width() / 2)
    j = int(ugfx.height() / 2)
    ugfx.area(0, 0, ugfx.width(), ugfx.height(), ugfx.BLACK)
    ugfx.area((i - 1) if i > 0 else 0, (j - 1) if j > 0 else 0, 3 if (i > 0 and i < (ugfx.width() - 1)) else 2, 3 if (j > 0 and j < (ugfx.height() - 1)) else 2, ugfx.GREY)

ugfx_helper.init()
ugfx.clear()

dialogs.notice("Draw with joystick arrows\nHold joystick centre for circle\nA to clear\nB to exit", title="Sketchy-Etch")

ugfx.area(0, 0, ugfx.width(), ugfx.height(), ugfx.BLACK)


circleSize = 3
reset()
while not Buttons.is_pressed(Buttons.BTN_B):
    changed = False
    oldI = i
    oldJ = j

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
        
    if Buttons.is_pressed(Buttons.JOY_Center):
        circleSize += 1
        ugfx.fill_circle(i, j, circleSize, ugfx.WHITE)
        changed = True
    else:
        circleSize = 3
        
    if Buttons.is_pressed(Buttons.BTN_A):
        reset()
	
    if changed:
        ugfx.area((oldI - 1) if oldI > 0 else 0, (oldJ - 1) if oldJ > 0 else 0, 3 if (oldI > 0 and oldI < (ugfx.width() - 1)) else 2, 3 if (oldJ > 0 and oldJ < (ugfx.height() - 1)) else 2, ugfx.WHITE)
        ugfx.area((i - 1) if i > 0 else 0, (j - 1) if j > 0 else 0, 3 if (i > 0 and i < (ugfx.width() - 1)) else 2, 3 if (j > 0 and j < (ugfx.height() - 1)) else 2, ugfx.GREY)
	
    sleep(0.05)

ugfx.clear()
app.restart_to_default()
