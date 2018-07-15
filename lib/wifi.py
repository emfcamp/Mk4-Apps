"""Handles connecting to a wifi access point based on a valid wifi.json file"""

___license___      = "MIT"
___dependencies___ = ["dialogs"]

import network
import os
import json
import pyb
import dialogs

_nic = None

def nic():
    global _nic
    if not _nic:
        _nic = network.CC3100()
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
    retry_connect = True

    while retry_connect:
        if nic().is_connected():
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
                        false_text="Forget it",
                    )
                    if not retry_connect:
                        os.remove('wifi.json')
                        os.sync()
                        # We would rather let you choose a new network here, but
                        # scanning doesn't work after a connect at the moment
                        pyb.hard_reset()
                else:
                    raise

def connect_wifi(details, timeout, wait=False):
    if 'pw' in details:
        nic().connect(details['ssid'], details['pw'], timeout=timeout)
    else:
        nic().connect(details['ssid'], timeout=timeout)

    if wait:
        while not nic().is_connected():
            nic().update()
            pyb.delay(100)

def is_connected():
    return nic().is_connected()

def get_security_level(ap):
    n = nic()
    levels = {}
    try:
        levels = {
            n.SCAN_SEC_OPEN: 0, # I am awful
            n.SCAN_SEC_WEP: 'WEP',
            n.SCAN_SEC_WPA: 'WPA',
            n.SCAN_SEC_WPA2: 'WPA2',
        }
    except AttributeError:
        print("Firmware too old to query wifi security level, please upgrade.")
        return None

    return levels.get(ap.get('security', None), None)

def choose_wifi(dialog_title='TiLDA'):
    filtered_aps = []
    with dialogs.WaitingMessage(text='Scanning for networks...', title=dialog_title):
        visible_aps = nic().list_aps()
        visible_aps.sort(key=lambda x:x['rssi'], reverse=True)
        # We'll get one result for each AP, so filter dupes
        for ap in visible_aps:
            title = ap['ssid']
            security = get_security_level(ap)
            if security:
                title = title + ' (%s)' % security
            ap = {
                'title': title,
                'ssid': ap['ssid'],
                'security': security,
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

            key = dialogs.prompt_text(
                "Enter %s key" % ap['security'],
                width = 310,
                height = 220
            )
        with open("wifi.json", "wt") as file:
            if key:
                conn_details = {"ssid": ap['ssid'], "pw": key}
            else:
                conn_details = {"ssid": ap['ssid']}

            file.write(json.dumps(conn_details))
        os.sync()
        # We can't connect after scanning for some bizarre reason, so we reset instead
        pyb.hard_reset()
