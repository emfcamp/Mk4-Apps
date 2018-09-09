"""Mini train departure board for your badge

Configurable with which station you want to monitor
"""
___title___ = "trains"
___license___ = "MIT"
___dependencies___ = ["app", "sleep", "wifi", "http", "ugfx_helper"]
___categories___ = ["Homescreens", "Other"]

# Config

STATION_CODE = "DEP"
API_URL = "https://huxley.apphb.com/all/{}?expand=true&accessToken=D102521A-06C6-44C9-8693-7A0394C757EF"

import wifi
import ugfx
import http
import ujson
import app
import sleep
from tilda import Buttons, LED


# initialize screen
ugfx.init()
ugfx.clear()

# initial screen
ugfx.text(5, 5, "Will monitor station:", ugfx.BLACK)
ugfx.text(200, 5, STATION_CODE, ugfx.BLUE)

def get_trains():
    global station_data

    LED(LED.RED).on() # Red for total get_trains
    try:
        station_json = http.get(API_URL.format(STATION_CODE)).raise_for_status().content
        LED(LED.GREEN).on() # Green for parsing
        station_data = ujson.loads(station_json)
    except:
        print('oh poop')

    LED(LED.RED).off()
    LED(LED.GREEN).off()

get_trains()
ugfx.text(5, 20, station_data['locationName'], ugfx.RED)

# waiting until a button has been pressed
while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    sleep.wfi()


# closing
ugfx.clear()
app.restart_to_default()
