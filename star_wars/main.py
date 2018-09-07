
"""
Will play music, maybe
"""

___title___        = "Star Wars Music"
___license___      = "MIT"
___categories___   = ["Sound"]
___dependencies___ = ["speaker", "shared/sw.png", "buttons"]

import random, ugfx, speaker, buttons, ugfx_helper
import time
import utime
from machine import Neopix
from tilda import LED
from homescreen import init, sleep_or_exit
from tilda import Buttons, Sensors

ledColours = [
    0xFF0000,
    0xFFFF00,
    0x00FF00,
    0x008000,
    0x00FFFF,
    0x0000FF,
    0xFF00FF,
    0xFA8072,
]
ledColourCount  = len(ledColours)

logo_path = "shared/sw.png"
logo_height = 121
logo_width = 240

mute = False

# Setup
init()
neopix = Neopix()
ugfx_helper.init()
speaker.enabled(True)

####################
####################
####################

notes = [
  {
    "name": "G3",
    "midi": 55,
    "time": 1.5,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 1.6666666666666665,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 1.833333333333333,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 9.5,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 9.833333333333334,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 17.5,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 17.833333333333336,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 18,
    "velocity": 0.6299212598425197,
    "duration": 0.7114583333333329
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 18.75,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 20.833333333333336,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "B3",
    "midi": 59,
    "time": 21,
    "velocity": 0.6299212598425197,
    "duration": 0.47395833333333215
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 21.5,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 21.833333333333336,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 22,
    "velocity": 0.6299212598425197,
    "duration": 0.7114583333333329
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 22.75,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 25.833333333333336,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 26,
    "velocity": 0.6299212598425197,
    "duration": 0.7114583333333329
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 26.75,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 28.833333333333336,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "B3",
    "midi": 59,
    "time": 29,
    "velocity": 0.6299212598425197,
    "duration": 0.47395833333333215
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 29.5,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 29.833333333333336,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 32.5,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 32.666666666666664,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 32.83333333333333,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 32.99999999999999,
    "velocity": 0.6299212598425197,
    "duration": 0.4739583333333357
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 33.49999999999999,
    "velocity": 0.6299212598425197,
    "duration": 0.23645833333333144
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 33.74999999999999,
    "velocity": 0.6299212598425197,
    "duration": 0.11770833333333286
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 33.87499999999999,
    "velocity": 0.6299212598425197,
    "duration": 0.11770833333333286
  },
  {
    "name": "A3",
    "midi": 57,
    "time": 33.99999999999999,
    "velocity": 0.6299212598425197,
    "duration": 0.7114583333333329
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 34.74999999999999,
    "velocity": 0.6299212598425197,
    "duration": 0.23645833333333144
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 37.49999999999999,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 37.66666666666666,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 37.83333333333332,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 45.499999999999986,
    "velocity": 0.6299212598425197,
    "duration": 0.31562499999999716
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 45.833333333333314,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 53.49999999999998,
    "velocity": 0.6299212598425197,
    "duration": 0.31562499999999716
  },
  {
    "name": "G3",
    "midi": 55,
    "time": 53.83333333333331,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 2,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 3.0000000000000004,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333331
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 4,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 4.166666666666667,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 4.333333333333334,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "C5",
    "midi": 72,
    "time": 4.500000000000001,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 5.500000000000001,
    "velocity": 0.6299212598425197,
    "duration": 0.47395833333333304
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 6.000000000000001,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 6.166666666666668,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 6.333333333333335,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666666
  },
  {
    "name": "C5",
    "midi": 72,
    "time": 6.500000000000002,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 7.500000000000002,
    "velocity": 0.6299212598425197,
    "duration": 0.47395833333333304
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 8.000000000000002,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 8.16666666666667,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 8.333333333333337,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 8.500000000000005,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 10.000000000000005,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 11.000000000000005,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 12.000000000000005,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 12.166666666666673,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 12.333333333333341,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "C5",
    "midi": 72,
    "time": 12.500000000000009,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 13.500000000000009,
    "velocity": 0.6299212598425197,
    "duration": 0.4739583333333339
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 14.000000000000009,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 14.166666666666677,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 14.333333333333345,
    "velocity": 0.6299212598425197,
    "duration": 0.1572916666666675
  },
  {
    "name": "C5",
    "midi": 72,
    "time": 14.500000000000012,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 15.500000000000012,
    "velocity": 0.6299212598425197,
    "duration": 0.4739583333333339
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 16.000000000000014,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 16.16666666666668,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 16.333333333333343,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 16.500000000000007,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 19.000000000000007,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 19.250000000000007,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 19.500000000000007,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 19.750000000000007,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 20.000000000000007,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 20.16666666666667,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 20.333333333333336,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 20.5,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 23,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 23.25,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 23.5,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 23.75,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 24,
    "velocity": 0.6299212598425197,
    "duration": 0.47395833333333215
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 24.5,
    "velocity": 0.6299212598425197,
    "duration": 0.9489583333333336
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 27,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 27.25,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 27.5,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 27.75,
    "velocity": 0.6299212598425197,
    "duration": 0.236458333333335
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 28,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 28.166666666666664,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "E4",
    "midi": 64,
    "time": 28.33333333333333,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 28.499999999999993,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "C5",
    "midi": 72,
    "time": 29.999999999999993,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "A#4",
    "midi": 70,
    "time": 30.33333333333333,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G#4",
    "midi": 68,
    "time": 30.499999999999993,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 30.83333333333333,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 30.999999999999993,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "D#4",
    "midi": 63,
    "time": 31.33333333333333,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 31.499999999999993,
    "velocity": 0.6299212598425197,
    "duration": 0.3156250000000007
  },
  {
    "name": "C4",
    "midi": 60,
    "time": 31.83333333333333,
    "velocity": 0.6299212598425197,
    "duration": 0.15729166666666572
  },
  {
    "name": "G4",
    "midi": 67,
    "time": 31.999999999999993,
    "velocity": 0.6299212598425197,
    "duration": 0.4739583333333357
  },
  {
    "name": "F4",
    "midi": 65,
    "time": 34.99999999999999,
    "velocity": 0.6299212598425197,
    "duration": 0.4739583333333357
  },
  {
    "name": "D4",
    "midi": 62,
    "time": 35.49999999999999,
    "velocity": 0.6299212598425197,
    "duration": 1.8989583333333329
  },
]

noteCount = len(notes)
notes.sort(key=lambda x: x['time'])

####################
####################
####################

def _random():
    return (utime.ticks_ms() % 100) / 100

def _randrange(start, stop=None):
    """Return a randomly selected element from range(start, stop)"""
    if stop is None:
        stop = start
        start = 0
    random = _random()
    randomRange = round(start + (random * (stop - start)))
    return randomRange

def playMusic(stopTime = 99999):
    global noteCount, notes

    index = 0
    startTime = utime.ticks_ms()
    while True:
        # Stop playing
        if index >= noteCount or buttons.is_pressed(Buttons.BTN_A):
            speaker.stop()
            break

        # How long have we been playing for
        currentTime = utime.ticks_ms()
        timeDiff = currentTime - startTime

        # End early if told
        if timeDiff > stopTime:
            speaker.stop()
            break

        # Play note
        note = notes[index]
        if timeDiff > (note['time'] * 1000):
            if 'midi' in note:
                freq = 27.5 * pow(2, (note['midi'] - 21) / 12)
                speaker.frequency(round(freq))
            else:
                speaker.stop()

            index += 1
        
        sleep_or_exit(0.1)

def doLights():
    # LED Flash
    if _randrange(1, 10) <= 5:
        LED(LED.RED).on()
    else:
        LED(LED.RED).off()

    if _randrange(1, 10) <= 5:
        LED(LED.GREEN).on()
    else:
        LED(LED.GREEN).off()

    # NEO Pixels
    colorNum1 = _randrange(0, ledColourCount - 1)
    colorNum2 = _randrange(0, ledColourCount - 1) 
    neopix.display([ledColours[colorNum1], ledColours[colorNum2]])

maxHeight = ugfx.height()
yPos = maxHeight
logo = ugfx.Image(logo_path, True)
def doScroll():
    global yPos, maxHeight, logo

    # Blank previous logo location
    ugfx.area(0, yPos, ugfx.width(), yPos + logo_height, 0)

    # Move up and wrap
    yPos -= 20
    if (yPos <= -logo_height):
        yPos = maxHeight

    # Draw logo
    ugfx.display_image(
        int((ugfx.width() - logo_width) / 2),
        int(yPos),
        logo
    )

def blankScreen():
  ugfx.clear(ugfx.BLACK)

def drawLogo():
  # Return to default
  ugfx.display_image(
      int((ugfx.width() - logo_width) / 2),
      int((ugfx.height() - logo_height) / 2),
      logo
  )

def drawTutorial():
  ugfx.orientation(270)

  # Draw for user
  blankScreen() 
  ugfx.text(5, 5, "Buttons: A = music, B = lights", ugfx.WHITE)
  ugfx.text(5, 25, "JoyStick Click = scrolling", ugfx.WHITE)

  ugfx.text(5, ugfx.height() - 20, "By Pez (@Pezmc)", ugfx.WHITE)

def boot():
  drawTutorial()

  ugfx.orientation(90) # Draw for others
  drawLogo()
  playMusic(9500)
  blankScreen()

#############
#############
#############
boot()

enableLights = False
enableScroll = True
while True:
    # Toggle lights
    if buttons.is_triggered(Buttons.BTN_B):
        enableLights = not enableLights
        neopix.display([0, 0]) # Lights off

    # Play music
    elif buttons.is_triggered(Buttons.BTN_A):
        neopix.display([0, 0]) # Lights off
        drawTutorial()
        drawLogo()
        playMusic()

    # Toggle scroll
    elif buttons.is_triggered(Buttons.JOY_Center):
        enableScroll = not enableScroll
        if not enableScroll:
            blankScreen()
            drawLogo()

    else:
        if enableLights:
            doLights()

        if enableScroll:
            doScroll()

    sleep_or_exit(0.1)