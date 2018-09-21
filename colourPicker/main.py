"""Colour picker to show on neopixels"""

___name___         = "ColourPicker"
___title___        = "Colour Picker"
___license___      = "MIT"
___dependencies___ = ["ugfx_helper"]
___categories___   = ["LEDs"]

import ugfx, ugfx_helper, app
from tilda import Buttons
from time import sleep
from machine import Neopix

def getColour(intensity, angle):
    intensity *= 2
    if angle < (1 / 6):
        return (intensity, intensity * (angle * 6), 0) if intensity < 1 else (1, (angle * 6) + ((1 - (angle * 6)) * (intensity - 1)), (intensity - 1))
    elif angle < (2 / 6):
        return (intensity * (2 - (6 * angle)), intensity, 0) if intensity < 1 else ((2 - (6 * angle)) + ((1 - (2 - (6 * angle))) * (intensity - 1)), 1, (intensity - 1))
    elif angle < (3 / 6):
        return (0, intensity, intensity * ((6 * angle) - 2)) if intensity < 1 else ((intensity - 1), 1, ((6 * angle) - 2) + ((1 - ((6 * angle) - 2)) * (intensity - 1)))
    elif angle < (4 / 6):
        return (0, intensity * (4 - (6 * angle)), intensity) if intensity < 1 else ((intensity - 1), (4 - (6 * angle)) + ((1 - (4 - (6 * angle))) * (intensity - 1)), 1)
    elif angle < (5 / 6):
        return (intensity * ((6 * angle) - 4), 0, intensity) if intensity < 1 else (((6 * angle) - 4) + ((1 - ((6 * angle) - 4)) * (intensity - 1)), (intensity - 1), 1)
    else:
        return (intensity, 0, intensity * 6 * (1 - angle)) if intensity < 1 else (1, (intensity - 1), (6 * (1 - angle)) + ((1 - (6 * (1 - angle))) * (intensity - 1)))


ugfx_helper.init()
ugfx.clear()

maxHeight = ugfx.height()
n = Neopix()

# Draw colour swatch
for x in range(ugfx.width()):
    intensity = x / ugfx.width()
    for y in range(maxHeight):
        (r, g, b) = getColour(intensity, y / ugfx.height())
        colour = (int(31 * r) << 11) + (int(63 * g) << 5) + int(31 * b)
        ugfx.area(x, y, 1, 1, colour)


i = 0
j = 0
ugfx.area((i - 1) if i > 0 else 0, (j - 1) if j > 0 else 0, 3 if (i > 0 and i < (ugfx.width() - 1)) else 2, 3 if (j > 0 and j < (maxHeight - 1)) else 2, ugfx.WHITE)
while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    changed = False
    oldI = i
    oldJ = j

    if Buttons.is_pressed(Buttons.JOY_Right) and (i < (ugfx.width() - 1)):
        i += 1
        changed = True
    elif Buttons.is_pressed(Buttons.JOY_Left) and (i > 0):
        i -= 1
        changed = True
        
    if Buttons.is_pressed(Buttons.JOY_Down) and (j < (maxHeight - 1)):
        j += 1
        changed = True
    elif Buttons.is_pressed(Buttons.JOY_Up) and (j > 0):
        j -= 1
        changed = True
        
    if changed:
        (r, g, b) = getColour(i / ugfx.width(), j / ugfx.height())
        colour = (int(255 * r) << 16) + (int(255 * g) << 8) + int(255 * b)
        n.display([colour, colour])
        
        
        for xx in range((oldI - 1) if (oldI > 0) else 0, 1 + ((oldI + 1) if (oldI < (ugfx.width() - 2)) else (ugfx.width() - 1))):
            intensity = xx / ugfx.width()
            for yy in range((oldJ - 1) if (oldJ > 0) else 0, 1 + ((oldJ + 1) if (oldJ < (maxHeight - 2)) else (maxHeight - 1))):
                (rr, gg, bb) = getColour(intensity, yy / ugfx.height())
                colour = (int(31 * rr) << 11) + (int(63 * gg) << 5) + int(31 * bb)
                ugfx.area(xx, yy, 1, 1, colour)

        ugfx.area((i - 1) if i > 0 else 0, (j - 1) if j > 0 else 0, 3 if (i > 0 and i < (ugfx.width() - 1)) else 2, 3 if (j > 0 and j < (maxHeight - 1)) else 2, ugfx.WHITE)
        
        
    sleep(0.05)

ugfx.clear()
app.restart_to_default()
