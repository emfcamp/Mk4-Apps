"""Camp Holland app
"""
___name___         = "Holland"
___license___      = "MIT"
___dependencies___ = ["app", "sim800", "ugfx_helper"]
___categories___   = ["Villages"]
___bootstrapped___ = True

from app import *
from dialogs import *
import ugfx
import ugfx_helper

from machine import Neopix

def show_screen(color1, color2, text, text2="", flip=False):
	if flip:
		ugfx.orientation(90)
	ugfx.clear(ugfx.html_color(color1))
	ugfx.set_default_font(ugfx.FONT_NAME)
	ugfx.text(0, 100, text, ugfx.html_color(color2))
	ugfx.set_default_font(ugfx.FONT_SMALL)
	ugfx.text(0, 200, text2, ugfx.html_color(color2))
	if flip:
		ugfx.orientation(270)

def show_vip(inv):
	if (inv):
		show_screen(0xFFFFFF, 0xFFA400, "Dutch VIP", "", True)
	else:
		show_screen(0xFFA400, 0xFFFFFF, "Dutch VIP", "", True)

def show_flag():
	ugfx.display_image(0, 0, "holland/nederland.png")

def show_boot():
	ugfx.display_image(0, 0, "holland/start.png")

ugfx_helper.init()
ugfx.clear()
show_boot()

import sim800
import time
from tilda import Buttons

sim800.poweron()
n = Neopix()

vip = False
vip_inv = False
strobe = False

def cbButtonA(button_id):
	global vip
	vip = False
	show_flag()

def cbButtonB(button_id):
	global vip
	vip = True
	show_vip(vip_inv)
	
def load():
	global vip
	vip = False
	show_screen(0x000000, 0xFFFFFF, "LOADING")
	print("Copy AMR")
	sim800.fscreate("REC\\1.AMR")
	f = open('holland/wilhelmus.amr', 'r')
	data = f.read(256)
	c = len(data)
	sim800.fswrite("REC\\1.AMR", data, True)
	pr = c
	while (c>0):
		data = f.read(256)
		c = len(data)
		sim800.fswrite("REC\\1.AMR", data, False)
		pr = pr + c
		show_screen(0x000000, 0xFFFFFF, "LOADING", str(pr))
		print(str(pr))
	f.close()
	show_screen(0x000000, 0xFFFFFF, "DONE")
	
	
wilhelmus = (
    ("D", 300), ("G", 300), ("G", 300), ("A", 300), ("B", 300), ("C2", 300), ("A", 300), ("B", 300), ("A", 300), ("B", 300), ("C2", 300), ("B", 300), ("A", 300), ("G", 300), ("A", 600), ("G", 600), ("D", 300),
    ("G", 300), ("G", 300), ("A", 300), ("B", 300), ("C2", 300), ("A", 300), ("B", 300), ("A", 300), ("B", 300), ("C", 300), ("B", 300), ("A", 600), ("G", 600), ("A", 600), ("G", 600), ("B", 300), ("C", 300),
)

freq = {
    "C":   2616,
    "D":   2936,
    "E":   3296,
    "F":   3492,
    "G":   3920,
    "A":   4400,
    "B":   4938,
    "C2":  5322,
}
	
def cbButtonCall(button_id):
	sim800.speakervolume(100)
	show_screen(0x000000, 0xFFFFFF, "TONE")
	for note, length in wilhelmus:
		sim800.playtone(freq.get(note, 9000), length, False)

def cbButton1(button_id):
	global vip
	vip = False
	ugfx.display_image(0, 0, "holland/eu.png")
	
def cbButton2(button_id):
	sim800.speakervolume(100)
	sim800.stopplayback()
	show_screen(0x000000, 0xFFFFFF, "PLAY")
	a = sim800.startplayback(1,0,100)
	if not a:
		sim800.fsrm("REC\\1.AMR")
		sim800.fsrm("REC\\2.AMR")
		sim800.fsrm("REC\\3.AMR")
		load()
		show_screen(0x000000, 0xFFFFFF, "PLAY")
		sim800.startplayback(1,0,100)
	
def cbButton3(button_id):
	show_screen(0x000000, 0xFFFFFF, "STOP")
	sim800.stopplayback()

def cbButton4(button_id):
	global vip
	vip = False
	ugfx.display_image(0, 0, "holland/otter.png")
	
def cbButton5(button_id):
	n.display([0xFFFFFF, 0xFFFFFF])

def cbButton6(button_id):
	n.display([0x000000, 0x000000])
	
def cbButton7(button_id):
	global vip
	vip = False
	show_boot()

def cbButton8(button_id):
	global strobe
	strobe = True

def cbButton9(button_id):
	global strobe
	strobe = False
	
def cbButtonHash(button_id):
	global vip
	vip = False
	ugfx.display_image(0, 0, "holland/brenno.png")
		
Buttons.enable_interrupt(
	Buttons.BTN_Call,
	cbButtonCall,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_A,
	cbButtonA,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_B,
	cbButtonB,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_1,
	cbButton1,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_2,
	cbButton2,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_3,
	cbButton3,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_4,
	cbButton4,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_5,
	cbButton5,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_6,
	cbButton6,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_7,
	cbButton7,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_8,
	cbButton8,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_9,
	cbButton9,
	on_press=True,
	on_release=False);

Buttons.enable_interrupt(
	Buttons.BTN_Hash,
	cbButtonHash,
	on_press=True,
	on_release=False);

vip = True
aaa = False

while True:
	if vip_inv:
		vip_inv = False
	else:
		vip_inv = True
	if vip:
		show_vip(vip_inv)
	if strobe:
		if aaa:
			n.display([0xFFA500, 0xFFA500])
			aaa = False
		else:
			n.display([0x000000, 0x000000])
			aaa = True
		if not vip:
			time.sleep(0.1)
	else:
		time.sleep(0.1)
