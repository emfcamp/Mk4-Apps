"""SIM800 library for the TiLDA MK4"""

___license___ = "MIT"
___dependencies___ = []

import machine
import time
import micropython
import tilda

uart_port = 1
uart_default_baud = 115200
uart_timeout = 28
default_response_timeout = 2000

status_pin = machine.Pin(machine.Pin.GPIO_SIM_STATUS, machine.Pin.IN)
ringer_pin = machine.Pin(machine.Pin.GPIO_SIM_RI, machine.Pin.IN)
pwr_key_pin = machine.Pin(machine.Pin.GPIO_SIM_PWR_KEY, machine.Pin.OUT)
amp_pin = machine.Pin(machine.Pin.GPIO_AMP_SHUTDOWN, machine.Pin.OUT)
netlight_pin = machine.Pin(machine.Pin.GPIO_SIM_NETLIGHT, machine.Pin.IN)

# Open the UART
uart = machine.UART(uart_port, uart_default_baud, mode=machine.UART.BINARY, timeout=uart_timeout)
dirtybuffer = False # Flag if the buffer could have residual end of reresponsesponces line in it?

# A list of callback functions
callbacks = []

# Globals for remembering callback data
clip = ""
btpairing = ''
holdoffirq=False

# Check if the SIM800 is powered up
def ison():
    return status_pin.value()==1

# Check if the SIM800 is ringing
def isringing():
    return ringer_pin.value()==0

# Register for a callback
def registercallback(call, function):
    callbacks.append([call, function])

# Deregitser for a callback
def deregistercallback(function):
    for entry in callbacks:
        if entry[1]==function:
            callbacks.remove(entry)

# Identify if this was a positive response
def ispositive(response):
    return (response=="OK") or response.startswith("CONNECT") or response.startswith("SEND OK")

# Identify if this was a negative response
def isnegative(response):
    return (response=="NO CARRIER") or (response=="ERROR") or (response=="NO DIALTONE") or (response=="BUSY") or (response=="NO ANSWER") or (response=="SEND FAIL") or (response=="TIMEOUT") or (response=="TimeOut")

# Identify if this is the completion of a response
def isdefinitive(response, custom=None):
    if custom is not None:
        return ispositive(response) or isnegative(response) or response.startswith(custom)
    else:
        return ispositive(response) or isnegative(response)

# Extract the [first/only] parameter from a response 
def extractval(parameter, response, default=""):
    for entry in response:
        if entry.startswith(parameter):
            return (entry[len(parameter):]).strip()
    return default

# Extract all parameter from a response 
def extractvals(parameter, response):
    result = []
    for entry in response:
        if entry.startswith(parameter):
            result.append((entry[len(parameter):]).strip())
    return result

# Read a lines of response from the UART
def readline():
    stringin = ""
    while (True):
        charin = uart.read(1)
        # If we time out we are at the end of a line
        if charin is None:
            return stringin
        # We this the end of the line?
        elif (charin == b'\r'):
            if (stringin!=""):
                return stringin
        # This will be part of the string then
        elif not (charin == b'\n'):
            stringin += chr(ord(charin))
            
# Check if we have a callback hook for this line
def processcallbacks(line):
    global clip
    global btpairing
    # Check for the caller line information
    if line.startswith("+CLIP:"):
        clip = line[6:].strip()
    # Check for Bluetooth pairing request
    if line.startswith("+BTPAIRING:"):
        btpairing = line[11:].strip()
    # Check for app callbacks
    for entry in callbacks:
        if line.startswith(entry[0]):
            micropython.schedule(entry[1], line[len(entry[0]):].strip())
                
# Process the buffer for  unsolicited result codes 
def processbuffer():
    while uart.any()>0:
        line = readline()
        processcallbacks(line)
        
# Execute a command on the module
# The same interface as and called by command() but without power so can be called from power()
def command_internal(command="AT", response_timeout=default_response_timeout, required_response=None, custom_endofdata=None):
    global dirtybuffer
    global holdoffirq
    # Don't let the interupt process the buffer mid command
    holdoffirq = True
    # Process anything remaining in the buffer
    processbuffer()
    # Send the command
    uart.write(command + "\r")
    # Read the results
    result = []
    complete = False
    customcomplete = required_response is None
    timeouttime = time.time()+(response_timeout/1000)
    while (time.time()<timeouttime):
        line = readline()
        processcallbacks(line)
        # Remember the line if not empty
        if (len(line)>0):
            result.append(line)
        # Check if we have a standard end of response
        if isdefinitive(line, custom_endofdata):
            complete = True
        # Check if we have the data we are looking for
        if (required_response is not None) and (line.startswith(required_response)):
            customcomplete = True
        # Check if we are done
        if complete and customcomplete:
            holdoffirq = False
            return result
    # We ran out of time
    # set the dirty buffer flag is an out of date end of responcs cound end up in the buffer
    if required_response is None:
        dirtybuffer = True
    result.append("TIMEOUT")
    holdoffirq = False
    return result

# Send the command to set the default configuration to the SIM800
def senddefaultconfig():
    # Send a command to autonigotiate UART speed
    command_internal("AT")
    # Turn on new SMS notificationn
    command_internal("AT+CNMI=1,2")
    # Turn on calling line identification notification
    command_internal("AT+CLIP=1")
    # Swith to text mode
    command("AT+CMGF=1")
    # Switch to ASCII(ish)
    command("AT+CSCS=\"8859-1\"")
    # Enable DTMF detection
    command("AT+DDET=1,0,1")
    # Set up multichannel Bluetooth without transparent transmition
    command("AT+BTSPPCFG=\"MC\",1")
    command("AT+BTSPPCFG=\"TT\",0")
    
# Power on the SIM800 (True=on, False=off, returns true when on)
def power(onoroff, asyncro):
    # Get to a stable state if not async
    if not asyncro and pwr_key_pin.value():
        pwr_key_pin.off()
        time.sleep(3)
    # Press the virtual power key if we are off
    if not (ison()==onoroff):
        pwr_key_pin.on()
        if not asyncro:
            time.sleep(3)
    # Have we just turned on?
    isonnow = ison()
    if (isonnow==onoroff) and pwr_key_pin.value():
        # Stop pressing the virtual key
        pwr_key_pin.off()
        # Clear the buffer
        processbuffer()
        dirtybuffer = False
        # We are now live
        if isonnow:
            # Set the deault configuration
            senddefaultconfig()
    return isonnow

# Power on the SIM800 (returns true when on)
def poweron(asyncro=False):
    return power(True, asyncro)

# Power off the SIM800 (returns true when off)
def poweroff(asyncro=False):
    return not power(False, asyncro)

# Change the speed on the communication
def uartspeed(newbaud):
    global uart
    command("AT+IPR=" + str(newbaud))
    uart.deinit()
    if (newbaud==0):
        uart = machine.UART(uart_port, uart_default_baud, mode=UART.BINARY, timeout=uart_timeout)
    else:
        uart = machine.UART(uart_port, newbaud, mode=UART.BINARY, timeout=uart_timeout)

# Netlight sheduled (called for polling uart)
def netlightscheduled_internal(pinstate):
    # Complete the setup procedure if needed
    if pwr_key_pin.value() and ison():
        poweron()
    # Check for incomming commands
    if holdoffirq==False:
        processbuffer()

# Netlight IRQ (called for polling uart)
def netlightirq_internal(pinstate):
    micropython.schedule(netlightscheduled_internal, pinstate)

# Command is the AT command without the AT or CR/LF, response_timeout (in ms) is how long to wait for completion, required_response is to wait for a non standard response, custom_endofdata will finish when found
def command(command="AT", response_timeout=default_response_timeout, required_response=None, custom_endofdata=None):
    # Check we are powered on and set up
    poweron(False)
    # Call the internal command() function
    return command_internal(command, response_timeout, required_response, custom_endofdata)

# Make a voice call
def call(number):
    command("ATD" + str(number) + ";", 20000)

# Answer a voice call
def answer():
    command("ATA", 20000)

# End/reject a voice call
def hangup():
    command("ATH")

# Redial the last number
def redial():
    command("ATDL")

# Get the current/latest number to call
def latestnumber():
    if ison():
        processbuffer()
    return clip.split(",")[0].strip("\"")

# Play DTMF tone(s) on a call
def dtmf(number):
    validdigits = '1234567890#*ABCD'
    for digit in str(number).upper():
        if (digit in validdigits):
            command("AT+VTS=" + digit)
        elif (digit==','):
            time.sleep(1)

# Send an SMS message
def sendsms(number, message):
    # Swith to text mode
    command("AT+CMGF=1")
    # Switch to ASCII(ish)
    command("AT+CSCS=\"8859-1\"")
    # Send the message
    command("AT+CMGS=\"" + str(number) + "\"", 2000, None, "> ")
    return command(message + "\x1a", 60000)

# List the summery of SMS messages (0=unread,1=read,2=saved unread,3=saved sent, 4=all)
def listsms(stat=0):
    statvals = ["REC UNREAD", "REC READ", "STO UNSENT", "STO SENT", "ALL"]
    # Swith to text mode
    command("AT+CMGF=1")
    # Retrieve the list
    return extractvals("+CMGL:", command("AT+CMGL=\"" + statvals[stat] + "\",1", 8000))
    
# Check if we have recived a new unread SMS message
def newsms():
    return len(listsms(stat=0))>0

# Read an SMS message
def readsms(index, leaveunread=False):
    # Swith to text mode
    command("AT+CMGF=1")
    # Switch to ASCII(ish)
    command("AT+CSCS=\"8859-1\"")
    # Retrieve the message
    response = command("AT+CMGR=" + str(index) + "," + str(int(leaveunread)), 5000)
    if (len(response)>=3):
        return response[-2]
    else:
        return ""

# Delete an SMS message
def deletesms(index):
    command("AT+CMGD=" + str(index), 5000)

# Get the IMEI number of the SIM800
def imei():
    response = command("AT+GSN")
    if (len(response)>=2):
        return response[-2]
    else:
        return ""

# Get the IMSI number of the Sim Card
def imsi():
    response = command("AT+CIMI")
    if (len(response)>=2):
        return response[-2]
    else:
        return ""

# Get the ICCID of the Sim Card
def iccid():
    response = command("AT+ICCID")
    return extractval("+ICCID:", response)

# Get the received signal strength indication
def rssi():
    response = command("AT+CSQ")
    return int(extractval("+CSQ:", response, "0,0").split(",")[0])
    
# Get the bit error rate    
def ber():
    response = command("AT+CSQ")
    return int(extractval("+CSQ:", response, "0,0").split(",")[1])

# Get the cell engineering information (True to include neighboring cell id)
def engineeringinfo(neighbor=False):
    command("AT+CENG=1," + str(int(neighbor)))
    response = command("AT+CENG?")
    command("AT+CENG=0")
    responselist = extractvals("+CENG:", response)[1:]
    results = []
    for entry in responselist:
        results.append([entry[0], entry.replace("\"", "").split(",")[1:]])
    return results

# Get the cell id of the currently connected cell
def cellid():
    return engineeringinfo()[0][1][6]

# Get/Set ringer volume (0-100)
def ringervolume(level=None):
    # Set the new leve if we have one to set
    if level is not None:
        command("AT+CRSL=" + str(level))
    # Retieve the set level to report back
    response = command("AT+CRSL?")
    return int(extractval("+CRSL:", response, 0))

# Get/Set speaker volume (0-100)
def speakervolume(level=None):
    # Set the new leve if we have one to set
    if level is not None:
        command("AT+CLVL=" + str(level))
    # Retieve the set level to report back
    response = command("AT+CLVL?")
    return int(extractval("+CLVL:", response, 0))

# Get/Set/Preview and set the ringtone (alert is 0-19)
def ringtone(alert=None,preview=False):
    # Set/preview the new ringtone if we have one to set
    if alert is not None:
        command("AT+CALS=" + str(alert) + "," + str(int(preview)))
    # Retieve the current/new setting
    response = command("AT+CALS?")
    current = extractval("+CALS:", response, 0).split(",")[0]
    # Stop the preview unless we started it
    if alert is None:
        command("AT+CALS=" + current + ",0")
    # Return the surrent setting
    return int(current)

# Play a tone though the SIM800 (MHz and ms)
def playtone(freq=0,duration=2000,asyncro=True):
    if freq>0:
        command("AT+SIMTONE=1," + str(freq) + "," + str(duration) + ",0," + str(duration))
        if not asyncro:
            time.sleep(duration/1000)
    else:
        command("AT+SIMTONE=0")

# Record audio (id=1-10)
def startrecording(id=1, length=None):
    if length is None:
        return ispositive(command("AT+CREC=1," + str(id) + ",0")[-1])
    else:
        return ispositive(command("AT+CREC=1," + str(id) + ",0," + str(int(length/1000)))[-1])

# Stop recording audio
def stoprecording():
    return ispositive(command("AT+CREC=2")[-1])

# Delete recording
def deleterecording(id=1):
    return ispositive(command("AT+CREC=3," + str(id))[-1])

# Play recording
def startplayback(id=1, channel=0, level=100, repeat=False):
    return ispositive(command("AT+CREC=4," + str(id) + "," + str(channel) + "," + str(level) + "," + str(int(repeat)))[-1])

# Stop playback
def stopplayback():
    return ispositive(command("AT+CREC=5")[-1])

# List recordings (returns a list of ids and size)
def listrecordings():
    response = command("AT+CREC=7")
    responselist = extractvals("+CREC:", response)
    result = []
    for entry in responselist:
        splitentry = entry.split(",")
        result.append([splitentry[1], splitentry[2]])
    return result

# Is the battery charging (0=no, 1=yes, 2=full)
def batterycharging():
    response = command("AT+CBC")
    vals = extractval("+CBC:", response, "0,0,0").split(",")
    return int(vals[0])

# How full is the battery (1-100)
def batterycharge():
    response = command("AT+CBC")
    vals = extractval("+CBC:", response, "0,0,0").split(",")
    return int(vals[1])
    
# List the available operator (returns list of [0=?,1=available,2=current,3=forbidden], 0=long name, 1=short name, 2=GSMLAI )
def listoperators(available_only=True):
    delim = "||||"
    response = command("AT+COPS=?", 45000)
    responsedata = extractval("+COPS:", response, "").split(",,")[0]
    responselist = responsedata.replace("),(",delim)[1:-1].split(delim)
    results = []
    for entry in responselist:
        subresults = []
        for subentry in entry.split(","):
            subresults.append(subentry.strip("\""))
        if (not available_only) or (subresults[0]=="1") or (subresults[0]=="2"):
            results.append(subresults)
    return results

# Get the current operator (format 0=long name, 1=short name, 2=GSMLAI)
def currentoperator(format=0):
    command("AT+COPS=3," + str(format))
    response = command("AT+COPS?")
    responsedata = extractval("+COPS:", response, "").split(",")
    if (len(responsedata)>=3):
        return responsedata[2].strip("\"")
    else:
        return ""

# Set the operator selection ([0=automatic,1=Manual,2=deregister,4=try manual then automatic])
def setoperator(mode, format=None, operator=None):
    params = ""
    if format is not None:
        params += "," + str(format)
        if operator is not None:
            params += ",\"" + str(operator) + "\""
    command("AT+COPS=" + str(mode) + params, 120000)

# Get the activity status (returns 0=ready, 2=unknown, 3=ringing, 4=call in progress)
def getstatus():
    response = command("AT+CPAS")
    return int(extractval("+CPAS:", response, "2"))
    
# Get the firmware revision
def getfirmwarever():
    response = command("AT+CGMR")
    if (len(response)>=3):
        return response[-2]
    else:
        return ""

# Request Unstructured Supplementary Service Data from network
def ussd(ussdstring, timeout=8000):
    response = command("AT+CUSD=1,\"" + ussdstring + "\"", timeout, "+CUSD:")
    return extractval("+CUSD:", response, "")

# Get my number (only works on some networks)
def getmynumber():
    responsedata = ussd("*#100#", 8000).split(",")
    if (len(responsedata)>=2):
        num = responsedata[1].strip().strip("\"")
        return num
    else:
        return ""

# Turn on or off Bluetooth
def btpower(onoroff=True):
    command("AT+BTPOWER=" + str(int(onoroff)), 8000)

# Turn on Bluetooth
def btpoweron():
    btpower(True);

# Turn off Bluetooth
def btpoweroff():
    btpower(False);

# Get the current status of Bluetooth (0=off,5=idel, other values docuemtned for "AT+BTSTATUS")
def btstatus():
    response = command("AT+BTSTATUS?")
    return int(extractval("+BTSTATUS:", response, "0"))

# Is Bluetooth on?
def btison():
    return btstatus()>=5

# Get/Set the Bluetooth host device name
def btname(name=None):
    if name is not None:
        response = command("AT+BTHOST=" + str(name))
    # Retrieve the current name
    response = command("AT+BTHOST?")
    responsedata = extractval("+BTHOST:", response, "").split(",")
    return responsedata[0]

# Get the Bluetooth address
def btaddress():
    response = command("AT+BTHOST?")
    responsedata = extractval("+BTHOST:", response, "").split(",")
    if (len(responsedata)>=2):
        return responsedata[-1]
    else:
        return ""

# Get/Set Bluetooth visibility (True for on, False for off)
def btvisible(visible=None):
    # Power on if we want to be visible
    if visible:
        btpoweron()
    # Set the new leve if we have one to set
    if visible is not None:
        command("AT+BTVIS=" + str(int(visible)))
    # Retieve the set gain to report back
    response = command("AT+BTVIS?")
    return int(extractval("+BTVIS:", response, 0))

# Get the Bluetooth address (timeout in ms from 10000 to 60000, returnd device ID, name, address, rssi)
def btscan(timeout=30000):
    btpoweron()
    result = []
    response = command("AT+BTSCAN=1," + str(int(timeout/1000)), timeout+8000, "+BTSCAN: 1")
    for entry in extractvals("+BTSCAN: 0,", response):
        splitentry = entry.split(",")
        result.append([int(splitentry[0]), splitentry[1].strip("\""), splitentry[2], int(splitentry[3])])
    return result

# Get the requesting paring device name
def btparingname():
    if ison():
        processbuffer()
    return btpairing.split(",")[0].strip("\"")

# Get the requesting paring passcode
def btparingpasscode():
    if ison():
        processbuffer()
    splitdata = btpairing.split(",")
    if (len(splitdata)>=3):
        return splitdata[2]
    else:
        return ""
    
# Pair a Bluetooth device
def btpair(device):
    global btpairing
    btpairing = ''
    response = command("AT+BTPAIR=0," + str(device), 8000, "+BTPAIRING:")
    return extractval("+BTPAIRING:", response, "").split(",")

# Confirm the pairing of a Bluetooth device
def btpairconfirm(passkey=None):
    global btpairing
    btpairing = ''
    if passkey is None:
        return command("AT+BTPAIR=1,1", 8000)
    else:
        return command("AT+BTPAIR=2," + str(passkey), 8000)

# Cancel/reject the pairing of a Bluetooth device
def btpairreject():
    global btpairing
    btpairing = ''
    return command("AT+BTPAIR=1,0", 8000)

# Unpair a Bluetooth device (unpair everything when device is 0)
def btunpair(device=0):
    return command("AT+BTUNPAIR=" + str(device), 8000)

# List the paired Bluetooth devices
def btpaired():
    result = []
    response = command("AT+BTSTATUS?")
    for entry in extractvals("P:", response):
        splitentry = entry.split(",")
        result = [int(splitentry[0]), splitentry[1].strip("\""), splitentry[2]]
    return result

# List profiles supported by a paired device
def btgetprofiles(device):
    response = command("AT+BTGETPROF=" + str(device), 8000)
    responselist = extractvals("+BTGETPROF:", response)
    results = []
    for entry in responselist:
        splitentry = entry.split(",")
        subresults = [int(splitentry[0]), splitentry[1].strip("\"")]
        results.append(subresults)
    return results

# Is a paticula profile supported (usename=False for id, True for name)
def btprofilesupported(device, usename):
    profiles = btgetprofiles(device)
    for entry in profiles:
        if (type(usename)==int) and (entry[0]==usename):
            return True
        if (type(usename)==str) and (entry[1]==usename):
            return True
    return False
    
# Connect a Bluetooth device
def btconnect(device, profile):
    response = command("AT+BTCONNECT=" + str(device) + "," + str(profile), 8000, "+BTCONNECT:")
    return extractvals("+BTCONNECT:", response)

# Disconnect a Bluetooth device
def btdisconnect(device):
    response = command("AT+BTDISCONN=" + str(device), 8000, "+BTDISCONN:")
    return extractvals("+BTDISCONN:", response)

# List the Bluetooth connections
def btconnected():
    result = []
    response = command("AT+BTSTATUS?")
    for entry in extractvals("C:", response):
        splitentry = entry.split(",")
        result = [int(splitentry[0]), splitentry[1].strip("\""), splitentry[2]]
    return result

# Push an OPP object/file over Bluetooth (must be paired for OPP, monitor +BTOPPPUSH: for sucsess / fail / server issue)
def btopppush(device, filename):
    response = command("AT+BTOPPPUSH=" + str(device) + "," + filename, 45000, "+BTOPPPUSH:")
    responce2 = extractval("+BTOPPPUSH:", response, "")
    return responce2=="1"

# Accept an OPP object/file from Bluetooth (monitor +BTOPPPUSHING: for offering, files stored in "\\User\\BtReceived")
def btoppaccept():
    response = command("AT+BTOPPACPT=1", 45000, "+BTOPPPUSH:")
    responce2 = extractval("+BTOPPPUSH:", response, 0)
    return responce2=="1"

# Send data over a Bluetooth serial connection
def btsppwrite(connection, data):
    response = command("AT+BTSPPSEND=" + str(connection) + "," + str(len(data)), 8000, None, ">")
    if response[-1].startswith(">"):
        return ispositive(command(data)[-1])
    else:
        return False

# Receive data from a Bluetooth serial connection
def btsppread(connection):
    command()
    global holdoffirq
    # Don't let the interupt process the buffer mid command
    holdoffirq = True
    request = "AT+BTSPPGET=3," + str(connection) + "\n"
    uart.write(request)
    data = uart.read()
    while True:
        time.sleep(uart_timeout/1000)
        if uart.any()==0:
            break
        data += uart.read()
    holdoffirq = False
    if not data.endswith("ERROR\r\n"):
        return data[len(request)+2:-6]
    else:
        return None
        
# Reject an OPP object/file transfer
def btoppreject():
    command("AT+BTOPPACPT=0")

# Make a voice call
def btcall(number):
    btpoweron()
    command("AT+BTATD" + str(number), 20000)

# Answer a voice call
def btanswer():
    btpoweron()
    command("AT+BTATA", 20000)

# End a voice call
def bthangup():
    btpoweron()
    command("AT+BTATH")

# Redial the last number
def btredial():
    btpoweron()
    command("AT+BTATDL")

# Play DTMF tone(s) on a Bluetooth call
def btdtmf(number):
    validdigits = '1234567890#*ABCD'
    for digit in str(number).upper():
        if (digit in validdigits):
            command("AT+BTVTS=" + digit)
        elif (digit==','):
            time.sleep(1)

# Get/Set Bluetooth voice gain (0-15)
def btvoicevolume(gain=None):
    # Set the new leve if we have one to set
    if gain is not None:
        command("AT+BTVGS=" + str(gain))
    # Retieve the set gain to report back
    response = command("AT+BTVGS?")
    return int(extractval("+BTVGS:", response, 0))

# Get/Set microphone gain volume (0-15)
def btvoicevolume(gain=None):
    # Set the new leve if we have one to set
    if gain is not None:
        command("AT+BTVGM=" + str(gain))
    # Retieve the set gain to report back
    response = command("AT+BTVGM?")
    return int(extractval("+BTVGM:", response, 0))

# Get the Bluetooth signal quality for a device (-127-0)
def btrssi(device):
    response = command("AT+BTRSSI=" + str(device))
    return int(extractval("+BTRSSI:", response, 0))

# Get available space on the flash storage
def fsfree():
    response = command("AT+FSMEM")
    return extractval("+FSMEM:", response, "?:0bytes").split(",")[0].split(":")[1][:-5]

# List the entries in directory on flash storage (returned directories end with "\\")
def fsls(directory=""):
    if not directory.endswith("\\"):
        directory += "\\"
    return command("AT+FSLS=" + str(directory))[1:-1]

# Get the size of a file on the flash storage
def fssize(filename):
    response = command("AT+FSFLSIZE=" + str(filename))
    return int(extractval("+FSFLSIZE:", response, "-1"))

# Create a directory on flash storage
def fsmkdir(directory):
    return ispositive(command("AT+FSMKDIR=" + str(directory))[-1])

# Remove a directory on flash storage
def fsrmdir(directory):
    return ispositive(command("AT+FSRMDIR=" + str(directory))[-1])

# Create a file on flash storage
def fscreate(filename):
    return ispositive(command("AT+FSCREATE=" + str(filename))[-1])

# Read a chunk of data from a file on the flash storage
def fsreadpart(filename, size=256, start=0):
    global holdoffirq
    mode=int(start>0)
    command()
    # Don't let the interupt process the buffer mid command
    holdoffirq = True
    request = "AT+FSREAD=" + str(filename) + "," + str(mode) + "," + str(size) + "," + str(start) + "\n"
    uart.write(request)
    data = uart.read()
    while True:
        time.sleep(uart_timeout/1000)
        if uart.any()==0:
            break
        data += uart.read()
    holdoffirq = False
    if not data.endswith("ERROR\r\n"):
        return data[len(request)+2:-6]
    else:
        return None

# Read data from a file on the flash storage
def fsread(filename):
    result = bytearray(0)
    while True:
        chunk = fsreadpart(filename, 256, len(result))
        if chunk is not None:
            result += chunk
        else:
            return result

# Append a small chunk data to a file on the flash storage, you should use sfwrite
def fswritepart(filename, data):
    response = command("AT+FSWRITE=" + str(filename) + ",1," + str(len(data)) + ",8", 2000, None, ">")
    if response[-1].startswith(">"):
        return ispositive(command(data)[-1])
    else:
        return False

# Write data to a file on the flash storage
def fswrite(filename, data, truncate=False):
    length = len(data)
    pointer = 0
    chunksize = 256
    # Create a file if needed
    if truncate or (fssize(filename)<0):
        fscreate(filename)
    # Loop through the data in small chunks
    while pointer<length:
        result = fswritepart(filename, data[pointer:min(pointer+chunksize,length)])
        if not result:
            return False
        pointer += chunksize
    return True

# Delete a file from flash storage
def fsrm(filename):
    return ispositive(command("AT+FSDEL=" + str(filename))[-1])

# Rename a file on the flash storage
def fsmv(filenamefrom, filenameto):
    return ispositive(command("AT+FSRENAME=" + str(filenamefrom) + "," + str(filenameto))[-1])

# Callback for call buton being pressed
def callbuttonpressed_internal(nullparam=None):
    answer()

# Callback for end buton being pressed
def endbuttonpressed_internal(nullparam=None):
    hangup()


# Startup...

# Start turning on the SIM800 asynchronously
onatstart = poweron(True)

# Reset SIM800 configuration if hardware is still on from before 
if onatstart:
    senddefaultconfig()

# Turn on the audio amp
amp_pin.on()

# Hook in the Call / End buttons
tilda.Buttons.enable_interrupt(tilda.Buttons.BTN_Call, callbuttonpressed_internal)
tilda.Buttons.enable_interrupt(tilda.Buttons.BTN_End, endbuttonpressed_internal)

# Enable the interupts on network light to poll uart
netlight_pin.irq(netlightirq_internal)
