""" Description """  

___title___  = "hackspace home screen "
___license___ = "MIT"
___categories___ = ["Homescreens"]
___dependencies___ = ["sleep", "app", "ugfx_helper", "buttons", "homescreen" ]


import wifi, ugfx, http, os, time, sleep, ugfx_helper, math
from tilda import Buttons
from homescreen import *
from app import restart_to_default # import at the beginning of your code
ugfx.init()


width = 240
height = 320
init()

s = ugfx.Style()
s.set_background(ugfx.BLACK)
s.set_enabled([ugfx.BLUE, ugfx.html_color(0x800080), ugfx.html_color(0x800080), ugfx.html_color(0x800080)])

ugfx.set_default_style(s)
ugfx.clear(ugfx.BLACK)
# below displaying text 
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

    
draw_name() # yjis displays names ei print 

image = ("hackme3/LHSG3.gif") # defining the gif file 

ugfx.Imagebox(0, 0, 240, 200, image)# locating / scaling the gif 




" sleep_or_exit(0.5) would normly exit home screen but its broken when using gifs the below code deals with this "

while True:

    if buttons.is_triggered(tilda.Buttons.BTN_Menu):
        clean_up()
        launcher = "launcher"
        try:
            with open("default_launcher.txt", "r") as dl:
                launcher=dl.readline()
        except OSError:
            pass
        ugfx.deinit()
        App(launcher).boot()
    sleep.sleep(0.5)

