"""Launcher for apps currently installed"""

___name___         = "Launcher"
___license___      = "MIT"
___categories___   = ["System"]
___launchable___   = False
___bootstrapped___ = True

import ugfx

ugfx.clear()
apps = range(1, 10)

cols = 4


for i, p in enumerate(apps):
    logical_x = i % cols
    logical_y = i // cols
    x = logical_x * width




print("launcher")
