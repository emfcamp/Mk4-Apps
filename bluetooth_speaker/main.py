"""App to use the badge as a (handset profile only) bluetooth speaker"""

___name___         = "Bluetooth Speaker"
___license___      = "MIT"
___dependencies___ = ["ugfx_helper", "sim800", "dialogs", "buttons", "app"]
___categories___ = ["Sound"]


import ugfx_helper, ugfx
import app
import sim800
from dialogs import *
import buttons

BLUETOOTH_NAME = "BadgeSpeaker"

g_paired = False


def pairing_dialog(scan_timeout_s=10):
    ''' Show BLE devices to pair with and connect. Returns True if paired, False if failed '''
    waiting_message = WaitingMessage("Scanning for bluetooth devices for %s seconds"%scan_timeout_s, "Scanning")


    devices = sim800.btscan(int(scan_timeout_s * 1000))

    waiting_message.destroy()

    # List format is [id, name, addr, rssi]. FIXME: Only returns 1 item?
    try:
        devices_prompts = [{'title': v[1], 'id': v[0]} for v in devices]
    except TypeError: #Only one device found. #TODO: Not very neat
        devices_prompts = [{'title':devices[1] ,'id':devices[0]},]

    #TODO: Fix non printable chars in device names

    option = prompt_option(devices_prompts, title="Devices Found", select_text="Select", none_text="Rescan")

    if option:
        sim800.btpair(option['id'])
        passcode = sim800.btparingpasscode()
        correct_passcode = prompt_boolean(passcode, title="Started connection from other device?", font=FONT_MEDIUM_BOLD)

        if correct_passcode:
            sim800.btpairconfirm() #TODO: 4 number passcodes?
            return True

        else:
            sim800.btpairreject()
            return False
    else:
        return False


def pairing_callback(param):
    ''' Callback for incoming pairing request '''
    global g_paired
    accept = prompt_boolean("Accept pairing request from %s"%param, title="Incoming pairing")
    if accept:
        sim800.btpairconfirm(0000)
        # Check if we did pair
        if len(sim800.btpaired()) > 1:
            g_paired = True
    else:
        sim800.btpairreject()


def set_simple_pairing():
    ''' Set pairing mode to 4 digit pin, default 0000 '''
    sim800.command("AT+BTPAIRCFG=1,0000", 1000, "OK") # TODO: Error checking?


#Initialise
ugfx_helper.init()
ugfx.init()
ugfx.clear()

ugfx.text(5,5, "Powering Up SIM800", ugfx.BLACK)
sim800.poweron()
ugfx.clear()

ugfx.text(5,5, "Enabling Bluetooth", ugfx.BLACK)
sim800.btpoweron()
sim800.btname(BLUETOOTH_NAME)
sim800.poweroff()
sim800.poweron()
sim800.btpoweron() # Needs a full cycle to have an effect
sim800.btvisible(True)

# Set pairing mode
set_simple_pairing()

ugfx.text(5,20, "Addr: %s " % sim800.btaddress(), ugfx.BLACK)
ugfx.text(5,35, "Name: %s " % sim800.btname(), ugfx.BLACK)
ugfx.clear()

# Register pairings callback
sim800.registercallback("+BTPAIRING:", pairing_callback)

clear_pairing = prompt_boolean("Delete all bluetooth pairings?",title="Clear Pairings?", true_text="Yes", false_text="No")

if clear_pairing:
    sim800.btunpair(0) #0 = clear every pairing

# Start main loop
ugfx.clear()
ugfx.Label(5,5, 220, 200, "Connect to %s \n Passcode = 0000  \n Press menu to exit" % BLUETOOTH_NAME)

connected = True

while(True):

    # Check for pairing button
    if (buttons.is_triggered(buttons.Buttons.BTN_1)):
        pairing_dialog()

    # Check for exit button
    if (buttons.is_triggered(buttons.Buttons.BTN_Menu)):
        sim800.btpoweroff()
        app.restart_to_default()

    num_connections = len(sim800.btconnected())

    if (connected == False) and (num_connections > 0): # Gained connection
        ugfx.area(0,220,240,320, ugfx.BLACK) #Blank bottom of screen
        print(sim800.btconnected())
        sim800.speakervolume(100)
        sim800.btvoicevolume(100)
        ugfx.set_default_font(ugfx.FONT_TITLE)
        ugfx.text(5,230,"CONNECTED!", ugfx.GREEN)
        ugfx.set_default_font(ugfx.FONT_SMALL)
        connected = True

    elif (connected == True) and (num_connections == 0): # Lost connection
        ugfx.area(0,220,240,320, ugfx.BLACK) #Blank bottom of screen
        ugfx.set_default_font(ugfx.FONT_TITLE)
        ugfx.text(5,230,"DISCONNECTED", ugfx.RED)
        ugfx.set_default_font(ugfx.FONT_SMALL)
        connected = False

    sleep.wfi()