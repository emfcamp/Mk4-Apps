"""Library for sleep related functions"""

___license___ = "MIT"

import time

def sleep_ms(duration):
    # todo: deepsleep?
    time.sleep_ms(duration)

def sleep(duration):
    start_time = time.ticks_ms()
    end_time = start_time + duration * 1000
    while time.ticks_ms() < end_time:
        wfi()

def wfi():
    # todo: this is fake
    sleep_ms(1)
