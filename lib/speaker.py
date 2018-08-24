"""Library for speaker related functions"""

from machine import Pin, PWM
from math import log, pow
from time import sleep_ms

_enabled = True
_amp_pin = Pin(Pin.GPIO_AMP_SHUTDOWN)
_speaker_pwm = None

def enabled(value=None):
    """Sets the internal amplifier. This is entirely independent from the PWM"""
    global _enabled
    if value == None:
        return _enabled
    else:
        _enabled = value
        _set_amp()

def _set_amp():
    if enabled():
        _amp_pin.on()
    else:
        _amp_pin.off()

def speaker_pwm():
    global _speaker_pwm
    if not _speaker_pwm:
        _speaker_pwm = PWM(PWM.PWM_SPEAKER)
    return _speaker_pwm

_frequency = None
def frequency(value = None):
    global _frequency
    if value == None:
        return _frequency
    _frequency = value
    _set_amp()
    speaker_pwm().init(duty=1, freq=_frequency)

def stop():
    global _frequency
    # todo: maybe we should deinit the PWM?
    _frequency = None
    _set_amp()
    speaker_pwm().duty(0)

# Music
NOTES = {"C":0, "C#":1, "D":2, "D#":3, "E":4, "F":5, "F#":6, "G":7, "G#":8, "A":9, "A#":10, "B":11}

def note_to_frequency(note):
    if (len(note) == 2) and note[1].isdigit():
        octave = int(note[1])
        note = note[0].upper()
    elif len(note) == 3:
        octave = int(note[2])
        note = note[0:2].upper()
    else:
        octave = 4
        note = note.upper()

    if note not in NOTES:
        raise Exception("%s it not a valid note" % note)

    halftones = NOTES[note] + 12 * (octave - 4)
    freq = 440 * pow(1.059, halftones)
    return round(freq)

def note(note):
    frequency(note_to_frequency(note))

