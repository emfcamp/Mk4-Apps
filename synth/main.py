"""BEEP BEEP!

Todo: fix this, it doesn't work at at the moment
"""

___title___        = "Synthesizers"
___license___      = "MIT"
___categories___   = ["Sound"]
___dependencies___ = ["speaker", "buttons", "ugfx_helper", "app"]

import ugfx, speaker, ugfx_helper
from tilda import Buttons
from buttons import *
from app import restart_to_default

ugfx_helper.init()
speaker.enabled(True)

octave = 4

def mode_buttons():
    global octave
    print("mode: buttons")
    notes = {
        Buttons.BTN_1: "C",
        Buttons.BTN_2: "C#",
        Buttons.BTN_3: "D",
        Buttons.BTN_4: "D#",
        Buttons.BTN_5: "E",
        Buttons.BTN_6: "F",
        Buttons.BTN_7: "F#",
        Buttons.BTN_8: "G",
        Buttons.BTN_9: "G#",
        Buttons.BTN_Star: "A",
        Buttons.BTN_0: "A#",
        Buttons.BTN_Hash: "B"
    }
    render_ui()

    alive = True
    while alive:
        note_to_play = None
        for btn, note in notes.items():
            if is_pressed(btn):
                note_to_play = note
                break
        if note_to_play:
            speaker.note("{}{}".format(note_to_play, octave))
        else:
            speaker.stop()
        if is_triggered(Buttons.BTN_Menu):
            return
        if is_triggered(Buttons.JOY_Up):
            octave = min(6, max(0, octave+1))
            render_ui()
        if is_triggered(Buttons.JOY_Down):
            octave = min(6, max(0, octave-1))
            render_ui()

def render_ui():
    ugfx.clear()
    ugfx.text(5, 5, "Synth", ugfx.BLACK)
    ugfx.text(5, 30, "Use the buttons >", ugfx.BLACK)
    ugfx.text(5, 80, "Octave: {}".format(octave), ugfx.BLUE)

mode_buttons() # Todo: Allow different modes and allow users to switch between them via joystick or something
restart_to_default()
