"""Enables mass storage mode in a safe way"""

___name___         = "Mass Storage Enabler"
___license___      = "MIT"
___dependencies___ = ["dialogs", "ugfx_helper"]
___categories___   = ["EMF"]
___bootstrapped___ = True

import ugfx, tilda, ugfx_helper, dialogs, app, time

ugfx_helper.init()
ugfx.clear()

print("enabling USB storage...")
tilda.storage_enable_usb()
time.sleep(1)
print("DONE")
with dialogs.WaitingMessage(title="Mass Storage Enabled", text="You can now use the badge like a USB key.\nPlease safely eject afterwards. This app will close automatically."):
    print("Waiting for USB mass storage to be unmounted...")
    tilda.storage_disable_usb()
    print("DONE")
    app.restart_to_default()
