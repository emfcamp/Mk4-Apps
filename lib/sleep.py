"""Library for sleep related functions"""

___license___ = "MIT"

import time

def sleep_ms(duration):
    # todo: deepsleep?
    time.sleep_ms(duration)

def sleep(duration):
    # todo: deepsleep?
    time.sleep(duration)

def wfi():
    # todo: this is fake
    sleep_ms(1)
