"""Nyan cat
"""
___name___         = "Nyan"
___license___      = "MIT"
___dependencies___ = ["app", "homescreen", "ugfx_helper"]
___categories___   = ["Homescreens"]
___bootstrapped___ = False

from app import *
import ugfx
from homescreen import *
import ugfx_helper
import machine

from tilda import Buttons
from machine import Neopix

ext = False
bkl = False

intro_text = "Hi! I'm"
name_height = 70
intro_height = 30
max_name = 8

def cbButtonA(button_id):
	global bkl
	bkl = False	

def cbButtonB(button_id):
	global ext
	ext = True

frame = 0

def force_backlight():
	if ugfx.backlight() == 0:
		ugfx.power_mode(ugfx.POWER_ON)
	ugfx.backlight(100)

ugfx_helper.init()
ugfx.clear()

ugfx.orientation(180)
force_backlight()



#everything from here onwards is unknown
# Colour stuff
style = ugfx.Style()
style.set_enabled([ugfx.WHITE,ugfx.html_color(0x003265),ugfx.html_color(0x003265),ugfx.html_color(0x003265)])
style.set_background(ugfx.html_color(0x003265))
ugfx.set_default_style(style)
ugfx.orientation(90)

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

i = 0
while True:
	strimage = 'nyan/frame_'+str(i)+'_delay-0.07s.gif'
	ugfx.display_image(0, 0, strimage)
	i = i + 1
	if i > 11:
		i = 0
	sleep_or_exit(0.5)

app.restart_to_default()