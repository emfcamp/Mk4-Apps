import os, sync, json

def select_wifi():
    ssid = input('Enter wifi name (SSID): ')
    pw = input('Enter wifi password, leave empty for open network: ')
    with open(os.path.join(sync.get_root(), "wifi.json"), "wt") as file:
        if pw:
            conn_details = {"ssid": ssid, "pw": pw}
        else:
            conn_details = {"ssid": ssid}

        file.write(json.dumps(conn_details))
    print("wifi.json created - It will be transfered to the badge on the next sync")
