"""A simple homescreen diplaying an avatar from an url and the user's name"""

___name___         = "Avatar Homescreen"
___license___      = "WTFPL"
___categories___   = ["Homescreens"]
___dependencies___ = ["homescreen", "wifi", "http", "sleep", "app", "buttons"]
___bootstrapped___ = False
___launchable___   = True

import ugfx_helper, uos, wifi, ugfx, http, time, sleep, app, sys, database, buttons
from tilda import Buttons
from homescreen import *
from dialogs import *

# Constants
intro_height = 30
name_height = 60
status_height = 20
info_height = 30
max_name = 8
avatar_file_name='shared/avatar.png'
avatar_db_key="avatar_url"

# Local variables
db = database.Database()

### START OF WRITING STUFF ###

def write_instructions():
    ugfx.clear(ugfx.html_color(0x000000))
    ugfx.orientation(270)
    ugfx.text(5, 5, "Press A to refresh", ugfx.WHITE)
    ugfx.text(5, 25, "Press B to change the url", ugfx.WHITE)
    ugfx.text(5, 45, "Press Menu to exit", ugfx.WHITE)

def write_hot_instructions():
    ugfx.orientation(270)
    ugfx.text(3, 85, "Press A to refresh or press B", ugfx.WHITE)
    ugfx.text(3, 105, "to change the url or check", ugfx.WHITE)
    ugfx.text(3, 125, "your wifi settings...", ugfx.WHITE)

def write_loading():
    ugfx.clear(ugfx.html_color(0x000000))
    ugfx.orientation(90)
    ugfx.text(5, 5, "Loading...", ugfx.WHITE)
    ugfx.orientation(270)
    ugfx.text(5, 5, "Loading...", ugfx.WHITE)

def write_name():
    name_setting = name("Set your name in the settings app")
    if len(name_setting) <= max_name:
        ugfx.set_default_font(ugfx.FONT_NAME)
    else:
        ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
    # Draw name
    ugfx.orientation(90)
    ugfx.Label(0, ugfx.height() - name_height, ugfx.width(), name_height, name_setting, justification=ugfx.Label.CENTER, style=style)

### END OF WRITING STUFF ###

### START OF AVATAR HANDLING STUFF ###

def avatar_exists():
    ret = True
    try:
        f = open(avatar_file_name, 'r')
    except:
        ret = False
    return ret


def load_avatar():
    #Load the avatar from the local storage
    try:
        f = open(avatar_file_name, 'r')
        avatar_file = f.read()
        ugfx.orientation(90)
        ugfx.display_image(0,0,bytearray(avatar_file))
        f.close()
        return True
    except:
        ugfx.clear(ugfx.html_color(0x000000))
        ugfx.orientation(270)
        ugfx.text(3, 65, "No local avatar.", ugfx.RED)
        return False

def download_avatar():
    avatar_url=db.get("avatar_url", "")
    if avatar_url:
        if (avatar_url.endswith(".png") or avatar_url.startswith("http")):
            try:
                image = http.get(avatar_url).raise_for_status().content
                ugfx.orientation(90)
                ugfx.display_image(0,0,bytearray(image))
                #f = open(avatar_file_name, 'w')
                #f.write(image)
                #f.close()
                #ugfx.display_image(0,0,bytearray(image))
            except:
                ugfx.clear(ugfx.html_color(0x000000))
                ugfx.orientation(270)
                ugfx.text(3, 65, "Couldn't download the avatar.", ugfx.RED)
                return False
        else:
            ugfx.clear(ugfx.html_color(0x000000))
            ugfx.orientation(270)
            ugfx.text(3, 65, "Invalid avatar url.", ugfx.RED)
            return False
    else:
        ugfx.clear(ugfx.html_color(0x000000))
        ugfx.orientation(270)
        ugfx.text(3, 65, "No avatar url.", ugfx.RED)
    return True

### END OF AVATAR HANDLING STUFF ###

### START OF MAIN ###

def start():
    write_name()
    #if not avatar_exists():
    if not download_avatar():
        write_hot_instructions()
    #if not load_avatar():
        #write_hot_instructions()

init()

ugfx.clear(ugfx.html_color(0x000000))

style = ugfx.Style()
style.set_enabled([ugfx.WHITE, ugfx.html_color(0x000000), ugfx.html_color(0x000000), ugfx.html_color(0x000000)])
style.set_background(ugfx.html_color(0x000000))
ugfx.set_default_style(style)

write_instructions()

wait_until = time.ticks_ms() + 3000
while time.ticks_ms() < wait_until:
    time.sleep(0.1)
    if Buttons.is_pressed(Buttons.BTN_A) or Buttons.is_pressed(Buttons.BTN_B) or Buttons.is_pressed(Buttons.BTN_Menu):
        break

start()

while True:
    if buttons.is_triggered(Buttons.BTN_B):
        ugfx.orientation(270)
        avatar_url = prompt_text("Avatar url:", init_text=db.get(avatar_db_key, ""))
        db.set(avatar_db_key, avatar_url)
        db.flush()
        ugfx.orientation(90)
        start()
    if buttons.is_triggered(Buttons.BTN_Menu):
        break

app.restart_to_default()
       
### END OF MAIN ###
        
