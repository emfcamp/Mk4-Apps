"""Phone app for baic calling functions
"""
___name___         = "Phone"
___license___      = "MIT"
___dependencies___ = ["app", "dialogs", "sim800", "ugfx_helper"]
___categories___   = ["System"]
___bootstrapped___ = True

from app import *
from dialogs import *
import ugfx
import ugfx_helper
import sim800

ugfx_helper.init()
ugfx.clear()

notocall = prompt_text("Number to call:")

if (notocall):
	sim800.call(notocall)
