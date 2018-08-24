"""BEEP BEEP!

Todo: fix this, it doesn't work at at the moment
"""

___name___         = "Synthesizers"
___license___      = "MIT"
___categories___   = ["Sound"]
___dependencies___ = ["speaker", "buttons", "ugfx_helper"]

import ugfx, speaker, ugfx_helper
from app import *
from tilda import Buttons
from buttons import *

ugfx_helper.init()
speaker.enabled(True)

def mode_buttons():
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
    ugfx.clear()
    ugfx.text(5, 5, "Synth", ugfx.BLACK)
    ugfx.text(5, 30, "Use the buttons >", ugfx.BLACK)
    ugfx.text(5, 80, "Octave: 4", ugfx.BLUE) # Make this adjustable

    alive = True
    while alive:
        note_to_play = None
        for btn, note in notes.items():
            if is_pressed(btn):
                note_to_play = note
                break
        if note_to_play:
            speaker.note(note_to_play)
        else:
            speaker.stop()

mode_buttons()
