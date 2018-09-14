"""SMS app for reading and sending messages
"""
___title___         = "SMS"
___license___      = "MIT"
___dependencies___ = ["app", "dialogs", "sim800", "ugfx_helper"]
___categories___   = ["System"]
___bootstrapped___ = True

from app import *
from dialogs import *
import ugfx
import ugfx_helper
import sim800

sim800.poweron()

ugfx_helper.init()
ugfx.clear()

menuset = []
messages = sim800.listsms(4)

def send_message():
    number = ""
    message = ""
    while True:
        number = prompt_text("Number to message:", init_text=number, numeric=True)
        if number is None:
            return
        message = prompt_text("Message:", init_text=message)
        if message is not None:
            if sim800.sendsms(number, message):
                return

for message in messages:
    splitmessage = message.split(",")
    menuset.insert(0, { "title" : splitmessage[5] + " " + splitmessage[4] + " from " + splitmessage[2], "index" : splitmessage[0] })

menuset.insert(0, { "title" : "Send message...", "index" : -1 })

while True:
    selection = prompt_option(menuset, text="Select message", select_text="Read", none_text="Exit")
    if (selection):
        if (selection["index"]==-1):
            send_message()
        else:
            message = sim800.readsms(selection["index"])
            notice(message, title=selection["title"])
            if prompt_boolean("Delete this message?", title=selection["title"]):
                sim800.deletesms(selection["index"])
                for menuitem in menuset:
                    if menuitem["index"]==selection["index"]:
                        menuset.remove(menuitem)
    else:
        break

restart_to_default()
