"""Generic setting used by different apps"""

___name___         = "Settings"
___license___      = "GPL"
___categories___   = ["System"]
___launchable___   = True
___bootstrapped___ = True
___dependencies___ = ["app", "dialogs"]

import app
from dialogs import *

ugfx.init()

option = prompt_option(["tbd"], none_text="Exit", title="Settings")

app.restart_to_default()
