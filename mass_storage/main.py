"""Enables mass storage mode in a safe way"""

___title___        = "Mass Storage Enabler"
___license___      = "MIT"
___dependencies___ = ["dialogs", "ugfx_helper"]
___categories___   = ["EMF"]
___bootstrapped___ = True

import ugfx, tilda, ugfx_helper, dialogs, app, time

ugfx_helper.init()
ugfx.clear()

user_agreed = dialogs.prompt_boolean("Note: enabling mass storage is slightly risky, as the badge may end up factory "
                                     "resetting even if you safely eject it. Do you want to continue?")

if user_agreed:
    print("enabling USB storage...")
    tilda.storage_enable_usb()
    time.sleep(1)
    print("DONE")
    with dialogs.WaitingMessage(title="Mass Storage Enabled", text="You can now use the badge like a USB key.\nPlease safely eject afterwards. This app will close automatically."):
        print("Waiting for USB mass storage to be unmounted...")
        tilda.storage_disable_usb()
        print("DONE")
        app.restart_to_default()
else:
    app.restart_to_default()
