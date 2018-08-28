"""Phone app for baic calling functions
"""
___name___         = "Phone"
___license___      = "MIT"
___dependencies___ = ["dialogs", "app", "sim800"]
___categories___   = ["System"]
___bootstrapped___ = True

from app import *
from dialogs import *
import sim800
import ugfx_helper, ugfx

ugfx_helper.init()
ugfx.clear()

notocall = prompt_text("Number to call:")

if (notocall):
	sim800.call(notocall)
