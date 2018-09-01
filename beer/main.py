"""What's on tap?!
"""
___name___         = "beer"
___license___      = "MIT"
___dependencies___ = ["app", "sleep", "wifi", "http", "ugfx_helper"]
___categories___   = ["EMF"]

import wifi, ugfx, http, ujson, app, sleep
from tilda import Buttons, LED

orientation = 270

def get_beer():
    global bar
    LED(LED.RED).on()
    try:
        bar_json = http.get("https://bar.emf.camp/location/Bar.json").raise_for_status().content
        bar = ujson.loads(bar_json)
    except: 
        print('oh poop')
    LED(LED.RED).off()
    draw_screen()

def draw_screen():

    ugfx.clear(ugfx.BLACK)
    ugfx.text(60, 5, "what's on tap?", ugfx.RED)
    ugfx.line(5, 20, ugfx.width(), 20, ugfx.GREY)
    for idx, beer in enumerate(bar['location']):
        ugfx.text(5, 22 + idx*15, beer['description'], ugfx.WHITE)

def toggle_orientation():
    global orientation
    if orientation == 90:
        ugfx.orientation(270)
        orientation = 270
        draw_screen()
    else:
        ugfx.orientation(90)
        orientation = 90
        draw_screen()

ugfx.init()
ugfx.clear(ugfx.BLACK)

Buttons.enable_interrupt(Buttons.BTN_A, lambda button_id:get_beer(), on_press=True, on_release=False)
Buttons.enable_interrupt(Buttons.BTN_B, lambda button_id:toggle_orientation(), on_press=True, on_release=False)
Buttons.enable_interrupt(Buttons.BTN_Menu, lambda button_id:app.restart_to_default(), on_press=True, on_release=False)


ugfx.text(5, 10, "Instructions:", ugfx.WHITE)
ugfx.text(5, 30, "Press the A button to refresh", ugfx.WHITE)
ugfx.text(5, 45, "Press the B button to rotate", ugfx.WHITE)
ugfx.text(5, 60, "Press the Menu button to exit", ugfx.WHITE)
ugfx.text(5, 95, "Loading data from the bar...", ugfx.WHITE)

get_beer()

while True:
    sleep.wfi()

ugfx.clear()
app.restart_to_default()