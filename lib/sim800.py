import machine
import time

uart_port = 1
uart_default_baud = 115200
uart_timeout = 28
default_responce_timeout = 2000

status_pin = Pin(6, Pin.IN)
ringer_pin = Pin(8, Pin.IN)
pwr_key_pin = Pin(23, Pin.OUT)

# Open the UART
uart = machine.UART(uart_port, uart_default_baud, mode=UART.BINARY, timeout=uart_timeout)
dirtybuffer = False # Flag if the buffer could have residual end of responces line in it?

# Check if the SIM800 is powered up
def ison():
    return status_pin.value()==1

# Check if the SIM800 is ringing
def isringing():
    return ringer_pin.value()==0

# Identify if this was a positive responce
def ispositive(responce):
    return (responce=="OK") or responce.startswith("CONNECT") or responce.startswith("> ")

# Identify if this was a negative responce
def isnegative(responce):
    return (responce=="NO CARRIER") or (responce=="ERROR") or (responce=="NO DIALTONE") or (responce=="BUSY") or (responce=="NO ANSWER")

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
# command is the AT command without the AT or CR/LF, responce_timeout (in ms) is how long to wait for completion, custom_endofdata is to wait for a non standard bit of 
def command(command="AT", responce_timeout=default_responce_timeout, custom_endofdata=None):
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
    customcomplete = custom_endofdata is None
    timeouttime = time.time()+(responce_timeout/1000)
    while (time.time()<timeouttime):
        line = readline()
        # Remember the line if not empty
        if (len(line)>0):
            result.append(line)
        # Check if we have a standard end of responce
        if (ispositive(line)) or (isnegative(line)):
            complete = True
        # Check if we have the data we are looking for
        if (custom_endofdata is not None) and (line.startswith(custom_endofdata)):
            customcomplete = True
        # Check if we are done
        if complete and customcomplete:
            return result
    # We ran out of time
    # set the dirty buffer flag is an out of date end of responcs cound end up in the buffer
    if custom_endofdata is None:
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

# End a voice call
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
    command("AT+CMGS=\"" + str(number) + "\"")
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
    
# Start turning on the SIM800
poweron(True)

