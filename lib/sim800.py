import machine
import time

uart_port = 1
uart_default_baud = 115200
uart_timeout = 28
default_responce_timeout = 2000

status_pin = machine.Pin(6, machine.Pin.IN)
ringer_pin = machine.Pin(8, machine.Pin.IN)
pwr_key_pin = machine.Pin(23, machine.Pin.OUT)

# Open the UART
uart = machine.UART(uart_port, uart_default_baud, mode=machine.UART.BINARY, timeout=uart_timeout)
dirtybuffer = False # Flag if the buffer could have residual end of responces line in it?

# Check if the SIM800 is powered up
def ison():
    return status_pin.value()==1

# Check if the SIM800 is ringing
def isringing():
    return ringer_pin.value()==0

# Identify if this was a positive responce
def ispositive(responce):
    return (responce=="OK") or responce.startswith("CONNECT") or responce.startswith("SEND OK")

# Identify if this was a negative responce
def isnegative(responce):
    return (responce=="NO CARRIER") or (responce=="ERROR") or (responce=="NO DIALTONE") or (responce=="BUSY") or (responce=="NO ANSWER") or (responce=="SEND FAIL") or (responce=="TIMEOUT") or (responce=="TimeOut")

# Identify if this is the completion of a responce
def isdefinitive(responce, custom=None):
    if custom is not None:
        return ispositive(responce) or isnegative(responce) or responce.startswith(custom)
    else:
        return ispositive(responce) or isnegative(responce)

# Extract the [first/only] parameter from a responce 
def extractval(parameter, responce, default=""):
    for entry in responce:
        if entry.startswith(parameter):
            return (entry[len(parameter):]).strip()
    return default

# Extract all parameter from a responce 
def extractvals(parameter, responce):
    result = []
    for entry in responce:
        if entry.startswith(parameter):
            result.append((entry[len(parameter):]).strip())
    return result

# Read a lines of responce from the UART
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

# Execute a command on the module
# command is the AT command without the AT or CR/LF, responce_timeout (in ms) is how long to wait for completion, required_responce is to wait for a non standard responce, custom_endofdata will finish when found
def command(command="AT", responce_timeout=default_responce_timeout, required_responce=None, custom_endofdata=None):
    global dirtybuffer
    # Empty the buffer
    uart.read()
    # Do not bother if we are powered off
    if not ison():
        dirtybuffer = False
        return ["POWERED OFF"]
    # Send the command
    uart.write(command + "\r")
    # Read the results
    result = []
    complete = False
    customcomplete = required_responce is None
    timeouttime = time.time()+(responce_timeout/1000)
    while (time.time()<timeouttime):
        line = readline()
        # Remember the line if not empty
        if (len(line)>0):
            result.append(line)
        # Check if we have a standard end of responce
        if isdefinitive(line, custom_endofdata):
            complete = True
        # Check if we have the data we are looking for
        if (required_responce is not None) and (line.startswith(required_responce)):
            customcomplete = True
        # Check if we are done
        if complete and customcomplete:
            return result
    # We ran out of time
    # set the dirty buffer flag is an out of date end of responcs cound end up in the buffer
    if required_responce is None:
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
        uart.read()
        dirtybuffer = False
		# Send a command to autonigotiate UART speed
        if isonnow:
            command("AT")
    return isonnow

# Power on the SIM800 (returns true when on)
def poweron(async=False):
    power(True, async)

# Power off the SIM800
def poweroff(async=False):
    power(False, async)

# Change the speed on the communication
def uartspeed(newbaud):
    global uart
    command("AT+IPR=" + str(newbaud))
    uart.deinit()
    if (newbaud==0):
        uart = machine.UART(uart_port, uart_default_baud, mode=UART.BINARY, timeout=uart_timeout)
    else:
        uart = machine.UART(uart_port, newbaud, mode=UART.BINARY, timeout=uart_timeout)

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
    responce = command("AT+CMGR=" + str(index) + "," + str(int(leaveunread)), 5000)
    if (len(responce)>=3):
        return responce[-2]
    else:
        return ""

# Delete an SMS message
def deletesms(index):
    command("AT+CMGD=" + str(index), 5000)

# Get the IMEI number of the SIM800
def imei():
    responce = command("AT+GSN")
    if (len(responce)>=2):
        return responce[-2]
    else:
        return ""

# Get the IMSI number of the Sim Card
def imsi():
    responce = command("AT+CIMI")
    if (len(responce)>=2):
        return responce[-2]
    else:
        return ""

# Get/Set ringer volume (0-100)
def ringervolume(level=None):
    # Set the new leve if we have one to set
    if level is not None:
        command("AT+CRSL=" + str(level))
    # Retieve the set level to report back
    responce = command("AT+CRSL?")
    return int(extractval("+CRSL:", responce, 0))

# Get/Set speaker volume (0-100)
def speakervolume(level=None):
    # Set the new leve if we have one to set
    if level is not None:
        command("AT+CLVL=" + str(level))
    # Retieve the set level to report back
    responce = command("AT+CLVL?")
    return int(extractval("+CLVL:", responce, 0))

# Get/Set/Preview and set the ringtone (alert is 0-19)
def ringtone(alert=None,preview=False):
    # Set/preview the new ringtone if we have one to set
    if alert is not None:
        command("AT+CALS=" + str(alert) + "," + str(int(preview)))
    # Retieve the current/new setting
    responce = command("AT+CALS?")
    current = extractval("+CALS:", responce, 0).split(",")[0]
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
    responce = command("AT+CBC")
    vals = extractval("+CBC:", responce, "0,0,0").split(",")
    return int(vals[0])

# How full is the battery (1-100)
def batterycharge():
    responce = command("AT+CBC")
    vals = extractval("+CBC:", responce, "0,0,0").split(",")
    return int(vals[1])
    
# List the available operator (returns list of [0=?,1=available,2=current,3=forbidden], 0=long name, 1=short name, 2=GSMLAI )
def listoperators(available_only=True):
    delim = "||||"
    responce = command("AT+COPS=?", 45000)
    responcedata = extractval("+COPS:", responce, "").split(",,")[0]
    responcelist = responcedata.replace("),(",delim)[1:-1].split(delim)
    results = []
    for entry in responcelist:
        subresults = []
        for subentry in entry.split(","):
            subresults.append(subentry.strip("\""))
        if (not available_only) or (subresults[0]=="1") or (subresults[0]=="2"):
            results.append(subresults)
    return results

# Get the current operator (format 0=long name, 1=short name, 2=GSMLAI)
def currentoperator(format=0):
    command("AT+COPS=3," + str(format))
    responce = command("AT+COPS?")
    responcedata = extractval("+COPS:", responce, "").split(",")
    if (len(responcedata)>=3):
        return responcedata[2].strip("\"")
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
    responce = command("AT+CPAS")
    return int(extractval("+CPAS:", responce, "2"))
    
# Get the firmware revision
def getfirmwarever():
    responce = command("AT+CGMR")
    if (len(responce)>=3):
        return responce[-2]
    else:
        return ""

# Request Unstructured Supplementary Service Data from network
def ussd(ussdstring, timeout=8000):
    responce = command("AT+CUSD=1,\"" + ussdstring + "\"", timeout, "+CUSD:")
    return extractval("+CUSD:", responce, "")

# Get my number (only works on some networks)
def getmynumber():
    responcedata = ussd("*#100#", 8000).split(",")
    if (len(responcedata)>=2):
        return responcedata[1].strip().strip("\"")
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
    responce = command("AT+BTSTATUS?")
    return int(extractval("+BTSTATUS:", responce, "0"))

# Is Bluetooth on?
def btison():
    return btstatus()>=5

# Get/Set the Bluetooth host device name
def btname(name=None):
    if name is not None:
        responce = command("AT+BTHOST=" + str(name))
    # Retrieve the current name
    responce = command("AT+BTHOST?")
    responcedata = extractval("+BTHOST:", responce, "").split(",")
    return responcedata[0]

# Get the Bluetooth address
def btaddress():
    responce = command("AT+BTHOST?")
    responcedata = extractval("+BTHOST:", responce, "").split(",")
    if (len(responcedata)>=2):
        return responcedata[-1]
    else:
        return ""

# Get/Set Bluetooth visibility
def btvisible(visible=None):
    # Set the new leve if we have one to set
    if visible is not None:
        command("AT+BTVIS=" + str(visible))
    # Retieve the set gain to report back
    responce = command("AT+BTVIS?")
    return int(extractval("+BTVIS:", responce, 0))

# Get the Bluetooth address (timeout from 10000 to 60000, returnd device ID, name, address, rssi)
def btscan(timeout=30000):
    responce = command("AT+BTSCAN=1," + str(int(timeout/1000)), timeout+8000, "+BTSCAN: 1")
    return extractvals("+BTSCAN: 0,", responce)

# Pair a Bluetooth device
def btpair(device):
    responce = command("AT+BTPAIR=0," + str(device), 8000, "+BTPAIRING:")
    return extractval("+BTPAIRING:", responce, "").split(",")

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
    responce = command("AT+BTSTATUS?")
    return extractvals("P:", responce)

# List profiles supported by a paired device
def btgetprofiles(device):
    responce = command("AT+BTGETPROF=" + str(device), 8000)
    responcelist = extractvals("+BTGETPROF:", responce)
    results = []
    for entry in responcelist:
        subresults = []
        for subentry in entry.split(","):
            subresults.append(subentry.strip("\""))
        results.append(subresults)
    return results
		
# Connect a Bluetooth device
def btconnect(device, profile):
    responce = command("AT+BTCONNECT=" + str(device) + "," + str(profile), 8000, "+BTCONNECT:")
    return extractvals("+BTCONNECT:", responce)

# Disconnect a Bluetooth device
def btdisconnect(device):
    responce = command("AT+BTDISCONN=" + str(device), 8000, "+BTDISCONN:")
    return extractvals("+BTDISCONN:", responce)

# List the Bluetooth connections
def btconnected():
    responce = command("AT+BTSTATUS?")
    return extractvals("C:", responce)

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
    responce = command("AT+BTVGS?")
    return int(extractval("+BTVGS:", responce, 0))

# Get/Set microphone gain volume (0-15)
def btvoicevolume(gain=None):
    # Set the new leve if we have one to set
    if gain is not None:
        command("AT+BTVGM=" + str(gain))
    # Retieve the set gain to report back
    responce = command("AT+BTVGM?")
    return int(extractval("+BTVGM:", responce, 0))

# Get the Bluetooth signal quality for a device (-127-0)
def btrssi(device):
    responce = command("AT+BTRSSI=" + str(device))
    return int(extractval("+BTRSSI:", responce, 0))




# Get available space on the flash storage
def fsfree():
    responce = command("AT+FSMEM")
    return extractval("+FSMEM:", responce, "?:0bytes").split(",")[0].split(":")[1][:-5]

# List the entries in directory on flash storage (returned directories end with "\\")
def fsls(directory=""):
    if not directory.endswith("\\"):
        directory += "\\"
    return command("AT+FSLS=" + str(directory))[1:-1]

# Get the size of a file on the flash storage
def fssize(filename):
    responce = command("AT+FSFLSIZE=" + str(filename))
    return int(extractval("+FSFLSIZE:", responce, "-1"))

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
    responce = command("AT+FSWRITE=" + str(filename) + "," + str(int(append)) + "," + str(len(data)) + ",8", 2000, None, ">")
    if responce[-1].startswith(">"):
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
poweron(True)

# Testing code to move to app
#tilda.Buttons.enable_interrupt(tilda.Buttons.BTN_Call, answer())
#tilda.Buttons.enable_interrupt(tilda.Buttons.BTN_End, hangup())

