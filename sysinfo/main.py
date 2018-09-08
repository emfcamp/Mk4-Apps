"""This app tests all the onboard sensors and system info"""

___title___        = "System Info"
___license___      = "MIT"	
___dependencies___ = ["sleep", "app", "sim800"]
___categories___   = ["EMF", "System"]
___bootstrapped___ = True

#import ugfx, os, time, sleep, app, sim800

import ugfx, app, sim800
import os
from tilda import Buttons
from tilda import Sensors
from machine import ADC
from time import sleep

mag = ADC(ADC.ADC_HALLEFFECT)

status_height = 20

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_FIXED)

simversion = sim800.getfirmwarever()[9:]
simphonenumber = sim800.getmynumber()
simoperator = sim800.currentoperator()

if simphonenumber == None or len(simphonenumber) == 0 :
    ugfx.Label(5, 155, 240, 15, "No Number Yet")
else:
    ugfx.Label(5, 155, 240, 15, simphonenumber)

if simoperator == None or len(simoperator) == 0 :
    ugfx.Label(5, 170, 240, 15, "No Operator Yet")
else:
    ugfx.Label(5, 170, 240, 15, "Your network is " + simoperator)

ugfx.Label(5, 185, 240, 15, simversion)

ugfx.Label(5, 215, 240, 30, "Badge firmware version:\n{}".format(os.uname().version))

ugfx.Label(5, 300, 240, 15, "** Hold A or B or MENU to exit **")


while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):

    ugfx.Label(5, 5, 240, 15,  "Temperature (tmp) : {:.2f} C".format(Sensors.get_tmp_temperature()))
    ugfx.Label(5, 20, 240, 15, "Temperature (hdc) : {:.2f} C".format(Sensors.get_hdc_temperature()))
    ugfx.Label(5, 35, 240, 15, "Humidity    (hdc) : {:.2f} %".format(Sensors.get_hdc_humidity()))
    ugfx.Label(5, 50, 240, 15, "Light       (opt) : {:.2f} Lux".format(Sensors.get_lux()))
    ugfx.Label(5, 65, 240, 15, "Mag Field:  (drv) : {:.2f}    ".format(mag.convert()))
    ugfx.Label(5, 80, 240, 15, "Sensor samplerate : {} ms".format(Sensors.sample_rate()))

    charging = Sensors.get_charge_status()
    if charging == Sensors.BAT_PRE_CHARGING or charging == Sensors.BAT_FAST_CHARGING:
        ugfx.Label(5, 110, 240, 15, "Battery is        : charging")
    elif charging == Sensors.BAT_DONE_CHARGING:
        ugfx.Label(5, 110, 240, 15, "Battery is        : full")
    elif charging == Sensors.BAT_NOT_CHARGING:
        ugfx.Label(5, 110, 240, 15, "Battery is        : discharging")

    ugfx.Label(5, 125, 240, 15,     "Battery is        : {:.2f} %".format(sim800.batterycharge()))

    sleep(2)

ugfx.clear()

app.restart_to_default()	
