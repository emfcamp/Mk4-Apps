"""Helper library for ugfx stuff"""

___license___ = "MIT"

import ugfx
from machine import Pin

def init():
    ugfx.init()
    Pin(Pin.PWM_LCD_BLIGHT).on()

def deinit():
    Pin(Pin.PWM_LCD_BLIGHT).off()
