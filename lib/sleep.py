"""Library for sleep related functions"""

___license___ = "MIT"

import time


def sleep_ms(duration):
    start_time = time.ticks_ms()
    end_time = start_time + duration
    while time.ticks_ms() < end_time:
        wfi()


def sleep(duration):
    sleep_ms(duration * 1000)
    

def wfi():
    # todo: this is fake
    time.sleep_ms(1)
