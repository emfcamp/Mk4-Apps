"""Launcher for apps currently installed"""

___name___         = "Launcher"
___license___      = "MIT"
___categories___   = ["System"]
___dependencies___ = ["dialogs", "app", "ugfx_helper"]
___launchable___   = False
___bootstrapped___ = True

import ugfx_helper, ugfx
from app import *
from dialogs import *

ugfx_helper.init()
ugfx.clear()

options = [{"title": a.title, "app": a} for a in get_apps()]
option = prompt_option(options, none_text="Home", text="Select App to start")

if not option:
    restart_to_default()
else:
    option["app"].boot()
