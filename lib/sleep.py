"""Library for sleep related functions"""

import time

def sleep_ms(duration):
    # todo: deepsleep?
    time.sleep_ms(duration)

def wfi():
    # todo: this is fake
    sleep_ms(1)
