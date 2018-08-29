"""Bootstraps the badge by downloading the base software"""

import ugfx, machine, network, json, time, usocket, os, gc
from tilda import Buttons

HOST = "badgeserver.emfcamp.org"
wifi = network.WLAN()
wifi.active(True)

# Helpers
def msg(text):
    ugfx.clear()
    ugfx.text(5, 5, "EMF 2018", ugfx.BLACK)
    ugfx.text(5, 30, "TiLDA Mk4", ugfx.BLACK)
    lines = text.split("\n")
    print(lines[0])
    for i, line in enumerate(lines):
        ugfx.text(5, 65 + i * 20, line, ugfx.BLACK)

def wifi_select():
    msg("Please select your wifi\nConfirm with button A")
    sl = ugfx.List(5, 110, 228, 204)
    aps = {}
    while not Buttons.is_pressed(Buttons.BTN_A):
        for s in (wifi.scan() or []):
            if s[0] not in aps:
                sl.add_item(s[0])
                aps[s[0]] = s
        time.sleep(0.01)
        ugfx.poll()
    ssid = sl.selected_text()
    sl.destroy()

    msg("Wifi: %s\nPlease enter your password\nConfirm with button A" % ssid)
    kb = ugfx.Keyboard(0, 160, 240, 170)
    e = ugfx.Textbox(5, 130, 228, 25, text="")
    while not Buttons.is_pressed(Buttons.BTN_A):
        time.sleep(0.01)
        ugfx.poll()
    pw = e.text()
    e.destroy()
    kb.destroy()
    result = {"ssid":ssid,"pw":pw}
    with open("wifi.json", "wt") as file:
        file.write(json.dumps(result))
        file.flush()
    os.sync()
    return result

def wifi_details():
    try:
        with open("wifi.json") as f:
            return json.loads(f.read())
    except Exception as e:
        print(str(e))
        return wifi_select()

def connect():
    details = wifi_details()
    if 'user' in details:
        wifi.connect(details['ssid'], details['pw'], enterprise=True, entuser=details['user'], entmethod=wifi.EAP_METHOD_PEAP0_MSCHAPv2, entserverauth=False)
    elif 'pw' in details:
        wifi.connect(details['ssid'], details['pw'])
    else:
        wifi.connect(details['ssid'])

    wait_until = time.ticks_ms() + 10000
    while not wifi.isconnected():
        if (time.ticks_ms() > wait_until):
            os.remove("wifi.json")
            raise OSError("Wifi timeout");
        time.sleep(0.1)

def addrinfo(host, port, retries_left = 20):
    try:
        return usocket.getaddrinfo(host, port)[0][4]
    except OSError as e:
        if ("-15" in str(e)) and retries_left:
            # [addrinfo error -15]
            # This tends to happen after startup and goes away after a while
            time.sleep_ms(200)
            return addrinfo(host, port, retries_left - 1)
        else:
            raise e

def get(path):
    s = usocket.socket()
    s.connect(addrinfo(HOST, 80))
    body = b""
    status = None
    try:
        s.send('GET /2018/%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, HOST))
        state = 1
        hbuf = b""
        clen = 9999999
        headers = {}
        while len(body) < clen:
            buf = s.recv(1024)
            if state == 1: # Status
                nl = buf.find(b"\n")
                if nl > -1:
                    hbuf += buf[:nl - 1]
                    status = int(hbuf.split(b' ')[1])
                    state = 2
                    hbuf = b"";
                    buf = buf[nl + 1:]
                else:
                    hbuf += buf

            if state == 2: # Headers
                hbuf += buf
                nl = hbuf.find(b"\n")
                while nl > -1:
                    if nl < 2:
                        buf = hbuf[2:]
                        hbuf = None
                        state = 3
                        clen = int(headers["content-length"])
                        break

                    header = hbuf[:nl - 1].decode("utf8").split(':', 3)
                    headers[header[0].strip().lower()] = header[1].strip()
                    hbuf = hbuf[nl + 1:]
                    nl = hbuf.find(b"\n")

            if state == 3: # Content
                body += buf

    finally:
        s.close()
    if status != 200:
        raise Exception("HTTP %d for %s" % (status, path))
    return body

# os.path bits
def split(path):
    if path == "":
        return ("", "")
    r = path.rsplit("/", 1)
    if len(r) == 1:
        return ("", path)
    head = r[0]
    if not head:
        head = "/"
    return (head, r[1])

def dirname(path):
    return split(path)[0]

def exists(path):
    try:
        os.stat(path)[0]
        return True
    except OSError:
        return False

def makedirs(path):
    sub_path = split(path)[0]
    if sub_path and (not exists(sub_path)):
        makedirs(sub_path)
    if not exists(path):
        os.mkdir(path)

# Steps
def step_wifi():
    while not wifi.isconnected():
        msg("Connecting to wifi...");
        try:
            connect()
        except Exception as e:
            print(str(e))
            msg("Couldn't connect\nPlease check wifi details")
            time.sleep(1)

def step_download():
    msg("Connecting to server...")
    files = list(json.loads(get("bootstrap")).keys())
    for i, file in enumerate(files):
        msg("Downloading - %d%%\n%s" % (100 * i // len(files), file))
        makedirs(dirname(file))
        with open(file, 'wb') as f:
            f.write(get("download?repo=emfcamp/Mk4-Apps&path=%s" % file))
    os.sync()

def step_goodbye():
    msg("All done!\n\nRestarting badge...")
    time.sleep(2)
    machine.reset()

ugfx.init()
machine.Pin(machine.Pin.PWM_LCD_BLIGHT).on()
try:
    step_wifi()
    step_download()
    step_goodbye()
except Exception as e:
    msg("Error\nSomething went wrong :(\n\n" + str(e))
    raise e
