import machine
import time
import micropython

CALLER_CALLBACK = 1
CLI_CALLBACK = 2
NEWSMS_CALLBACK = 3

uart_port = 1
uart_default_baud = 115200
uart_timeout = 28
default_response_timeout = 2000

status_pin = machine.Pin(machine.Pin.GPIO_SIM_STATUS, machine.Pin.IN)
ringer_pin = machine.Pin(machine.Pin.GPIO_SIM_RI, machine.Pin.IN)
pwr_key_pin = machine.Pin(machine.Pin.GPIO_SIM_PWR_KEY, machine.Pin.OUT)

# Open the UART
uart = machine.UART(uart_port, uart_default_baud, mode=machine.UART.BINARY, timeout=uart_timeout)
dirtybuffer = False # Flag if the buffer could have residual end of reresponsesponces line in it?

callbacks = []

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
    
# Execute external funtion of a callback
def callcallback(call, parameter):
    for entry in callbacks:
        if entry[0]==call:
            micropython.schedule(entry[1], parameter)

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
            stringin += str(charin, "ASCII")

def processcallbacks(line):
    # Check for ringing
    if line=="RING":
        callcallback(CALLER_CALLBACK, "")
    # Check for new caler lin identification
    val = extractval("+CLIP:", [line])
    if val:
        callcallback(CLI_CALLBACK, val)
    # Check for new SMS messages
    val = extractval("+CMT:", [line])
    if val:
        callcallback(NEWSMS_CALLBACK, val)

# Process the buffer for  unsolicited result codes 
def processbuffer():
    while uart.any()>0:
        line = readline()
        processcallbacks(line)
        
# Execute a command on the module
# The same interface as and called by command() but without power so can be called from power()
def command_internal(command="AT", response_timeout=default_response_timeout, required_response=None, custom_endofdata=None):
    global dirtybuffer
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
            return result
    # We ran out of time
    # set the dirty buffer flag is an out of date end of responcs cound end up in the buffer
    if required_response is None:
        dirtybuffer = True
    result.append("TIMEOUT")
    return result

# Power on the SIM800 (True=on, False=off, returns true when on)
def power(onoroff, async):
    # Get to a stable state if not async
    if not async and pwr_key_pin.value():
        pwr_key_pin.off()
        time.sleep(3)
	# Press the virtual power key if we are off
    if not (ison()==onoroff):
        pwr_key_pin.on()
        if not async:
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
            # Send a command to autonigotiate UART speed
            command_internal("AT")
            # Turn on new SMS notificationn
            command_internal("AT+CNMI=1,2")
            # Turn on calling line identification notification
            command_internal("AT+CLIP=1")
    return isonnow

# Power on the SIM800 (returns true when on)
def poweron(async=False):
    return power(True, async)

# Power off the SIM800
def poweroff(async=False):
    return power(False, async)

# Change the speed on the communication
def uartspeed(newbaud):
    global uart
    command("AT+IPR=" + str(newbaud))
    uart.deinit()
    if (newbaud==0):
        uart = machine.UART(uart_port, uart_default_baud, mode=UART.BINARY, timeout=uart_timeout)
    else:
        uart = machine.UART(uart_port, newbaud, mode=UART.BINARY, timeout=uart_timeout)

# command is the AT command without the AT or CR/LF, response_timeout (in ms) is how long to wait for completion, required_response is to wait for a non standard response, custom_endofdata will finish when found
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

# play a tone though the SIM800 (MHz and ms)
def playtone(freq=0,duration=2000,async=True):
    if freq>0:
        command("AT+SIMTONE=1," + str(freq) + "," + str(duration) + ",0," + str(duration))
        if not async:
            time.sleep(duration/1000)
    else:
        command("AT+SIMTONE=0")

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
            params += "," + str(operator)
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
        return responsedata[1].strip().strip("\"")
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

# Get/Set Bluetooth visibility
def btvisible(visible=None):
    # Set the new leve if we have one to set
    if visible is not None:
        command("AT+BTVIS=" + str(visible))
    # Retieve the set gain to report back
    response = command("AT+BTVIS?")
    return int(extractval("+BTVIS:", response, 0))

# Get the Bluetooth address (timeout from 10000 to 60000, returnd device ID, name, address, rssi)
def btscan(timeout=30000):
    response = command("AT+BTSCAN=1," + str(int(timeout/1000)), timeout+8000, "+BTSCAN: 1")
    return extractvals("+BTSCAN: 0,", response)

# Pair a Bluetooth device
def btpair(device):
    response = command("AT+BTPAIR=0," + str(device), 8000, "+BTPAIRING:")
    return extractval("+BTPAIRING:", response, "").split(",")

# Confirm the pairing of a Bluetooth device
def btpairconfirm(passkey=None):
    if passkey is None:
        return command("AT+BTPAIR=1,1", 8000)
    else:
        return command("AT+BTPAIR=2," + str(passkey), 8000)

# Cancel/reject the pairing of a Bluetooth device
def btpairreject():
    return command("AT+BTPAIR=1,0", 8000)

# Unpair a Bluetooth device (unpair everything when device is 0)
def btunpair(device=0):
    return command("AT+BTUNPAIR=" + str(device), 8000)

# List the paired Bluetooth devices
def btpaired():
    response = command("AT+BTSTATUS?")
    return extractvals("P:", response)

# List profiles supported by a paired device
def btgetprofiles(device):
    response = command("AT+BTGETPROF=" + str(device), 8000)
    responselist = extractvals("+BTGETPROF:", response)
    results = []
    for entry in responselist:
        subresults = []
        for subentry in entry.split(","):
            subresults.append(subentry.strip("\""))
        results.append(subresults)
    return results
		
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
    response = command("AT+BTSTATUS?")
    return extractvals("C:", response)

# Make a voice call
def btcall(number):
    command("AT+BTATD" + str(number), 20000)

# Answer a voice call
def btanswer():
    command("AT+BTATA", 20000)

# End a voice call
def bthangup():
    command("AT+BTATH")

# Redial the last number
def btredial():
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

# Read data from a file on the flash storage
def fsread(filename, size=1024, start=0):
    mode=int(start>0)
    return command("AT+FSREAD=" + str(filename) + "," + str(mode) + "," + str(size) + "," + str(start))[1:-1]

# Write data to a file on the flash storage
def fswrite(filename, data, append=True, truncate=False):
    if truncate or (fssize(filename)<0):
        fscreate(filename)
    response = command("AT+FSWRITE=" + str(filename) + "," + str(int(append)) + "," + str(len(data)) + ",8", 2000, None, ">")
    if response[-1].startswith(">"):
        return ispositive(command(data)[-1])
    else:
        return False

# Delete a file from flash storage
def fsrm(filename):
    return ispositive(command("AT+FSDEL=" + str(filename))[-1])

# Rename a file on the flash storage
def fsmv(filenamefrom, filenameto):
    return ispositive(command("AT+FSRENAME=" + str(filenamefrom) + "," + str(filenameto))[-1])


# Start turning on the SIM800
onatstart = poweron(True)

# Testing code to move to app
# Try using call and end buttons to answer and hangup
#tilda.Buttons.enable_interrupt(tilda.Buttons.BTN_Call, answer())
#tilda.Buttons.enable_interrupt(tilda.Buttons.BTN_End, hangup())
# See if the netowrk list can be used for checking SIM800
#status_pin = machine.Pin(7, machine.Pin.IN)
#tilda.Buttons.enable_interrupt(machine.Pin(machine.Pin.GPIO_SIM_NETLIGHT, machine.Pin.IN),processbuffer())
