"""Handles connecting to a wifi access point based on a valid wifi.json file"""

___license___      = "MIT"
___dependencies___ = ["dialogs", "sleep"]

import network, os, json, dialogs, sleep, time

_nic = None

def nic():
    global _nic
    if not _nic:
        _nic = network.WLAN()
        _nic.active(True)
    return _nic

def connection_details():
    data = None
    try:
        if "wifi.json" in os.listdir():
            with open("wifi.json") as f:
                data = json.loads(f.read())
                if 'ssid' not in data or not data['ssid']:
                    data = None
    except ValueError as e:
        print(e)

    return data

def ssid():
    return connection_details()["ssid"]

def connect(wait=True, timeout=10, show_wait_message=False, prompt_on_fail=True, dialog_title='TiLDA'):
    while True:
        if nic().isconnected():
            return

        details = connection_details()
        if not details:
            if prompt_on_fail:
                choose_wifi(dialog_title=dialog_title)
            else:
                raise OSError("No valid wifi configuration")

        if not wait:
            connect_wifi(details, timeout=None, wait=False)
            return
        else:
            try:
                if show_wait_message:
                    with dialogs.WaitingMessage(text="Connecting to '%s'...\n(%ss timeout)" % (details['ssid'], timeout), title=dialog_title):
                        connect_wifi(details, timeout=timeout, wait=True)
                else:
                    connect_wifi(details, timeout=timeout, wait=True)
            except OSError:
                if prompt_on_fail:
                    retry_connect = dialogs.prompt_boolean(
                        text="Failed to connect to '%s'" % details['ssid'],
                        title=dialog_title,
                        true_text="Try again",
                        false_text="Change it",
                    )
                    if not retry_connect:
                        os.remove('wifi.json')
                        os.sync()

                else:
                    raise

def connect_wifi(details, timeout, wait=False):
    if 'user' in details:
        nic().connect(details['ssid'], details['pw'], enterprise=True, entuser=details['user'], entmethod=nic().EAP_METHOD_PEAP0_MSCHAPv2, entserverauth=False)
    elif 'pw' in details:
        nic().connect(details['ssid'], details['pw'])
    else:
        nic().connect(details['ssid'])

    if wait:
        while not nic().isconnected():
            sleep.sleep_ms(100)


def is_connected():
    return nic().isconnected()

# returns wifi strength in %, None if unavailable
def get_strength():
    n = nic()
    if n.isconnected():
        v = n.status("rssi");
        if v:
            # linear range: -60 =100%; -100= 20%
            # todo: it's probably not linear, improve me.
            return v * 2 + 220
    return None

def get_security_level(ap):
    #todo: fix this
    n = nic()
    levels = {
        n.SCAN_SEC_OPEN: 0, # I am awful
        n.SCAN_SEC_WEP: 'WEP',
        n.SCAN_SEC_WPA: 'WPA',
        n.SCAN_SEC_WPA2: 'WPA2',
    }

    return levels.get(ap.get('security', None), None)

def choose_wifi(dialog_title='TiLDA'):
    filtered_aps = []
    with dialogs.WaitingMessage(text='Scanning for networks...', title=dialog_title):
        visible_aps = None
        while not visible_aps:
            visible_aps = nic().scan()
            print(visible_aps)
            sleep.sleep_ms(300)
            #todo: timeout
        visible_aps.sort(key=lambda x:x[3], reverse=True)
        # We'll get one result for each AP, so filter dupes
        for ap in visible_aps:
            title = ap[0]
            security = "?" # todo: re-add get_security_level(ap)
            if security:
                title = title + ' (%s)' % security
            ap = {
                'title': title,
                'ssid': ap[0],
                'security': ap[4],
            }
            if ap['ssid'] not in [ a['ssid'] for a in filtered_aps ]:
                filtered_aps.append(ap)
        del visible_aps

    ap = dialogs.prompt_option(
        filtered_aps,
        text='Choose wifi network',
        title=dialog_title
    )
    if ap:
        key = None
        if ap['security'] != 0:
            # Backward compat
            if ap['security'] == None:
                ap['security'] = 'wifi'

            key = dialogs.prompt_text("Enter %s key" % ap['security'])
        with open("wifi.json", "wt") as file:
            if key:
                conn_details = {"ssid": ap['ssid'], "pw": key}
            else:
                conn_details = {"ssid": ap['ssid']}

            file.write(json.dumps(conn_details))
        os.sync()
        # todo: last time we had to hard reset here, is that still the case?
