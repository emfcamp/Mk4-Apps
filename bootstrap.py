"""Bootstraps the badge by downloading the base software"""

import ugfx, machine, network, json, time, usocket, os

HOST = "badgeserver.emfcamp.org"

# Helpers
def msg(text):
    ugfx.clear()
    ugfx.text(5, 5, "EMF 2018", ugfx.BLACK)
    ugfx.text(5, 30, "TiLDA Mk4", ugfx.BLACK)
    lines = text.split("\n")
    print(lines[0])
    for i, line in enumerate(lines):
        ugfx.text(5, 65 + i * 20, line, ugfx.BLACK)

def wifi_details():
    if not "wifi.json" in os.listdir():
        with open("wifi.json", "w") as f:
            f.write('{"ssid":"emfcamp","pw":"emfemf"}')
    with open("wifi.json") as f:
        return json.loads(f.read())

def connect(wifi):
    details = wifi_details()
    if 'pw' in details:
        wifi.connect(details['ssid'], details['pw'])
    else:
        wifi.connect(details['ssid'])

    wait_until = time.ticks_ms() + 10000
    while not wifi.isconnected():
        if (time.ticks_ms() > wait_until):
            raise OSError("Timeout while trying to\nconnect to wifi.\n\nPlease connect your\nbadge to your computer\nand edit wifi.json with\nyour wifi details");
        time.sleep(0.1)

def get(path):
    s = usocket.socket()
    s.connect(usocket.getaddrinfo(HOST, 80)[0][4])
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
    msg("Connecting to wifi...");
    wifi = network.WLAN()
    wifi.active(True)
    if not wifi.isconnected():
        connect(wifi)

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
