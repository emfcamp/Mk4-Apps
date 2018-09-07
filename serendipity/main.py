"""Happy accidents or unplanned, fortunate discoveries."""

___name___         = "serendipity"
___license___      = "MIT"
___dependencies___ = ["sleep", "app", "ugfx_helper"]
___categories___   = ["Villages"]

import ugfx_helper, os, wifi, ugfx, http, time, sleep, app
from tilda import Buttons

# initialize screen
ugfx_helper.init()
ugfx.clear(ugfx.BLACK)

img = [ugfx.Image("serendipity/sun.png"),
       ugfx.Image("serendipity/world.png")]

ugfx.backlight(100)

n = 0
ugfx.display_image( 0, 0, img[n] )

while True:
    
    if Buttons.is_pressed(Buttons.BTN_B):
      break
    elif Buttons.is_pressed(Buttons.BTN_A):
      n = (n+1) % 2
      ugfx.display_image( 0, 0, img[n] )

ugfx.clear()
app.restart_to_default()