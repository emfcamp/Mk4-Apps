''' Random card generator, includes Base Set, The First Expansion, The Second Expansion, The Third Expansion, The Fourth Expansion, The Fifth Expansion, The Sixth Expansion, Green Box Expansion, 90s Nostalgia Pack, Box Expansion, Fantasy Pack, Food Pack, Science Pack and World Wide Web Pack '''

___name___         = "Cards Against EMF"
___license___      = ["MIT"]
___dependencies___ = ["ugfx_helper", "sleep"]
___categories___   = ["Games"]
___bootstrapped___ = False # Whether or not apps get downloaded on first install. Defaults to "False", mostly likely you won't have to use this at all.

import ugfx, json, random

from tilda import Buttons
from app import restart_to_default

ugfx.init()
ugfx.clear()
ugfx.text(10, 10, "CARDS AGAINST EMF", ugfx.BLACK)
ugfx.text(10, 40, "A for a question", ugfx.BLACK)
ugfx.text(10, 60, "B for an answer", ugfx.BLACK)
ugfx.text(10, 80, "MENU to exit", ugfx.BLACK)

b=ugfx.Style()
b.set_background(ugfx.BLACK)
b.set_enabled([ugfx.WHITE, ugfx.BLACK, ugfx.BLACK, ugfx.BLACK]) # sets the style for when something is enabled
w=ugfx.Style()
w.set_background(ugfx.WHITE)

with open("cards_against_emf/cards.json") as data:
    d = json.load(data)

def get_black():
    x = random.randint(1, 320)
    ugfx.clear(ugfx.html_color(0x000000))
    text = str(d["blackCards"][x]["text"])
    ugfx.Label(0, 0, 240, 400, text, style=b)

def get_white():
    y = random.randint(1, 1271)
    ugfx.clear(ugfx.html_color(0xffffff))
    text = str(d["whiteCards"][y])
    ugfx.Label(0, 0, 240, 400, text, style=w)

Buttons.enable_interrupt(
    Buttons.BTN_A,
    lambda button_id:get_black(),
    on_press=True,
    on_release=False)

Buttons.enable_interrupt(
    Buttons.BTN_B,
    lambda button_id:get_white(),
    on_press=True,
    on_release=False)

Buttons.enable_interrupt(
    Buttons.BTN_Menu,
    lambda button_id:restart_to_default(),
    on_press=True,
    on_release=False)
