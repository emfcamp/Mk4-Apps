"""Shared functionality for home screen apps

Apps in the "homescreen" should behave in a similar manner to not confuse users.

In particular, they *should*:

* Call "homescreen.init()" at the beginning. This will initiate ugfx, clear the screen and
  initiate button handline.
* Use "sleep.wfi()" as much as possible to avoid draining the battery.
* Not use

They also *may*:

* Display a name, returned by "homescreen.name()"
* Display network strength "homescreen.wifi_strength()" (0-1, might return "None" if not connected)
* Display remaining battery "homescreen.battery()" (0-1)
"""

___license___      = "MIT"
___dependencies___ = ["database", "buttons", "random", "app", "sleep", "ugfx_helper"]

import database, ugfx, random, buttons, tilda, sleep, ugfx_helper
from app import App

_state = None
def init(enable_menu_button = True):
    global _state
    _state = {"menu": False}
    ugfx_helper.init()

    if enable_menu_button:
        pass
        #buttons.enable_interrupt("BTN_MENU", lambda t: set_state("menu"), on_release = True)

def set_state(key, value = True):
    # we can't allocate memory in interrupts, so make sure all keys are set beforehand and
    # you're only using numbers and booleans
    global _state
    _state[key] = value

def clean_up():
    pass

def sleep_or_exit(interval = 0.5):
    # todo: do this better - check button multiple times and sleep for only a short while
    if buttons.is_triggered(tilda.Buttons.BTN_Menu):
        clean_up()
        App("launcher").boot()
    sleep.sleep(interval)


def name(default = None):
    return database.get("homescreen.name", default)

def wifi_strength():
    return random.random()

def battery():
    return random.random()

