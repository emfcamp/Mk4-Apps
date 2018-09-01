"""Settings app for common or shared settings

Currently supports
* Setting name
* Setting wifi
* Pick default app
* Change badgestore repo/branch

Todo:
* timezone

"""

___name___         = "Settings"
___license___      = "MIT"
___dependencies___ = ["dialogs", "ugfx_helper", "database", "app", "stack_nav", "wifi"]
___categories___   = ["System"]
___bootstrapped___ = True

import ugfx_helper, os, wifi, app, database
from settings.badge_store_settings import settings_badge_store
from dialogs import *
from stack_nav import *

### SCREENS ###
def settings_startup_app(state):
    apps = app.get_apps()
    print(apps)
    selection = prompt_option([{"title": a.title, "app": a} for a in apps], text="Select App:", none_text="Back", title="Set startup app")
    if selection:
       app.write_launch_file(app.name, "default_app.txt")

def settings_wifi(state):
    wifi.choose_wifi()

def settings_main(state):
    return selection({
        "Homescreen Name": change_database_string("Set your name", "homescreen.name"),
        "Homescreen Callsign": change_database_string("Set your callsign", "homescreen.callsign"),
        "Wifi": settings_wifi,
        "Startup app": settings_startup_app,
        "Badge Store": settings_badge_store
    }, none_text="Exit")

### ENTRY POINT ###
ugfx_helper.init()
nav(settings_main)
app.restart_to_default()
