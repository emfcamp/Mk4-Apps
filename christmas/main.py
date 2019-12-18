"""
Merry Christmas EMF People !
"""

___title___        = "Christmas"
___license___      = ""
___categories___   = ["Sound"]
___dependencies___ = ["speaker", "ugfx_helper", "app", "ugfx", "sleep","time" ]

import ugfx_helper, ugfx,time, sleep, app,speaker
from app import restart_to_default
import time
from homescreen import init, sleep_or_exit

ugfx_helper.init()
ugfx.clear(ugfx.BLACK)
ugfx.text(5, 5, "Buttons: They Do Nothing !", ugfx.WHITE)
ugfx.text(5, 25, "Reboot When Your Done !", ugfx.WHITE)
ugfx.text(40, 80, "Merry Christmas", ugfx.WHITE)
ugfx.text(90, 100, "2019", ugfx.WHITE)
ugfx.text(50, ugfx.height()-80, "Not Long Until", ugfx.WHITE)
ugfx.text(80, ugfx.height()-60, "EMF 2020", ugfx.WHITE)
ugfx.text(5, ugfx.height() - 20, "By Alex(@AEastabrook)", ugfx.WHITE)
speaker.enabled(True)

NOTE_C4  = 262
NOTE_CS4 = 277
NOTE_D4  = 294
NOTE_DS4 = 311
NOTE_E4  = 330
NOTE_F4  = 349
NOTE_FS4 = 370
NOTE_G4  = 392
NOTE_GS4 = 415
NOTE_A4  = 440
NOTE_AS4 = 466
NOTE_B4  = 494
NOTE_C5  = 523
NOTE_CS5 = 554
NOTE_D5  = 587
NOTE_DS5 = 622
NOTE_E5  = 659
NOTE_F5  = 698
NOTE_FS5 = 740
NOTE_G5  = 784
NOTE_GS5 = 831

def buzz(freq,timetorun):
	speaker.frequency(freq)
	sleep.sleep(0.001*timetorun)
	speaker.stop()

melody = [
    NOTE_D4, NOTE_D4, NOTE_G4, NOTE_A4,NOTE_G4,
    NOTE_FS4,NOTE_E4,NOTE_C4,NOTE_E4,NOTE_A4,
    NOTE_A4,NOTE_B4,NOTE_A4,NOTE_G4,NOTE_FS4,
    NOTE_D4,NOTE_FS4,NOTE_B4,NOTE_E4,NOTE_B4,
    NOTE_A4,NOTE_G4,NOTE_E4,NOTE_D4,NOTE_D4,NOTE_E4,
    NOTE_A4,NOTE_A4,NOTE_FS4,NOTE_G4,
    ]
	
tempo = [
    3,3,5,5,5,5,3,3,3,3,5,5,5,5,3,3,3,3,5,5,5,5,3,3,5,5,3,3,3,2 
    ]

size =  len(melody)

for thisNote in range(0, size):
	noteDuration = 1800 / tempo[thisNote];
	buzz(melody[thisNote], noteDuration)
	pauseBetweenNotes = noteDuration * 1.30;
    
sleep_or_exit(0.1)