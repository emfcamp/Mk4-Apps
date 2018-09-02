"""This is a simple hello world app"""

___name___         = "Hello World"
___license___      = "MIT"
___dependencies___ = ["sleep", "app"]
___categories___   = ["EMF"]

import ugfx, sleep, app


# initialize screen
ugfx.init()
ugfx.clear()

# show text
ugfx.text(5, 5, "Hello World!", ugfx.BLACK)


# waiting until a button has been pressed
while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    sleep.wfi()


# closing
ugfx.clear()
app.restart_to_default()
