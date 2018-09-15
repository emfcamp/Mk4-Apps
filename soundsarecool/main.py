'''
A small N channel music player a la 8088 MPH
(Demo is only two channels)

By Molive^SLP
'''

___name___         = "Arp Music Player"
___title___        = "Arp Music Player"
___license___      = "WTFPL"
___dependencies___ = ["ugfx_helper", "speaker"]
___categories___   = ["Demo","Sound"]

import speaker
import utime

from app import restart_to_default
from tilda import Buttons
	
channels = [		#Supports up to n simultaneous channels. 
					#Each channel will loop it's data independently from the others
	[				#and channels do not need the same length of data in them.
	('F4',2),		#No. of channels is decided on startup, and all channels are running at any one time.
	('D#4',2),		
	('D4',2),
	('C#4',1),
	('D#4',1),
	],
	
	##[
	##('A#3',4),
	##],
	
	##[
	##('C4',4),
	##],
	
	[
	('F5',0.125),
	('G#5',0.25),
	('F5',0.125),
	('A#5',0.25),
	('F5',0.125),
	('C6',0.25),
	('F5',0.125),
	('A#5',0.25),
	('F5',0.25),
	('G#5',0.25),
	],
	
	]

def prt(s):
	ugfx.clear()
	ugfx.text(5,5,str(s),0)
	
import ugfx
ugfx.init()

prt("RUNNING SOUND TEST")

utime.sleep(1)

prt("Use menu to reboot")

speaker.enabled(True)

channel_waits = [				#Add more of these to increase the max channel count
	[-1,utime.ticks_ms()],
	[-1,utime.ticks_ms()],
	[-1,utime.ticks_ms()],
	[-1,utime.ticks_ms()],
	]

current_channel = 0	
	
while True:						#Main awesome loop which handles all music channels. Can handle and arbitrary amount, but lags at high numbers.
	for channel in channels:
		##print(channel_waits[current_channel][1])		#Uncomment some of these for more debug info :P
		if channel_waits[current_channel][1] == 0 or channel_waits[current_channel][1] <= utime.ticks_ms():
			print("CHANGING CHANNEL "+str(current_channel))
			channel_waits[current_channel][0] += 1
			if channel_waits[current_channel][0] == len(channel):
				channel_waits[current_channel][0] = 0
			channel_waits[current_channel][1] += (channels[current_channel][channel_waits[current_channel][0]][1]*1000.0)
		speaker.note(channel[channel_waits[current_channel][0]][0])
		##print(channel[channel_waits[current_channel][0]])
		if Buttons.is_pressed(Buttons.BTN_Menu):
			print("BAIL BAIL BAIL")
			restart_to_default()
		current_channel += 1
		if current_channel == len(channels):
			current_channel = 0
		##print(current_channel)
		utime.sleep(0.03) 		#Decrease this for more accurate but weirder arps. Comment it out for insane madness
		
restart_to_default()