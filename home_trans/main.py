"""Trans homescreen

A version of the home screen that has a trans flag.
Press 0 to go back to normal or 8 to show the flag.
Hold * to activate all LEDs for use as a torch.
"""

___name___         = "Homescreen (Trans)"
___license___      = "MIT"
___categories___   = ["Homescreens"]
___dependencies___ = ["homescreen", "shared/logo.png"]
___launchable___   = False
___bootstrapped___ = False

import ugfx
from homescreen import *
import time
from tilda import Buttons
from machine import Pin
from machine import Neopix

torch = Pin(Pin.GPIO_FET)
neo = Neopix()

init()

# Padding for name
intro_height = 30
intro_text = "Hi! I'm"
name_height = 64
status_height = 20
info_height = 30
logo_path = "shared/logo.png"
trans_logo_path = "home_trans/logo.png"
logo_height = 150
logo_width = 56

# Maximum length of name before downscaling
max_name = 8

torch_on = False

# Background stuff
ugfx.clear(ugfx.html_color(0x55cdfc))
# Colour stuff
style = ugfx.Style()
style.set_enabled([ugfx.BLACK, ugfx.html_color(0x55cdfc), ugfx.html_color(0x55cdfc), ugfx.html_color(0x55cdfc)])
style.set_background(ugfx.html_color(0x55cdfc))
ugfx.set_default_style(style)
ugfx.display_image(0, 0, "home_trans/trans.png")

# Logo stuff
ugfx.display_image(
    int((ugfx.width() - logo_width) / 2),
    int((ugfx.height() - logo_height) / 2)+9,
    trans_logo_path
)

# Draw for people to see
ugfx.orientation(90)
# Draw introduction
style.set_enabled([ugfx.BLACK, ugfx.html_color(0xf8b0be), ugfx.html_color(0xf8b0be), ugfx.html_color(0xf8b0be)])
style.set_background(ugfx.html_color(0xf8b0be))
ugfx.set_default_style(style)
ugfx.set_default_font(ugfx.FONT_TITLE)
ugfx.Label(0, ugfx.height() - name_height - intro_height, ugfx.width(), intro_height, intro_text, justification=ugfx.Label.CENTER)
# Prepare to draw name
style.set_enabled([ugfx.BLACK, ugfx.html_color(0x55cdfc), ugfx.html_color(0x55cdfc), ugfx.html_color(0x55cdfc)])
style.set_background(ugfx.html_color(0x55cdfc))
ugfx.set_default_style(style)
# Process name
name_setting = name("Set your name in the settings app")
if len(name_setting) <= max_name:
	ugfx.set_default_font(ugfx.FONT_NAME)
else:
	ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
# Draw name
ugfx.Label(0, ugfx.height() - name_height, ugfx.width(), name_height, name_setting, justification=ugfx.Label.CENTER)

# Draw for wearer to see
ugfx.orientation(270)
ugfx.set_default_font(ugfx.FONT_SMALL)
status = ugfx.Label(0, ugfx.height() - status_height, ugfx.width(), status_height, "", justification=ugfx.Label.LEFT)

def draw_badge():
	style.set_enabled([ugfx.WHITE, ugfx.html_color(0x800080), ugfx.html_color(0x800080), ugfx.html_color(0x800080)])
	style.set_background(ugfx.html_color(0x800080))
	ugfx.clear(ugfx.html_color(0x800080))
	ugfx.set_default_style(style)
	# Logo stuff
	ugfx.display_image(
		int((ugfx.width() - logo_width) / 2),
		int((ugfx.height() - logo_height) / 2),
		logo_path
	)

	# Draw for people to see
	ugfx.orientation(90)
	# Draw introduction
	ugfx.set_default_font(ugfx.FONT_TITLE)
	ugfx.Label(0, ugfx.height() - name_height - intro_height, ugfx.width(), intro_height, intro_text, justification=ugfx.Label.CENTER)
	# Process name
	name_setting = name("Set your name in the settings app")
	if len(name_setting) <= max_name:
		ugfx.set_default_font(ugfx.FONT_NAME)
	else:
		ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
	# Draw name
	ugfx.Label(0, ugfx.height() - name_height, ugfx.width(), name_height, name_setting, justification=ugfx.Label.CENTER)

	# Draw for wearer to see
	ugfx.orientation(270)
	ugfx.set_default_font(ugfx.FONT_SMALL)
	status = ugfx.Label(0, ugfx.height() - status_height, ugfx.width(), status_height, "", justification=ugfx.Label.LEFT)

def draw_trans():
	style.set_enabled([ugfx.BLACK, ugfx.html_color(0x55cdfc), ugfx.html_color(0x55cdfc), ugfx.html_color(0x55cdfc)])
	style.set_background(ugfx.html_color(0x55cdfc))
	ugfx.set_default_style(style)
	ugfx.display_image(0, 0, "home_trans/trans.png")

	# Logo stuff
	ugfx.display_image(
	    int((ugfx.width() - logo_width) / 2),
	    int((ugfx.height() - logo_height) / 2)+9,
	    trans_logo_path
	)

	# Draw for people to see
	ugfx.orientation(90)
	# Draw introduction
	style.set_enabled([ugfx.BLACK, ugfx.html_color(0xf8b0be), ugfx.html_color(0xf8b0be), ugfx.html_color(0xf8b0be)])
	style.set_background(ugfx.html_color(0xf8b0be))
	ugfx.set_default_style(style)
	ugfx.set_default_font(ugfx.FONT_TITLE)
	ugfx.Label(0, ugfx.height() - name_height - intro_height, ugfx.width(), intro_height, intro_text, justification=ugfx.Label.CENTER)
	# Prepare to draw name
	style.set_enabled([ugfx.BLACK, ugfx.html_color(0x55cdfc), ugfx.html_color(0x55cdfc), ugfx.html_color(0x55cdfc)])
	style.set_background(ugfx.html_color(0x55cdfc))
	ugfx.set_default_style(style)
	# Process name
	name_setting = name("Set your name in the settings app")
	if len(name_setting) <= max_name:
		ugfx.set_default_font(ugfx.FONT_NAME)
	else:
		ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
	# Draw name
	ugfx.Label(0, ugfx.height() - name_height, ugfx.width(), name_height, name_setting, justification=ugfx.Label.CENTER)

	# Draw for wearer to see
	ugfx.orientation(270)
	ugfx.set_default_font(ugfx.FONT_SMALL)
	status = ugfx.Label(0, ugfx.height() - status_height, ugfx.width(), status_height, "", justification=ugfx.Label.LEFT)

# update loop
while True:
	text = "";
	value_battery = battery()
	if value_battery:
		text += "%s%%" % int(value_battery)
	if Buttons.is_pressed(Buttons.BTN_Star):
		if torch_on:
			torch_on = False
			torch.off()
			neo.display([0,0])
		else:
			torch_on = True
			torch.on()
			neo.display([0xffffff,0xffffff])
	if Buttons.is_pressed(Buttons.BTN_8):
		draw_trans()
	if Buttons.is_pressed(Buttons.BTN_0):
		draw_badge()
	status.text(text)
	sleep_or_exit(0.5)
