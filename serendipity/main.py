"""This is a simple hello world app"""

___name___         = "serendipity"
___license___      = "MIT"
___dependencies___ = ["sleep", "app"]
___categories___   = ["EMF", "Other"]

import ugfx, os, time, sleep, app


# initialize screen
ugfx.init()
ugfx.clear()

ugfx.text(5, 5, "[work in progress]", ugfx.BLACK)
