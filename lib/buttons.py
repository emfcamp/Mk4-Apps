"""Convenience methods for dealing with the TiLDA buttons

Pins are decined in tilda.Buttons.BTN_XYZ:
BTN_0 - BTN_9, BTN_Hash, BTN_Star
BTN_A, BTN_B
BTN_Call, BTN_End
BTN_Menu
JOY_Center, JOY_Down, JOY_Left, JOY_Right, JOY_Up
"""

___license___ = "MIT"

import machine, time, tilda

# Convenience
Buttons = tilda.Buttons

_tilda_bounce = {}

def is_pressed(button):
    return tilda.Buttons.is_pressed(button)

def is_triggered(button, interval = 30):
    """Use this function if you want buttons as a trigger for something in a loop

    It blocks for a while before returning a True and ignores trailing edge highs
    for a certain time to filter out bounce on both edges
    """
    global _tilda_bounce
    if is_pressed(button):
        if button in _tilda_bounce:
            if time.ticks_ms() > _tilda_bounce[button]:
                del _tilda_bounce[button]
            else:
                return False # The button might have bounced back to high

        # Wait for a while to avoid bounces to low
        time.sleep_ms(interval)

        # Wait until button is released again
        while is_pressed(button):
            time.sleep_ms(1)

        _tilda_bounce[button] = time.ticks_ms() + interval
        return True



# The following functions might not work


def has_interrupt(button):
    return False;

    # todo: re-enable
    #global _tilda_interrupts
    #_get_pin(button)
    #if button in _tilda_interrupts:
    #    return True
    #else:
    #    return False


def enable_interrupt(button, interrupt, on_press = True, on_release = False):
    raise Exception("interrupts don't work yet")
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
        mode = machine.ExtInt.IRQ_RISING_FALLING
    else:
        if pin.pull() == machine.Pin.PULL_DOWN:
            mode = machine.ExtInt.IRQ_RISING if on_press else machine.ExtInt.IRQ_FALLING
        else:
            mode = machine.ExtInt.IRQ_FALLING if on_press else machine.ExtInt.IRQ_RISING

    _tilda_interrupts[button] = {
        "interrupt": machine.ExtInt(pin, mode, pin.pull(), interrupt),
        "mode": mode,
        "pin": pin
    }

def disable_interrupt(button):
    raise Exception("interrupts don't work yet")
    global _tilda_interrupts
    if button in _tilda_interrupts:
        interrupt = _tilda_interrupts[button]
        machine.ExtInt(interrupt["pin"], interrupt["mode"], interrupt["pin"].pull(), None)
        del _tilda_interrupts[button]
        init([button])

def disable_all_interrupt():
    raise Exception("interrupts don't work yet")
    for interrupt in _tilda_interrupts:
        disable_interrupt(interrupt)

