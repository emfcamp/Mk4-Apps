""" <your description>
"""
___name___         = "my_app"
___license___      = "MIT"
___dependencies___ = ["dialogs", "ugfx_helper", "app", "sleep"]
___categories___   = ["Other"]
___bootstrapped___ = False # Whether or not apps get downloaded on first install. Defaults to "False", mostly likely you won't have to use this at all.


import ugfx, ugfx_helper, sleep
from tilda import Sensors, Buttons
from app import *
from dialogs import *

ugfx_helper.init()
array_temp = []
array_hum = []
count = 0
grid_size = 4

while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
	ugfx.clear()

	ugfx.orientation(90)
	ugfx.Label(0, ugfx.height() - 500, ugfx.width(), 90, "Warm and wet?", justification=ugfx.Label.CENTER)

	# Title
	ugfx.set_default_font(ugfx.FONT_TITLE)
	temp_cal =  Sensors.get_tmp_temperature()-10
	string_temp = "%.1f degrees C" % temp_cal
	ugfx.Label(0, ugfx.height() - 120, ugfx.width(), 60, string_temp, justification=ugfx.Label.CENTER)


	hum =  Sensors.get_hdc_humidity()
	string_hum = "%.1f %% humidity" % hum
	ugfx.Label(0, ugfx.height() - 60, ugfx.width(), 60, string_hum, justification=ugfx.Label.CENTER)

	if count < 58:
		array_temp.append(temp_cal)
		array_hum.append(hum)
	else:
		array_temp.pop(0)
		array_hum.pop(0)
		array_temp.append(temp_cal)
		array_hum.append(hum)
	for time, temp in enumerate(array_temp):
		ugfx.area(int((time+1)*grid_size), 180-int((temp+1)*grid_size), grid_size-2, grid_size-2, ugfx.RED)
	for time, hum in enumerate(array_hum):
		ugfx.area(int((time+1)*grid_size), 200-int((hum/4+1)*grid_size), grid_size-2, grid_size-2, ugfx.BLUE)
	count = count + 1
	sleep.sleep_ms(10000)

restart_to_default()