"""Shared functionality for home screen apps

Apps in the "homescreen" should behave in a similar manner to not confuse users.

In particular, they *should*:

* Call "homescreen.init()" at the beginning. This will initiate ugfx, clear the screen and
  initiate button handline.
* Use "pyb.wfi()" as much as possible to avoid draining the battery.
* Not use

They also *may*:

* Display a name, returned by "homescreen.name()"
* Display network strength "homescreen.mobile_strength()" (0-1, might return "None" if no SIM card found)
* Display network strength "homescreen.wifi_strength()" (0-1, might return "None" if not connected)
* Display remaining battery "homescreen.battery()" (0-1)
"""

__license___      = "MIT"
__dependencies___ = ["database", "buttons"]

import database, ugfx, buttons

def init(color = 0xFFFFFF):
    ugfx.init()
    ugfx.clear(ugfx.html_color(color))
    buttons.init()
    #buttons.enable_interrupt()

def menu():
    ugfx.clear()

def name():
    return database.get("homescreen.name", "Marek")

def mobile_strength():
    return 0.75

def wifi_strength():
    return 0.65

def battery():
    return 0.65

