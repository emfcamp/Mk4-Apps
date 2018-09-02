"""Scan for and display nearby bluetooth devices"""

___name___         = "Bluetooth Scan"
___license___      = "MIT"	
___dependencies___ = ["sleep", "app", "sim800"]
___categories___   = ["Other", "System"]

import ugfx, app
from machine import Neopix
np = Neopix()

import sim800
from tilda import Buttons
from time import sleep

btrestore = False
duration = 10
status_height = 20

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_FIXED)

def instructions(duration):
    ugfx.Label(5, 180, 240, 30, "Press A to start, B to change scan length or MENU to exit")
    ugfx.Label(5, 210, 240, 15, "Scan requires ~{0} seconds".format(duration))

if not sim800.btison():
    sim800.btpoweron()
    btrestore = True

instructions(duration)
# while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
while not Buttons.is_pressed(Buttons.BTN_Menu):
    a = Buttons.is_pressed(Buttons.BTN_A)
    b = Buttons.is_pressed(Buttons.BTN_B)
    if not a and not  b:
        ugfx.poll()
        continue

    if b:
        duration = duration + 5
        if duration > 60:
            duration = 5
        ugfx.clear()
        instructions(duration)
        continue

    ugfx.clear()

    np.display([0,0])
    np.display([0x000099, 0x000099])
    devs = sim800.btscan(duration*1000)
    np.display([0x00, 0x00])
    
    if len(devs) == 0:
        ugfx.Label(0, 0, 240, 25, "No devices found")
        np.display([0x110000,0x110000])
        sleep(1)
        np.display([0,0])
    else:
        if type(devs[0]) == int: 
            devs = [devs]

        y = 0
        for dev in devs[:20]:
            ugfx.Label(0, y, 240, 25, "{3}dB {1}".format(*dev))
            y += status_height
    instructions(duration)
            
## App quitting... 
if btrestore:
    sim800.btpoweroff()

ugfx.clear()
app.restart_to_default()
