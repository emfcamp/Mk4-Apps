"""Happy accidents or unplanned, fortunate discoveries."""

___name___         = "serendipity"
___license___      = "MIT"
___dependencies___ = ["sleep", "app", "ugfx_helper"]
___categories___   = ["EMF", "Other"]

import ugfx_helper, ugfx, os, time, sleep, app
from tilda import Buttons

# initialize screen
ugfx.init()
ugfx.clear()

#ugfx.text(5, 5, "[work in progress]", ugfx.BLACK)

def show_screen():
  ugfx.display_image( 0, 0, "serendipity/main.png" )

  
show_screen()
  
while True:
  
  sleep.wfi()

  if Buttons.is_pressed( Buttons.BTN_Menu ) or \
    Buttons.is_pressed( Buttons.BTN_B ) or \
    Buttons.is_pressed( Buttons.JOY_Center):
    break
  
ugfx.clear()