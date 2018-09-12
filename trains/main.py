"""Mini train departure board for your badge

Configurable with which station you want to monitor
"""
___title___ = "trains"
___license___ = "MIT"
___dependencies___ = ["app", "sleep", "wifi", "http", "ugfx_helper"]
___categories___ = ["Homescreens", "Other"]

# Config

STATION_CODE = "DEP"
API_URL = "https://huxley.apphb.com/all/{}?expand=true&accessToken=D102521A-06C6-44C9-8693-7A0394C757EF"

import wifi
import ugfx
import http
import ujson
import app
import sleep
from tilda import Buttons, LED

def init():
    # initialize screen
    ugfx.init()
    ugfx.clear()
    ugfx.orientation(90)
    ugfx.backlight(50)
    
    # ensure wifi connection
    if not wifi.is_connected():
        wifi.connect(show_wait_message=True)
    
    # show initial screen
    ugfx.text(5, 5, "Will monitor station:", ugfx.BLACK)
    ugfx.text(200, 5, STATION_CODE, ugfx.BLUE)
    
def get_trains():
    station_data = None

    LED(LED.RED).on() # Red for total get_trains
    try:
        station_json = http.get(API_URL.format(STATION_CODE)).raise_for_status().content
        LED(LED.GREEN).on() # Green for parsing
        station_data = ujson.loads(station_json)
    except:
        print('Fuck')

    LED(LED.RED).off()
    LED(LED.GREEN).off()
    return station_data

def get_time(station_data):
    return ':'.join(station_data['generatedAt'].split('T')[1].split(':')[0:2])

def is_red(service):
    return service['isCancelled'] or service['etd'] != 'On time'

def get_arrival(service):
    if service['isCancelled']:
        return 'CANX'

    if service['eta'] == 'On time':
        return service['sta']

    return service['eta']

def get_title(name, has_error):
    if has_error:
        return 'ERR ' + name
    
    return name

def show_trains(station_data, has_error):
    ugfx.clear()
    ugfx.area(0, 0, 240, 25,
              ugfx.RED if has_error else ugfx.GRAY)
    title = get_title(station_data['locationName'], has_error)
    ugfx.text(5, 5, title,
              ugfx.WHITE if has_error else ugfx.BLACK)
    ugfx.text(195, 5, get_time(station_data), ugfx.BLUE)
    names = ugfx.Container(0, 25, 190, 295)
    names.show()
    for idx, service in enumerate(station_data['trainServices']):
        names.text(5, 15 * idx, service['destination'][0]['locationName'], ugfx.BLACK)
        ugfx.text(195, 25 + (15 * idx), get_arrival(service), ugfx.RED if is_red(service) else ugfx.BLUE)

def show_error():
    ugfx.clear()
    ugfx.text(5, 5, 'Error :(', ugfx.RED)

init()
station_data = None
has_error = False
while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    new_station_data = get_trains()
    if new_station_data == None:
        has_error = True
    else:
        station_data = new_station_data
        has_error = False
    
    if station_data == None:
        show_error()
    else:
        show_trains(station_data, has_error)
    sleep.sleep_ms(30 * 1000)


# closing
ugfx.clear()
app.restart_to_default()
