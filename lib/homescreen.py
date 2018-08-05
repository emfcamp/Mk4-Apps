"""Shared functionality for home screen apps

Apps in the "homescreen" should behave in a similar manner to not confuse users.

In particular, they *should*:

* Call "homescreen.init()" at the beginning. This will initiate ugfx, clear the screen and
  initiate button handline.
* Use "pyb.wfi()" as much as possible to avoid draining the battery.
* Not use

They also *may*:

* Display a name, returned by "homescreen.name()"
* Display network strength "homescreen.wifi_strength()" (0-1, might return "None" if not connected)
* Display remaining battery "homescreen.battery()" (0-1)
"""

___license___      = "MIT"
___dependencies___ = ["database", "buttons", "random", "app"]

import database, ugfx, random, buttons, time
from app import App

def init(color = 0xFFFFFF):
    ugfx.init()
    ugfx.orientation(90)
    ugfx.clear(ugfx.html_color(color))

# A special loop that exits on menu being pressed
def loop(func, interval = 500):
    buttons.init()
    state = {"pressed": False} # This is a terrible hack
    def irp(t):
        state["pressed"] = True
    buttons.enable_interrupt("BTN_MENU", irp, on_release = True)
    while not state["pressed"]:
        func()
        time.sleep_ms(interval)
    buttons.disable_interrupt("BTN_MENU")
    App("launcher").boot()


def menu():
    ugfx.clear()

def name(default = None):
    return database.get("homescreen.name", default)

def wifi_strength():
    return random.rand() / 256

def battery():
    return random.rand() / 256

