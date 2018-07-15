"""switches between app libraries, updates and installs apps.

To publish apps use https://badge.emfcamp.org"""

___license___      = "MIT"
___name___         = "App Library"
___dependencies___ = ["wifi", "dialogs"]
___bootstrapped___ = True

import pyb
import ugfx
import os
#import http_client
import wifi
import dialogs
#from app import App, get_local_apps, get_public_apps, get_public_app_categories, empty_local_app_cache
#import filesystem

TEMP_FILE = ".temp_download"

ugfx.init()

### VIEWS ###

def clear():
    ugfx.clear(ugfx.html_color(0x7c1143))

def store():
    None

def update():
    None

def remove():
    None

def settings():
    None

def main_menu():
    while True:
        clear()

        print()

        menu_items = [
            {"title": "Install Apps", "function": store},
            {"title": "Update", "function": update},
            {"title": "Manage Apps", "function": remove},
            {"title": "Settings", "function": settings}
        ]

        option = dialogs.prompt_option(menu_items, none_text="Exit", text="What do you want to do?", title="TiLDA App Library")

        if option:
            option["function"]()
        else:
            return

main_menu()

#if App("home").loadable:
#    main_menu()
#else:
#    for app_name in ["changename", "snake", "alistair~selectwifi", "sponsors", "home"]:
#        install(App(app_name))
#    pyb.hard_reset()
