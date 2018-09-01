"""What's on tap?!
"""
___name___         = "beer"
___license___      = "MIT"
___dependencies___ = ["app", "sleep", "wifi", "http", "ugfx_helper"]
___categories___   = ["EMF"]

import wifi, ugfx, http, ujson, app, sleep
from tilda import Buttons, LED

def get_beer():
    global bar

    LED(LED.RED).on()
    bar_json = http.get("https://bar.emf.camp/location/Bar.json").raise_for_status().content
    bar = ujson.loads(bar_json)
    LED(LED.RED).off()

def draw_screen():
    get_beer()
    ugfx.clear(ugfx.BLACK)
    ugfx.text(60, 5, "what's on tap?", ugfx.RED)
    ugfx.line(5, 20, ugfx.width(), 20, ugfx.GREY)
    for idx, beer in enumerate(bar['location']):
        ugfx.text(5, 22 + idx*15, beer['description'], ugfx.WHITE)

ugfx.init()
ugfx.clear(ugfx.BLACK)

Buttons.enable_interrupt(Buttons.BTN_A, lambda button_id:draw_screen(), on_press=True, on_release=False)
Buttons.enable_interrupt(Buttons.BTN_B, lambda button_id:app.restart_to_default(), on_press=True, on_release=False)

ugfx.text(5, 10, "Instructions:", ugfx.WHITE)
ugfx.text(5, 30, "Press the A button to refresh", ugfx.WHITE)
ugfx.text(5, 45, "Press the B button to exit", ugfx.WHITE)
ugfx.text(5, 75, "Loading data from the bar...", ugfx.WHITE)

draw_screen()

while True:
    sleep.wfi()

ugfx.clear()
app.restart_to_default()