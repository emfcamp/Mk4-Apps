""" Tildr Dating
"""
___name___         = "Tildr Dating"
___license___      = "MIT"
___dependencies___ = ["wifi", "http", "ugfx_helper", "sleep", "dialogs", "sim800", "database"]
___categories___   = ["Other"]
___bootstrapped___ = True

import app, buttons, ugfx, ugfx_helper, sleep, http, dialogs, sim800, database, ujson
from tilda import Buttons

from tildr.profile import get_profile
from tildr.shared import clear
from tildr import splash, profile, person, nomore

api_url = "http://emf2018.us-east-2.elasticbeanstalk.com"

ugfx_helper.init()
ugfx.clear(ugfx.html_color(0x000000))

style = ugfx.Style()
style.set_enabled([ugfx.WHITE, ugfx.WHITE, ugfx.html_color(0x888888), ugfx.html_color(0x444444)])
style.set_background(ugfx.html_color(0x000000))
ugfx.set_default_style(style)

def error_screen(state):
    ugfx.text(5, 100, "Error: try again later :(", ugfx.WHITE)

def error_actions(state):
    if buttons.is_triggered(Buttons.BTN_A):
        state['next'] = "SPLASH"

screens = {
    'SPLASH': {'render': splash.screen, 'actions': splash.actions},
    'PROFILE': {'render': profile.screen, 'actions': profile.actions},
    'ERROR': {'render': error_screen, 'actions': error_actions},
    'NEXT_PERSON': {'render': person.screen, 'actions': person.actions},
    'NO_MORE': {'render': nomore.screen, 'actions': nomore.actions}
}

state = {
    'api': api_url,
    'running': True,
    'screen': None,
    'next': "SPLASH",
    'ui': [],
    'profile': None
}


def destroy(state):
    for item in state['ui']:
        try:
            item.hide()
        except:
            pass
        item.destroy()

    state['ui'] = []


state['profile'] = get_profile()

while state['running']:

    # Move to next screen
    if state['next']:
        destroy(state)
        nxt = state['next']
        state['screen'] = nxt
        state['next'] = None

        clear()
        screens[nxt]['render'](state)

    sleep.wfi()

    s = state['screen']
    screens[s]['actions'](state)

    if buttons.is_triggered(Buttons.BTN_Menu):
        state['running'] = False


app.restart_to_default()
