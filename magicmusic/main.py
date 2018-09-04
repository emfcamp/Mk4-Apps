"""BEEP BEEP!

Todo: fix this, it doesn't work at at the moment
"""

___name___         = "MAGICMUSIC"
___license___      = "MIT"
___categories___   = ["Sound"]
___dependencies___ = ["speaker", "buttons", "ugfx_helper", "app"]

import ugfx, speaker, ugfx_helper, random, sleep
from tilda import Buttons, Sensors
from buttons import *
from app import restart_to_default

notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

ugfx_helper.init()
octave = 4
delay = 200
def mode_buttons():
    global octave
    global delay
    # render_ui()

    alive = True
    while alive:
        speaker.enabled(True)

        if is_pressed(Buttons.JOY_Up):
            delay += 10
        if is_pressed(Buttons.JOY_Down):
            if delay > 10:
                delay -= 10

        if is_pressed(Buttons.JOY_Left):
            if 1 < octave:
                octave -= 1
        if is_pressed(Buttons.JOY_Right):
            if octave < 6:
                octave += 1

        rand_temp = str(Sensors.get_hdc_temperature()).split('.')[-1]


        rand_num = int(rand_temp) % len(notes)

        rest_delay = int(rand_temp) % 100

        note_to_play = notes[rand_num]
        render_ui(note_to_play, delay, octave, rest_delay)
        # octave = random.randint(1,5)
        speaker.note("{}{}".format(note_to_play, octave))
        sleep.sleep_ms(delay)

        speaker.enabled(False)
        sleep.sleep_ms(rest_delay)





def render_ui(note, delay, octave, rest_delay):
    ugfx.clear()
    ugfx.text(0, 0, "lets make some music! {}".format(note), ugfx.BLACK)
    ugfx.text(0, 100, "Delay: {}ms".format(delay), ugfx.BLACK)
    ugfx.text(0, 200, "Octave: {}".format(octave), ugfx.BLACK)
    ugfx.text(0, 300, "Note Delay: {}".format(rest_delay), ugfx.BLACK)
    
mode_buttons() # Todo: Allow different modes and allow users to switch between them via joystick or something
restart_to_default()


