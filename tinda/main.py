"""
TiNDA: A dating app for TiLDA. Find your perfect EMF match!
"""
___name___ = "tinda"
___license___ = "WTFPL"
___dependencies___ = ["app", "buttons", "database", "dialogs", "http", "sleep", "ugfx_helper"]
___categories___ = ["Other", "EMF"]

import database
import dialogs
import http
import json
import sleep
import ugfx
import ugfx_helper

from app import *
from buttons import is_pressed
from tilda import Buttons

#
# CONFIGURATION
#

ENABLE_SPLASH_SCREEN = True

APP_TITLE = "TiNDA"
APP_COLOUR = ugfx.html_color(0x800080)
LOCAL_FOLDER = 'tinda/%s'
CARD_API_ENDPOINT = "http://d1obbkgck7qwwy.cloudfront.net"
QR_API_ENDPOINT = "http://api.qrserver.com/v1/create-qr-code/?size=231x231&format=gif&data=%s"

DB_KEY_ANSWERS = "tinda_app_answers"
DB_KEY_CARD = "tinda_app_card"
DB_KEY_QR = "tinda_app_qr"

#
# FUNCTIONS
#
def get_questions():
    with open(LOCAL_FOLDER % "questions.json", "r") as f:
        data = json.load(f)
        return data["questions"]

def get_image_urls(answers):
    try:
        with dialogs.WaitingMessage("Sending data...", title=APP_TITLE):
            response = http.post(CARD_API_ENDPOINT, json={"answers": answers}).raise_for_status()

            data = response.json()
            url = json.loads(data["body"])["url"]

            database.set(DB_KEY_CARD, url)
            database.set(DB_KEY_QR, QR_API_ENDPOINT % url)

            return True
    except Exception as ex:
        dialogs.notice(repr(ex), title="%s - Download failed" % APP_TITLE)

#
# VIEWS
#

def show_spash_screen():
    if ENABLE_SPLASH_SCREEN:
        ugfx.display_image(0, 0, LOCAL_FOLDER % "splash.gif")
        sleep.sleep_ms(1000)

def show_menu():
    menu_items = [
        {"title": "Answer questions", "function": show_questions},
        {"title": "View emoji card", "function": show_card},
        {"title": "Share emoji card", "function": show_share},
        {"title": "Manual", "function": show_manual}
    ]

    option = dialogs.prompt_option(
        menu_items, none_text="Exit", text="Menu", title=APP_TITLE)

    if option:
        option["function"]()

def show_manual():
    ugfx.clear(APP_COLOUR)
    window = ugfx.Container(0, 0, ugfx.width(), ugfx.height())
    window.show()
    window.text(5, 10, "TiNDA: Dating app for TiLDA", ugfx.BLACK)
    window.text(5, 30, "Find your perfect EMF match", ugfx.BLACK)
    window.line(0, 50, ugfx.width(), 50, ugfx.BLACK)

    window.text(5, 60, "Step 1: Answer all questions", ugfx.BLACK)
    window.text(5, 80, "and receive an emoji card.", ugfx.BLACK)

    window.text(5, 110, "Step 2: Compare cards with", ugfx.BLACK)
    window.text(5, 130, "other people and count", ugfx.BLACK)
    window.text(5, 150, "matching emoji.", ugfx.BLACK)

    window.text(5, 180, "Step 3: <3", ugfx.BLACK)

    while ((not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu))):
        sleep.wfi()

def show_questions():
    answer_items = []
    answers = None

    questions = get_questions()

    if questions:
        for i, question in enumerate(questions):
            # add 3rd option "skip" to all questions
            question["options"].append({"title": "Skip", "value": "0"})

            title = "TiNDA - Question %i/%i" % (i + 1, len(questions))
            option = dialogs.prompt_option(question["options"], text=question["text"], select_text="OK", none_text="Skip", title=title)

            if option:
                answer_items.append(option["value"])
            else:
                answer_items.append("0")

        answers = "".join(answer_items)

        database.set(DB_KEY_ANSWERS, answers)

        if get_image_urls(answers):
            show_card()

def show_card():
    url = database.get(DB_KEY_CARD)

    if url:
        try:
            with dialogs.WaitingMessage("Loading data...", title=APP_TITLE):
                image = http.get(url).raise_for_status().content
                ugfx.display_image(0, 0, bytearray(image))

                while ((not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu))):
                    sleep.wfi()
        except Exception as ex:
            dialogs.notice(repr(ex), title="%s - Download failed" % APP_TITLE)
    else:
        dialogs.notice("Please answer the questions first", title=APP_TITLE)
        show_menu()

def show_share():
    ugfx.clear(APP_COLOUR)
    url = database.get(DB_KEY_QR)

    if url:
        dialogs.notice("Scan the QR code with your phone and share your emoji card online.", title=APP_TITLE)

        try:
            with dialogs.WaitingMessage("Loading data...", title=APP_TITLE):
                image = http.get(url).raise_for_status().content
                ugfx.clear(APP_COLOUR)
                ugfx.display_image(5, 45, bytearray(image))

                while (not is_pressed(Buttons.BTN_B)) and (not is_pressed(Buttons.BTN_Menu)):
                    sleep.wfi()
        except Exception as ex:
            dialogs.notice(repr(ex), title="%s - Download failed" % APP_TITLE)
    else:
        dialogs.notice("Please answer the questions first", title=APP_TITLE)
        show_menu()

#
# INITIALIZATION
#

ugfx_helper.init()
ugfx.clear(APP_COLOUR)

#
# START
#

show_spash_screen()

while True:
    show_menu()

    while (not is_pressed(Buttons.BTN_B)) and (not is_pressed(Buttons.BTN_Menu)):
        sleep.wfi()

restart_to_default()
