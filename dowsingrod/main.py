"""This is a dowsing rod for WiFi APs"""

___name___         = "Dowsing Rod"
___license___      = "MIT"	
___dependencies___ = ["sleep", "app", "wifi", "sim800"]
___categories___   = ["EMF", "System"]

import ugfx, wifi, app
from tilda import Buttons
from time import sleep

status_height = 20
ssid = 'emfcamp-legacy18'

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_FIXED)

ugfx.Label(5, 180, 240, 15, "Press A to scan, MENU to exit")

# while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
while not Buttons.is_pressed(Buttons.BTN_Menu):
    if not Buttons.is_pressed(Buttons.BTN_A) and not Buttons.is_pressed(Buttons.BTN_B):
        ugfx.poll()
        continue

    if Buttons.is_pressed(Buttons.BTN_B):
      ugfx.clear()
      ugfx.Label(0, 0, 240, 25, "SSID:")
      ssid_box = ugfx.Textbox(0, 25, 240, 25, text=ssid)
      ugfx.Keyboard(0, ugfx.height()//2, ugfx.width(), ugfx.height()//2)
      ssid_box.set_focus()
      while not Buttons.is_pressed(Buttons.BTN_A):
        ugfx.poll()
        continue
      ssid = ssid_box.text()

    ugfx.clear()

    wifi.nic().active(False)
    wifi.nic().active(True)

    # networks = [{ "ssid": ap[0], "mac": ap[1], "channel": ap[2], "signal": ap[3] } for ap in wifi.nic().scan()]
    networks = sorted([net for net in wifi.nic().scan() if net[0] == ssid], key=lambda n: n[3], reverse=True)

    aps = []
    for ap in [(net[1], net[3]) for net in networks]:
        if ap[0] not in [ap[0] for ap in aps]:
            aps.append(ap)

    y = 0
    for ap in aps[:20]:
        ugfx.Label(0, y, 240, 25, "{1}dB {0}".format(*ap))
        y += status_height
    
    if len(aps) == 0:
        ugfx.Label(0, y, 240, 25, "No %s APs found" % ssid)

ugfx.clear()
app.restart_to_default()
