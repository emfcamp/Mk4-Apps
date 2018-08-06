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

import database, ugfx, random, buttons, time, select
from app import App

_state = None
def init(enable_menu_button = True):
    global _state
    _state = {"menu": False}
    ugfx.init()
    ugfx.orientation(90)



    if enable_menu_button:
        buttons.init()
        buttons.enable_interrupt("BTN_MENU", lambda t: set_state("menu"), on_release = True)

def set_state(key, value = True):
    global _state
    _state[key] = value

def clean_up():
    buttons.disable_all_interrupt()

def check():
    global _state
    if _state["menu"]:
        clean_up()
        App("launcher").boot()

def sleep(interval = 500):
    check()
    time.sleep_ms(interval) # todo: deep sleep
    check()

def name(default = None):
    return database.get("homescreen.name", default)

def wifi_strength():
    return random.rand() / 256

def battery():
    return random.rand() / 256

