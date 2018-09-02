import ugfx, buttons
from tilda import Buttons
from tildr.shared import top_left_logo

def screen(state):
    window = ugfx.Container(0, 0, 240, 320)
    window.show()

    top_left_logo()

    ugfx.set_default_font(ugfx.FONT_TITLE)
    l1 = ugfx.Label(5, 90, 230, 50, "You've swiped everybody!", parent=window, justification=ugfx.Label.CENTERTOP)
    ugfx.set_default_font(ugfx.FONT_SMALL)
    l2 = ugfx.Label(5, 160, 230, 20, "Soz "+state["profile"]["username"], parent=window, justification=ugfx.Label.CENTERTOP)
    l3 = ugfx.Label(5, 180, 230, 20, "Come back later ;)", parent=window, justification=ugfx.Label.CENTERTOP)

    b2 = ugfx.Button(0, 280, 120, 40, "< Edit profile", parent=window, shape=ugfx.Button.RECT, style=None)
    b1 = ugfx.Button(120, 280, 120, 40, "Try again >", parent=window, shape=ugfx.Button.RECT, style=None)

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
