"""Default homescreen

This is the default homescreen for the Tilda Mk4.
It gets automatically installed when a badge is
newly activated or reset.
"""

___name___         = "Homescreen (Default)"
___license___      = "GPL"
___categories___   = ["homescreen"]
___launchable___   = False
___bootstrapped___ = True

print("there")
import ugfx, homescreen

homescreen.init(color = 0xe4ffdb)

ugfx.display_image(0, 0, "home_default/bg.gif")
ugfx.text(20, 20, homescreen.name(), ugfx.BLACK)
