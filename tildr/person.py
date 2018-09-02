import http, ugfx, buttons
from tilda import Buttons
from tildr.shared import top_left_logo


def get_next_person(state):
    try:
        resp = http.get(state['api']+'/get_user/'+state['profile']['unique_identifier']).json()
    except:
        return None

    if not resp['success']:
        return None

    return resp['value']


def screen(state):
    loading = ugfx.Container(0, 0, 240, 320)
    loading.text(5, 100, "Loading...", ugfx.WHITE)
    state['ui'].append(loading)

    loading.show()
    person = get_next_person(state)
    loading.hide()

    if person is None:
        state['next'] = "NO_MORE"
        return

    window = ugfx.Container(0, 0, 240, 320)
    window.show()

    top_left_logo()

    ugfx.set_default_font(ugfx.FONT_TITLE)
    l1 = ugfx.Label(5, 90, 230, 40, person["username"], parent=window, justification=ugfx.Label.LEFTTOP)
    ugfx.set_default_font(ugfx.FONT_SMALL)
    window.text(200, 92, person["age"], ugfx.WHITE)

    l2 = ugfx.Label(5, 120, 230, 60, person["tag_line"], parent=window)

    l3 = ugfx.Label(5, 200, 230, 40, person["looking_for"], parent=window)
    window.text(5, 180, "Looking for...", ugfx.RED)

    if not person["contact"].startswith("@"):
        person["contact"] = "@" + person["contact"]

    window.text(5, 245, person["contact"], ugfx.BLUE)

    b2 = ugfx.Button(0, 280, 120, 40, "< Edit profile", parent=window, shape=ugfx.Button.RECT, style=None)
    b1 = ugfx.Button(120, 280, 120, 40, "Swipe >", parent=window, shape=ugfx.Button.RECT, style=None)

    state['ui'].append(window)
    state['ui'].append(l1)
    state['ui'].append(l2)
    state['ui'].append(l3)
    state['ui'].append(b1)
    state['ui'].append(b2)


def actions(state):
    if buttons.is_triggered(Buttons.BTN_B) or buttons.is_triggered(Buttons.JOY_Right):
        state['next'] = "NEXT_PERSON"
    if buttons.is_triggered(Buttons.BTN_A) or buttons.is_triggered(Buttons.JOY_Left):
        state['next'] = "PROFILE"
