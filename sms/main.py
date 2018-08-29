"""SMS app for reading and sending messages
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

menuset = []
messages = sim800.listsms(4)

for message in messages:
    splitmessage = message.split(",")
    menuset.insert(0, { "title" : splitmessage[5] + " " + splitmessage[4] + " from " + splitmessage[2], "index" : splitmessage[0] })

while True:
	selection = prompt_option(menuset, text="Select message", select_text="Read", none_text="Exit")
	if (selection):
		message = sim800.readsms(selection["index"])
		notice(message, title=selection["title"])
	else:
		break
