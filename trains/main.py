"""Mini train departure board for your badge

Configurable with which station you want to monitor
"""
___title___ = "trains"
___license___ = "MIT"
___dependencies___ = ["app", "sleep", "wifi", "http", "ugfx_helper"]
___categories___ = ["Homescreens", "Other"]
___bootstrapped___ = False


import database
import wifi
import ugfx
import app
import sleep
import ntp
from tilda import Buttons, LED
from trains import api
from trains import screen
from trains.departure_screen import DepartureScreen
from trains.settings_screen import SettingsScreen

def init_screen(orientation):
    # initialize screen
    ugfx.clear()
    ugfx.orientation(orientation)
    ugfx.backlight(50)
    # show initial screen
    # photo credit: https://www.flickr.com/photos/remedy451/8061918891
    ugfx.display_image(0, 0, 'trains/splash.gif', 90)


def init():
    print('trains/main: Init')
    ugfx.init()
    ntp.set_NTP_time()
    # ensure wifi connection
    if not wifi.is_connected():
        wifi.connect(show_wait_message=True)


def exit():
    print('trains/main: Exit')
    ugfx.clear()
    app.restart_to_default()


app_screens = {
    screen.SETTINGS: SettingsScreen(),
    screen.DEPARTURES: DepartureScreen()
}


def get_initial_screen():
    station_code = database.get('trains.station_code', None)
    if station_code == None:
        return app_screens[screen.SETTINGS]
    return app_screens[screen.DEPARTURES]


def run_screen(instance):
    print('trains/main: Starting screen {}'.format(instance))
    instance.enter()

    is_running = True
    next_screen_name = None
    while is_running:
        status, value = instance.tick()

        if status == screen.SWITCH_SCREEN:
            is_running = False
            next_screen_name = value
        elif status == screen.EXIT_APP:
            is_running = False
    
    print('trains/main: Stopping screen {} (next = {})'.format(instance, next_screen_name))
    instance.exit()
    return next_screen_name

init()
current_screen = get_initial_screen()
is_app_running = True
while is_app_running:
    init_screen(current_screen.orientation())
    next_screen_name = run_screen(current_screen)

    if next_screen_name != None:
        current_screen = app_screens[next_screen_name]
    else:
        is_app_running = False
        exit()
