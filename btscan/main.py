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

status_height = 20

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_FIXED)

ugfx.Label(5, 180, 240, 15, "Press A to scan, MENU to exit")
ugfx.Label(5, 200, 240, 15, "Scan requires ~10 seconds")
if not sim800.btison():
    sim800.btpoweron()
    btrestore = True

# while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
while not Buttons.is_pressed(Buttons.BTN_Menu):
    if not Buttons.is_pressed(Buttons.BTN_A):
        ugfx.poll()
        continue

    ugfx.clear()

    np.display([0,0])
    np.display([0x000099, 0x000099])
    devs = sim800.btscan(15000)
    
    if len(devs) == 0:
        ugfx.Label(0, 0, 240, 25, "No devices found")
        np.display([0x110000,0x110000])
        sleep(1)
        np.display([0,0])
    else:
        if type(devs[0]) == int: 
            devs = [devs]
        print(devs)

        y = 0
        for dev in devs[:20]:
            print(dev)
            ugfx.Label(0, y, 240, 25, "{3}dB {1}".format(*dev))
            y += status_height
        
    
    np.display([0x00, 0x00])
    
if btrestore:
    sim800.btpoweroff()

ugfx.clear()
app.restart_to_default()
