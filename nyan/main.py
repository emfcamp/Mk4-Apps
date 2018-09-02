"""Nyan Cat Animation!"""

___name___         = "nyan"
___license___      = "MIT"
___dependencies___ = ["sleep", "app", "ugfx_helper", 
                      "shared/nyan/0.png",
                      "shared/nyan/1.png",
                      "shared/nyan/2.png",
                      "shared/nyan/3.png",
                      "shared/nyan/4.png",
                      "shared/nyan/5.png",
                      "shared/nyan/6.png",
                      "shared/nyan/7.png",
                      "shared/nyan/8.png",
                      "shared/nyan/9.png",
                      "shared/nyan/10.png",
                      "shared/nyan/11.png"]
                      
___categories___   = ["FUN", "Homescreens"]

import ugfx_helper, os, wifi, ugfx, http, time, sleep, app
from tilda import Buttons

# initialize screen
ugfx_helper.init()
ugfx.clear(ugfx.BLACK)

ugfx.backlight(100)

n = 0
while True:
    ugfx.display_image( 0, 90, "shared/nyan/{}.png".format(n) )
    n = (n+2) % 12
    sleep.sleep_ms(10)
    
    if Buttons.is_pressed(Buttons.BTN_B):
      break

ugfx.clear()
app.restart_to_default()