"""Happy accidents or unplanned, fortunate discoveries."""

___name___         = "serendipity"
___license___      = "MIT"
___dependencies___ = ["sleep", "app"]
___categories___   = ["EMF", "Other"]

import ugfx, os, time, sleep, app


# initialize screen
ugfx.init()
ugfx.clear()

#ugfx.text(5, 5, "[work in progress]", ugfx.BLACK)

def draw_furniture():
  ugfx.display_image( 0, 0, "serendipity/main.png" )
