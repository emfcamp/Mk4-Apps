"""Happy accidents or unplanned, fortunate discoveries."""

___name___         = "serendipity"
___license___      = "MIT"
___dependencies___ = ["sleep", "app", "ugfx_helper", "serendipity/world.png", "serendipity/sun.png"]
___categories___   = ["EMF", "Other"]

import ugfx_helper, os, wifi, ugfx, http, time, sleep, app
from tilda import Buttons

# initialize screen
ugfx_helper.init()
ugfx.clear(ugfx.BLACK)

#ugfx.text(5, 5, "[work in progress]", ugfx.BLACK)

sun = ugfx.Image("serendipity/seresun.png")
sun = ugfx.Image("serendipity/world.png")

ugfx.backlight(100)

n = 0
while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    
    ugfx.display_image( 0, 90, "shared/nyan/{}.png".format(n) )
    n = (n+1) % 12
    sleep.sleep_ms(10)

ugfx.clear()
app.restart_to_default()