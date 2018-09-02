"""Phone app for baic calling functions
"""
___name___         = "Phone"
___license___      = "MIT"
___dependencies___ = ["app", "dialogs", "sim800", "ugfx_helper"]
___categories___   = ["System"]
___bootstrapped___ = True

from app import *
from dialogs import *
import ugfx
import ugfx_helper
import sim800

sim800.poweron()

ugfx_helper.init()
ugfx.clear()


def makecall():
    notocall = prompt_text("Number to call:", numeric=True)
    if (notocall):
        sim800.call(notocall)

def answercall():
    if sim800.isringing():
        sim800.answer()
    else:
        notice("No call to answer.", title="TiLDA Phone")

def hangupcall():
    sim800.hangup()

def playdtmf():
    if sim800.getstatus()==4:
        notice("Use the keypad to play a DTMF tones on a call. Pres A or B to retun to the menu.", title="TiLDA Phone")
        while True:
            if buttons.is_pressed(buttons.Buttons.BTN_0):
                sim800.dtmf("0")
            if buttons.is_pressed(buttons.Buttons.BTN_1):
                sim800.dtmf("1")
            if buttons.is_pressed(buttons.Buttons.BTN_2):
                sim800.dtmf("2")
            if buttons.is_pressed(buttons.Buttons.BTN_3):
                sim800.dtmf("3")
            if buttons.is_pressed(buttons.Buttons.BTN_4):
                sim800.dtmf("4")
            if buttons.is_pressed(buttons.Buttons.BTN_5):
                sim800.dtmf("5")
            if buttons.is_pressed(buttons.Buttons.BTN_6):
                sim800.dtmf("6")
            if buttons.is_pressed(buttons.Buttons.BTN_7):
                sim800.dtmf("7")
            if buttons.is_pressed(buttons.Buttons.BTN_8):
                sim800.dtmf("8")
            if buttons.is_pressed(buttons.Buttons.BTN_9):
                sim800.dtmf("9")
            if buttons.is_pressed(buttons.Buttons.BTN_Star):
                sim800.dtmf("*")
            if buttons.is_pressed(buttons.Buttons.BTN_Hash):
                sim800.dtmf("#")
            if buttons.is_pressed(buttons.Buttons.BTN_A):
                return
            if buttons.is_pressed(buttons.Buttons.BTN_B):
                return
    else:
        notice("You are not on a call.", title="TiLDA Phone")

def speakervolume():
    sim800.hangup()

def ringervol():
    opset = []
    opset.append({ "title" : "Silent", "index" : "0" })
    opset.append({ "title" : "Quiet", "index" : "25" })
    opset.append({ "title" : "Medium", "index" : "50" })
    opset.append({ "title" : "Loud", "index" : "75" })
    opset.append({ "title" : "Very Loud", "index" : "100" })
    selectedop = prompt_option(opset, text="Ringer Volume", select_text="Select", none_text="Cancel")
    if selectedop:
        sim800.ringervolume(selectedop["index"])
    
def speakervol():
    opset = []
    opset.append({ "title" : "Silent", "index" : "0" })
    opset.append({ "title" : "Quiet", "index" : "25" })
    opset.append({ "title" : "Medium", "index" : "50" })
    opset.append({ "title" : "Loud", "index" : "75" })
    opset.append({ "title" : "Very Loud", "index" : "100" })
    selectedop = prompt_option(opset, text="Speaker Volume", select_text="Select", none_text="Cancel")
    if selectedop:
        sim800.speakervolume(selectedop["index"])
    
def showinfo():
    info = ""
    yournum = sim800.getmynumber()
    if (yournum):
        info += yournum + "\n"
    yourop = sim800.currentoperator(0)
    if (yourop):
        info += "Operator : " + yourop + "\n"
    imei = sim800.imei()
    if (imei):
        info += "IMEI : " + imei + "\n"
    imsi = sim800.imsi()
    if (imsi):
        info += "IMSI : " + imsi + "\n"
    rssi = sim800.rssi()
    if (rssi):
        info += "RSSI : " + str(rssi) + "\n"
    ber = sim800.ber()
    if (ber):
        info += "BER : " + str(ber) + "\n"
    cellid = sim800.cellid()
    if (cellid):
        info += "Cell ID : " + cellid + "\n"
    yourbat = sim800.batterycharge()
    if (yourbat>0):
        info += "Battery : " + str(yourbat) + "%\r\n"
    notice(info, title="TiLDA Phone")


def selectoperator():
    opset = []
    opset.append({ "title" : "EMF", "index" : "23404" })
    opset.append({ "title" : "Auto", "index" : -1 })
    for op in sim800.listoperators():
        opset.append({ "title" : op[1], "index" : op[3] })
    selectedop = prompt_option(opset, text="Operator", select_text="Select", none_text="Cancel")
    if selectedop:
        if selectedop["index"]==-1:
            sim800.setoperator(0)
            notice("Operator selection set to automatic.", title="TiLDA Phone")
        else:
            sim800.setoperator(1,2,selectedop["index"])
            notice(selectedop["title"] + " set as operator.", title="TiLDA Phone")

menuset = []
menuset.append({ "title" : "Call", "index" : 1 })
menuset.append({ "title" : "Answer", "index" : 2 })
menuset.append({ "title" : "Hangup/Reject", "index" : 3 })
menuset.append({ "title" : "DTMF Tones", "index" : 4 })
menuset.append({ "title" : "Speaker Volume", "index" : 6 })
menuset.append({ "title" : "Ringer Volume", "index" : 7 })
menuset.append({ "title" : "Information", "index" : 8 })
menuset.append({ "title" : "Select Operator", "index" : 9 })

while True:
    selection = prompt_option(menuset, text="TiLDA Phone", select_text="Select", none_text="Exit")
    if (not selection):
        restart_to_default()
    elif (selection["index"]==1):
        makecall()
    elif (selection["index"]==2):
        answercall()
    elif (selection["index"]==3):
        hangupcall()
    elif (selection["index"]==4):
        playdtmf()
    elif (selection["index"]==6):
        speakervol()
    elif (selection["index"]==7):
        ringervol()
    elif (selection["index"]==8):
        showinfo()
    elif (selection["index"]==9):
        selectoperator()
