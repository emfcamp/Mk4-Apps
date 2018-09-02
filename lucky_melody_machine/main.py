"""
Learn your personal lucky melody.
"""

___name___ = "lucky_melody_machine"
___license___ = "WTFPL"
___dependencies___ = ["app", "buttons", "dialogs", "speaker", "sleep", "ugfx_helper"]
___categories___ = ["Sound"]

import app
import dialogs
import speaker
import sleep
import time
import ugfx
import ugfx_helper

from app import *
from buttons import is_pressed
from tilda import Buttons

#
# CONFIGURATION
#

APP_TITLE = "Lucky Melody Machine"
LOCAL_FOLDER =  "lucky_melody_machine/%s"
STEP_IDX = 0

#
# FUNCTIONS
#

def is_int(value):
    try:
        i = int(value)
        return True
    except ValueError:
        return False

def show_next_step():
    global STEP_IDX
    current_step = STEP_IDX
    STEP_IDX = (current_step + 1) % len(STEPS) # next step
    STEPS[current_step]()

def play_note(note, duration):
    speaker.note(note)
    sleep.sleep_ms(duration)

def play_coin_fx():
    play_note("C#7", 200)
    play_note("G#7", 200)
    speaker.stop()

def play_melody():
    play_note("E4", 400)
    play_note("E4", 400)
    play_note("E4", 400)
    play_note("D4", 220)
    play_note("C4", 200)
    play_note("E4", 400)
    play_note("E4", 400)
    play_note("E4", 400)
    play_note("D4", 220)
    play_note("C4", 220)
    play_note("E4", 400)
    play_note("E4", 400)
    play_note("F4", 400)
    play_note("E4", 400)
    play_note("D4", 760)
    speaker.stop()

def loop_notice(text, image, is_numpad=False, interval=4000):
    next_tick = 0
    while True:
        if time.ticks_ms() > next_tick:
            dialogs.notice(text, title=APP_TITLE)
            ugfx.display_image(0, 0, LOCAL_FOLDER % image)
            next_tick = time.ticks_ms() + interval

        if is_numpad:
            if is_pressed(Buttons.BTN_1) or is_pressed(Buttons.BTN_2) or is_pressed(Buttons.BTN_3) or is_pressed(Buttons.BTN_4) or is_pressed(Buttons.BTN_5) or is_pressed(Buttons.BTN_6) or is_pressed(Buttons.BTN_7) or is_pressed(Buttons.BTN_8) or is_pressed(Buttons.BTN_9):
                break
        else:
            if is_pressed(Buttons.BTN_A):
                break

        sleep.wfi()

#
# VIEWS
#

def show_start():
    ugfx.display_image(0, 0, LOCAL_FOLDER % "main.gif")
    sleep.sleep_ms(2000)

    loop_notice("Please insert a coin to\nlearn your personal lucky melody.", "main.gif")
    show_next_step()

def show_coin():
    loop_notice("Please insert a coin.", "coin_slot.gif", is_numpad=True)
    play_coin_fx()
    show_next_step()

def show_coin_again():
    loop_notice("Please insert another coin.", "coin_slot.gif", is_numpad=True)
    play_coin_fx()
    show_next_step()

def show_weight():
    ugfx.display_image(0, 0, LOCAL_FOLDER % "main.gif")
    sleep.sleep_ms(1000)

    while True:
        input = dialogs.prompt_text("Please enter your weight.", false_text="Cancel")
        if is_int(input):
            break

        sleep.wfi()

    ugfx.display_image(0, 0, LOCAL_FOLDER % "main.gif")
    sleep.sleep_ms(1000)

    while True:
        input = dialogs.prompt_text("Please enter your correct weight.", false_text="Cancel")
        if is_int(input):
            break

        sleep.wfi()

    ugfx.display_image(0, 0, LOCAL_FOLDER % "main.gif")

    with dialogs.WaitingMessage("Please wait.", title="Processing..."):
        sleep.sleep_ms(2000)

    show_next_step()

def show_std():
    ugfx.display_image(0, 0, LOCAL_FOLDER % "main.gif")
    dialogs.prompt_boolean("Did you have STDs?", title=APP_TITLE)
    ugfx.display_image(0, 0, LOCAL_FOLDER % "main.gif")

    with dialogs.WaitingMessage("Please wait a moment.", title="Processing..."):
        sleep.sleep_ms(6000)

    show_next_step()

def show_melody():
    ugfx.display_image(0, 0, LOCAL_FOLDER % "main.gif")
    sleep.sleep_ms(1000)

    dialogs.notice("You will now hear your personal lucky melody.", title=APP_TITLE)
    ugfx.display_image(0, 0, LOCAL_FOLDER % "main.gif")
    play_melody()

    show_next_step()

def show_repeat():
    dialogs.notice("Please repeat your personal lucky melody.", title=APP_TITLE)
    ugfx.display_image(0, 0, LOCAL_FOLDER % "rec.gif")
    sleep.sleep_ms(3000)

    dialogs.notice("PLEASE REPEAT YOUR PERSONAL LUCKY MELODY.", title=APP_TITLE)
    ugfx.display_image(0, 0, LOCAL_FOLDER % "rec.gif")
    sleep.sleep_ms(4000)

    dialogs.notice("Please repeat your personal lucky melody a bit louder.", title=APP_TITLE)
    ugfx.display_image(0, 0, LOCAL_FOLDER % "rec.gif")
    sleep.sleep_ms(4000)

    dialogs.notice("Unfortunately, this tone\nwas wrong. Please repeat\nyour personal lucky melody\nonce again.", title=APP_TITLE)
    ugfx.display_image(0, 0, LOCAL_FOLDER % "rec.gif")
    sleep.sleep_ms(6000)

    dialogs.notice("This lucky melody will help you in every situation.\nMany thanks.", title=APP_TITLE)

    show_next_step()

#
# INITIALIZATION
#

ugfx_helper.init()
speaker.enabled(True)
STEPS = [show_start, show_coin, show_coin_again, show_weight, show_std, show_melody, show_repeat]

#
# START
#

while True:
    show_next_step()

speaker.stop()
restart_to_default()
