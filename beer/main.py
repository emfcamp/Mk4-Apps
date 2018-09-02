"""What's on tap?!

Get up to date information on what's in stock at The Robot Arms!
"""
___name___         = "beer"
___license___      = "MIT"
___dependencies___ = ["app", "sleep", "wifi", "http", "ugfx_helper"]
___categories___   = ["EMF"]

import wifi, ugfx, http, ujson, app, sleep
from tilda import Buttons, LED

orientation = 270

def get_beer():
    global bar, stock

    LED(LED.RED).on()
    try:
        bar_json = http.get("https://bar.emf.camp/location/Bar.json").raise_for_status().content
        stock_json = http.get("https://bar.emf.camp/stock.json").raise_for_status().content
        bar = ujson.loads(bar_json)
        stock = ujson.loads(stock_json)
    except: 
        print('oh poop')

    LED(LED.RED).off()
    draw_screen()

def draw_screen():
    global bar, stock

    ugfx.clear(ugfx.BLACK)
    ugfx.text(65, 5, "what's on tap?", ugfx.RED)
    ugfx.line(5, 20, ugfx.width(), 20, ugfx.GREY)

    for idx, beer in enumerate(bar['location']):

        remaining = 0

        for item in stock['stock']:
            if item['description'] == beer['description']:
                remaining = float(item['remaining'])

        ugfx.text(5, 22 + idx*15, beer['description'][:28], ugfx.WHITE)
        ugfx.text(202, 22 + idx*15, '!' if (remaining < 30) else ' ', ugfx.RED)
        ugfx.text(210, 22 + idx*15, "{:>4}".format(beer['price']), ugfx.WHITE)

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
ugfx.set_default_font(ugfx.FONT_FIXED)

s=ugfx.Style()
s.set_enabled([ugfx.WHITE, ugfx.BLACK, ugfx.BLACK, ugfx.GREY])
s.set_background(ugfx.BLACK)
ugfx.set_default_style(s)

Buttons.enable_interrupt(Buttons.BTN_A, lambda button_id:get_beer(), on_press=True, on_release=False)
Buttons.enable_interrupt(Buttons.BTN_B, lambda button_id:toggle_orientation(), on_press=True, on_release=False)
Buttons.enable_interrupt(Buttons.BTN_Menu, lambda button_id:app.restart_to_default(), on_press=True, on_release=False)

ugfx.text(5, 10, "Instructions:", ugfx.WHITE)
ugfx.text(5, 30, "Press the A button to refresh", ugfx.WHITE)
ugfx.text(5, 45, "Press the B button to rotate", ugfx.WHITE)
ugfx.text(5, 60, "Press the Menu button to exit", ugfx.WHITE)
ugfx.text(5, 90, "!", ugfx.RED)
ugfx.text(15, 90, "means the stock is low", ugfx.WHITE)
ugfx.text(5, 120, "Loading data from the bar...", ugfx.WHITE)


get_beer()

while True:
    sleep.wfi()

ugfx.clear()
app.restart_to_default()