"""What's on tap?!
"""
___name___         = "beer"
___license___      = "MIT"
___dependencies___ = ["app", "sleep", "wifi", "http", "ugfx_helper"]
___categories___   = ["EMF"]

import wifi, ugfx, http, ujson, app
from tilda import Buttons
from time import sleep

ugfx.init()
ugfx.clear()

while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):

    bar_json = http.get("https://bar.emf.camp/location/Bar.json").raise_for_status().content
    bar = ujson.loads(bar_json)

    for idx, beer in enumerate(bar['location']):
        ugfx.text(5, 5+idx*15, beer['description'], ugfx.RED)

    sleep(60)

app.restart_to_default()