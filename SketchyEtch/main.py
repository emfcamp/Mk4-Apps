"""Accidentally created etcher sketch...\nThen made it awesome"""

___name___         = "Sketchy-Etch"
___title___        = "Sketchy-Etch"
___license___      = "MIT"
___dependencies___ = ["ugfx_helper", "dialogs"]
___categories___   = ["Games"]

import ugfx, ugfx_helper, app, dialogs
from tilda import Buttons
from time import sleep


def reset():
    global i
    global j
    global maxHeight
    i = int(ugfx.width() / 2)
    j = int(maxHeight / 2)
    ugfx.area(0, 0, ugfx.width(), maxHeight, ugfx.BLACK)
    ugfx.area((i - 1) if i > 0 else 0, (j - 1) if j > 0 else 0, 3 if (i > 0 and i < (ugfx.width() - 1)) else 2, 3 if (j > 0 and j < (maxHeight - 1)) else 2, ugfx.GREY)

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

shades = 16
hues = 20
scroll = 0
huesToShow = 2
colourI = 0
colourJ = 0

def showColourChangeMenu():
    global shades
    global hues
    global scroll
    global huesToShow
    global maxHeight
    boxHeight = int((ugfx.height() - maxHeight) / huesToShow)
    boxWidth = int(ugfx.width() / shades)
    for x in range(shades):
        for y in range(scroll, scroll + huesToShow):
            (r, g, b) = getColour(x / shades, y / hues)
            ugfx.area(x * boxWidth, maxHeight + int((y - scroll) * boxHeight), boxWidth, boxHeight, (int(31 * r) << 11) + (int(63 * g) << 5) + int(31 * b))

def selectColour():
    global shades
    global hues
    global scroll
    global huesToShow
    global colourI
    global colourJ
    global maxHeight
    boxHeight = int((ugfx.height() - maxHeight) / huesToShow)
    boxWidth = int(ugfx.width() / shades)
    (r, g, b) = getColour(colourI / shades, colourJ / hues)
    ugfx.box(colourI * boxWidth, maxHeight + ((colourJ - scroll) * boxHeight), boxWidth, boxHeight, (int(31 * (1 - r)) << 11) + (int(63 * (1 - g)) << 5) + int(31 * (1 - b)))

    while not Buttons.is_pressed(Buttons.JOY_Center):
        positionChanged = False
        scrollChanged = False
        oldI = colourI
        oldJ = colourJ

        if Buttons.is_pressed(Buttons.JOY_Right) and (colourI < (shades - 1)):
            colourI += 1
            positionChanged = True
            while Buttons.is_pressed(Buttons.JOY_Right):
                pass
        elif Buttons.is_pressed(Buttons.JOY_Left) and (colourI > 0):
            colourI -= 1
            positionChanged = True
            while Buttons.is_pressed(Buttons.JOY_Left):
                pass

        if Buttons.is_pressed(Buttons.JOY_Down) and (colourJ < (hues - 1)):
            if (colourJ - scroll) == 1:
                scroll += 1
                scrollChanged = True
            colourJ += 1
            positionChanged = True
            while Buttons.is_pressed(Buttons.JOY_Down):
                pass
        elif Buttons.is_pressed(Buttons.JOY_Up) and (colourJ > 0):
            if (colourJ - scroll) == 0:
                scroll -= 1
                scrollChanged = True
            colourJ -= 1
            positionChanged = True
            while Buttons.is_pressed(Buttons.JOY_Up):
                pass

        if scrollChanged or positionChanged:
            if scrollChanged:
                showColourChangeMenu()
            elif positionChanged:
                (r, g, b) = getColour(oldI / shades, oldJ / hues)
                ugfx.box(oldI * boxWidth, maxHeight + ((oldJ - scroll) * boxHeight), boxWidth, boxHeight, (int(31 * r) << 11) + (int(63 * g) << 5) + int(31 * b))

            (r, g, b) = getColour(colourI / shades, colourJ / hues)
            ugfx.box(colourI * boxWidth, maxHeight + ((colourJ - scroll) * boxHeight), boxWidth, boxHeight, (int(31 * (1 - r)) << 11) + (int(63 * (1 - g)) << 5) + int(31 * (1 - b)))

        sleep(0.05)

    while Buttons.is_pressed(Buttons.JOY_Center):
        pass

    (r, g, b) = getColour(colourI / shades, colourJ / hues)
    ugfx.box(colourI * boxWidth, maxHeight + ((colourJ - scroll) * boxHeight), boxWidth, boxHeight, (int(31 * r) << 11) + (int(63 * g) << 5) + int(31 * b))
    return (int(31 * r) << 11) + (int(63 * g) << 5) + int(31 * b)

ugfx_helper.init()

maxHeight = int(ugfx.height() * 0.9)
i = 0
j = 0

ugfx.clear()

dialogs.notice("Draw with joystick arrows\nHold joystick centre for circle\nA to clear\nMENU to choose colour\nB to exit", title="Sketchy-Etch")

ugfx.area(0, 0, ugfx.width(), maxHeight, ugfx.BLACK)
showColourChangeMenu()

circleSize = 3
reset()
colour = ugfx.WHITE
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

    if Buttons.is_pressed(Buttons.JOY_Down) and (j < (maxHeight - 1)):
        j += 1
        changed = True
    elif Buttons.is_pressed(Buttons.JOY_Up) and (j > 0):
        j -= 1
        changed = True

    if Buttons.is_pressed(Buttons.JOY_Center):
        circleSize += 1
        ugfx.fill_circle(i, j, circleSize, colour)
        showColourChangeMenu()

    if Buttons.is_pressed(Buttons.BTN_A):
        circleSize = 3
        reset()

    if Buttons.is_pressed(Buttons.BTN_Menu):
        colour = selectColour()
        circleSize = 3

    if changed:
        circleSize = 3
        ugfx.area((oldI - 1) if oldI > 0 else 0, (oldJ - 1) if oldJ > 0 else 0, 3 if (oldI > 0 and oldI < (ugfx.width() - 1)) else 2, 3 if (oldJ > 0 and oldJ < (maxHeight - 1)) else 2, colour)
        ugfx.area((i - 1) if i > 0 else 0, (j - 1) if j > 0 else 0, 3 if (i > 0 and i < (ugfx.width() - 1)) else 2, 3 if (j > 0 and j < (maxHeight - 1)) else 2, ugfx.GREY)

    sleep(0.05)

ugfx.clear()
app.restart_to_default()
