"""Nyan Cat Animation! Rotate the screen with 'A'."""

___name___         = "nyan"
___license___      = "MIT"
___dependencies___ = ["sleep", "app", "ugfx_helper", 
                      "shared/nyan/0.png",
                      "shared/nyan/1.png",
                      "shared/nyan/2.png",
                      "shared/nyan/3.png",
                      "shared/nyan/4.png",
                      "shared/nyan/5.png"]
                      
___categories___   = ["Homescreens", "Other"]

import ugfx_helper, os, wifi, ugfx, http, time, sleep, app
from tilda import Buttons

# initialize screen
ugfx_helper.init()
ugfx.clear(ugfx.BLACK)

ugfx.backlight(100)

n = 0
r = 270
while True:
    ugfx.display_image( 0, 90, "shared/nyan/{}.png".format(n) )
    n = (n+1) % 6
    sleep.sleep_ms(10)
    
    if Buttons.is_pressed(Buttons.BTN_B):
      break
    elif Buttons.is_pressed(Buttons.BTN_A):
      r = (r + 180) % 360
      ugfx.clear(ugfx.BLACK)
      ugfx.orientation(r)

ugfx.clear()
app.restart_to_default()