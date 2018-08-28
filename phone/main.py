"""Phone app for baic calling functions
"""
___name___         = "Phone"
___license___      = "MIT"
___dependencies___ = ["dialogs", "ugfx_helper", "app", "stack_nav", "sim800"]
___categories___   = ["System"]
___bootstrapped___ = True

import sim800
import ugfx_helper, ugfx
from app import *
from dialogs import *

ugfx_helper.init()
ugfx.clear()

notocall = prompt_text("Number to call:")

if (notocall):
	sim800.call(notocall)
