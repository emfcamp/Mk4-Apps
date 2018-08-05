"""Convenience methods for dealing with the TiLDA buttons"""

___license___ = "MIT"

import pyb

CONFIG = {
    "JOY_UP": pyb.Pin.PULL_DOWN,
    "JOY_DOWN": pyb.Pin.PULL_DOWN,
    "JOY_RIGHT": pyb.Pin.PULL_DOWN,
    "JOY_LEFT": pyb.Pin.PULL_DOWN,
    "JOY_CENTER": pyb.Pin.PULL_DOWN,
    "BTN_MENU": pyb.Pin.PULL_UP,
    "BTN_A": pyb.Pin.PULL_UP,
    "BTN_B": pyb.Pin.PULL_UP
}

ROTATION_MAP = {
    "JOY_UP": "JOY_LEFT",
    "JOY_LEFT": "JOY_DOWN",
    "JOY_DOWN": "JOY_RIGHT",
    "JOY_RIGHT": "JOY_UP",
}

_tilda_pins = {}
_tilda_interrupts = {}
_tilda_bounce = {}

def _get_pin(button):
    if button not in _tilda_pins:
        raise ValueError("Please call button.init() first before using any other button functions")
    return _tilda_pins[button]

def init(buttons = CONFIG.keys()):
    """Inits all pins used by the TiLDA badge"""
    global _tilda_pins
    for button in buttons:
        _tilda_pins[button] = pyb.Pin(button, pyb.Pin.IN)
        _tilda_pins[button].init(pyb.Pin.IN, CONFIG[button])

def rotate(button):
    """remaps names of buttons to rotated values"""
    return ROTATION_MAP[button]

def is_pressed(button):
    pin = _get_pin(button)
    if pin.pull() == pyb.Pin.PULL_DOWN:
        return pin.value() > 0
    else:
        return pin.value() == 0

def is_triggered(button, interval = 30):
    """Use this function if you want buttons as a trigger for something in a loop

    It blocks for a while before returning a True and ignores trailing edge highs
    for a certain time to filter out bounce on both edges
    """
    global _tilda_bounce
    if is_pressed(button):
        if button in _tilda_bounce:
            if pyb.millis() > _tilda_bounce[button]:
                del _tilda_bounce[button]
            else:
                return False # The button might have bounced back to high

        # Wait for a while to avoid bounces to low
        pyb.delay(interval)

        # Wait until button is released again
        while is_pressed(button):
            pyb.wfi()

        _tilda_bounce[button] = pyb.millis() + interval
        return True

def has_interrupt(button):
    global _tilda_interrupts
    _get_pin(button)
    if button in _tilda_interrupts:
        return True
    else:
        return False


def enable_interrupt(button, interrupt, on_press = True, on_release = False):
    """Attaches an interrupt to a button

    on_press defines whether it should be called when the button is pressed
    on_release defines whether it should be called when the button is releaseed

    The callback function must accept exactly 1 argument, which is the line that
    triggered the interrupt.
    """
    global _tilda_interrupts
    pin = _get_pin(button)
    if button in _tilda_interrupts:
        # If someone tries to set an interrupt on a pin that already
        # has one that's totally ok, but we need to remove the old one
        # first
        disable_interrupt(button)

    if not (on_press or on_release):
        return

    mode = None;
    if on_press and on_release:
        mode = pyb.ExtInt.IRQ_RISING_FALLING
    else:
        if pin.pull() == pyb.Pin.PULL_DOWN:
            mode = pyb.ExtInt.IRQ_RISING if on_press else pyb.ExtInt.IRQ_FALLING
        else:
            mode = pyb.ExtInt.IRQ_FALLING if on_press else pyb.ExtInt.IRQ_RISING

    _tilda_interrupts[button] = {
        "interrupt": pyb.ExtInt(pin, mode, pin.pull(), interrupt),
        "mode": mode,
        "pin": pin
    }

def disable_interrupt(button):
    global _tilda_interrupts
    if button in _tilda_interrupts:
        interrupt = _tilda_interrupts[button]
        pyb.ExtInt(interrupt["pin"], interrupt["mode"], interrupt["pin"].pull(), None)
        del _tilda_interrupts[button]
        init([button])

def disable_all_interrupt():
    for interrupt in _tilda_interrupts:
        disable_interrupt(interrupt)

def enable_menu_reset():
    import onboard
    enable_interrupt("BTN_MENU", lambda t:onboard.semihard_reset(), on_release = True)

def disable_menu_reset():
    disable_interrupt("BTN_MENU")

