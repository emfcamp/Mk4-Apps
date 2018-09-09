"""Praise the Horse or Worship the Melon, directly from your badge
"""
___name___         = "Praise Horse! Worship Melon!"
___license___      = "MIT"
___dependencies___ = ["app","wifi", "buttons", "ugfx_helper"]
___categories___   = ["Other"]

import ugfx, wifi, utime, ugfx_helper, buttons
from tilda import Buttons
import random
from app import App


def loading_screen():
    logo = 'praise_horse_worship_melon/loading.gif'
    ugfx.area(0,0,ugfx.width(),ugfx.height(),0xFFFF)
    ugfx.display_image(2,2,logo)
    ugfx.set_default_font(ugfx.FONT_SMALL)
    ugfx.text(60, 145, "Praise Horse (A)", ugfx.GREY)
    ugfx.text(55, 305, "Worship Melon (B)", ugfx.GREY)

def show_screen(type=None):
    if type == "horse":
        img = "praise_horse_worship_melon/horse.gif"
        color = ugfx.RED
        text = "HORSE!"
    elif type == "melon":
        img = "praise_horse_worship_melon/melon.gif"
        color = ugfx.BLUE
        text = "MELON!"
    else:
        return

    ugfx.area(0,0,ugfx.width(),ugfx.height(), color)
    ugfx.display_image(0, 0,img)
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
    for y_offset in range(8):
        ugfx.Label(0, 42 * y_offset, ugfx.width(), 20, text, parent=None, style=None, justification=ugfx.Label.CENTER)
        utime.sleep_ms(100)

    utime.sleep_ms(1000)
    loading_screen()

def start():
    ugfx_helper.init()
    loading_screen()
    utime.sleep_ms(2000)
    return True

running = start()
while running:
    if buttons.is_triggered(Buttons.BTN_A):
        show_screen(type='horse')
    if buttons.is_triggered(Buttons.BTN_B):
        show_screen(type='melon')
    if buttons.is_triggered(Buttons.BTN_Menu):
        App("launcher").boot()
    utime.sleep_ms(30)
