"""App that gets backed into the firmware.

It's only purpose is to download the base operating system on first boot.

It's not meant to be executed from the launcher"""

___license___      = "MIT"
___title___        = "Bootstrap"
___categories___   = ["System"]
___dependencies___ = ["badge_store", "dialogs"]
___launchable___   = False
___builtin___      = True

import ugfx, wifi, badge_store, machine, dialogs

ugfx.init()
machine.Pin(machine.Pin.PWM_LCD_BLIGHT).on()
wifi.connect(show_wait_message=True)
with dialogs.WaitingMessage(title="Setting up TiLDA Mk4", text="Please wait...") as message:
    installers = badge_store.BadgeStore().bootstrap()
    n = len(installers)
    for i, installer in enumerate(installers):
        message.text = "%s (%s/%s)" % (installer.path, i + 1, n)
        installer.download()
machine.reset()

