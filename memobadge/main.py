"""This app tests all the onboard sensors and system info"""

___name___         = "Memobadge"
___license___      = "MIT"
___dependencies___ = ["app", "sim800", "sleep", "ugfx_helper"]
___categories___   = ["Sound"]

import ugfx, app, sim800, time
from tilda import Buttons
from machine import Neopix

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_FIXED)

neopix = Neopix()

def displayControls():
    ugfx.Label(5, 0, 240, 15, "Controls:")
    ugfx.Label(5, 15, 240, 15, "  A: Start / Stop recording")
    ugfx.Label(5, 30, 240, 15, "  B: playback")
    ugfx.Label(5, 45, 240, 15, "  Menu: exit")

def displayStatus(status):
    ugfx.Label(5, 90, 240, 15, status)

def setRecordingStatus():
    global neopix, isRecording

    if isRecording:
        neopix.display([0x000000, 0x050000])
    else:
        neopix.display([0x000000, 0x000000])


def startRecording():
    global isRecording

    if isRecording:
        isRecording = False
        sim800.stoprecording()
        displayStatus("")
    else:
        # Just in case something is being played
        sim800.stopplayback()
        isRecording = True
        sim800.deleterecording(1)
        displayStatus("Recording, press A again to stop.")
        sim800.startrecording(1)

    setRecordingStatus()

def playback():
    global isRecording

    if isRecording:
        isRecording = False
        sim800.stoprecording()
        setRecordingStatus()
        displayStatus("")

    sim800.startplayback(1, 0, 100, False)

Buttons.enable_interrupt(
    Buttons.BTN_A,
    lambda button_id: startRecording(),
    on_press=True,
    on_release=False
)

Buttons.enable_interrupt(
    Buttons.BTN_B,
    lambda button_id: playback(),
    on_press=True,
    on_release=False
)

Buttons.enable_interrupt(
    Buttons.BTN_Menu,
    lambda button_id:app.restart_to_default(),
    on_press=True,
    on_release=False
)

isRecording = False
displayControls()
setRecordingStatus()

while True:
    # Wait for instruction
    time.sleep(0.1)

ugfx.clear()
app.restart_to_default()
