"""This app connects to the Hologram service via GPRS  displays recieved data on the screen and sets the neopixles"""

___title___        = "Hologram Demo"
___license___      = "MIT"	
___dependencies___ = ["app", "sim800"]
___categories___   = ["EMF", "System"]
___bootstrapped___ = False

#import ugfx, os, time, sleep, app, sim800

import ugfx, app, sim800
import os
from tilda import Buttons
from time import sleep
from machine import Neopix


n = Neopix()

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_FIXED)


def callback(data):
    payload=data.decode("utf-8") 
    ugfx.Label(5, 100, 240, 15, payload)
    colour = int(payload)
    n.display([colour,colour])
    
print('Launching Hologram Demo')
ugfx.Label(5, 20, 240, 15, "Starting....")
sim800.setup_gprs()
ugfx.Label(5, 20, 240, 15, "GPRS Ready")
sim800.connect_gprs('hologram')
ugfx.Label(5, 40, 240, 15, "GPRS Connected")
sim800.start_server(4010, callback)
ugfx.Label(5, 60, 240, 15, "Server Started")


ugfx.Label(5, 300, 240, 15, "** Hold A or B or MENU to exit **")


while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    sleep(2)

ugfx.clear()
ugfx.Label(5, 20, 240, 15, "Stopping....")
sim800.stop_server()
sim800.stop_gprs()
app.restart_to_default()	
