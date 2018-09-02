'''Party thing
'''

___author___ = 'Skybound - ECS'
___name___ = 'Party'
___license___ = 'MIT'
___categories___ = ['LEDs']
___bootstrapped___ = False

from app import restart_to_default
import random
from machine import Neopix
from tilda import Buttons

n = Neopix()

mapping = {
        0: 0x000001,
        1: 0x000100,
        2: 0x010000
        }

exit = False


def breakout(x):
    global exit
    exit = True


Buttons.enable_interrupt(
        Buttons.BTN_Menu,
        breakout,
        on_press=True,
        on_release=False
        )

while True:
    store = [0, 0]
    incs = [random.randint(0, 2) for _ in range(2)]
    for i in range(0xff):
        store[0] += mapping[incs[0]]
        store[1] += mapping[incs[1]]
        n.display(store)
    if exit:
        break

restart_to_default()
