import http, ugfx, buttons
from tilda import Buttons
from tildr.shared import clear


def screen(state):
    window = ugfx.Container(0, 0, 240, 320)
    window.show()

    try:
        # logo = http.get("https://i.imgur.com/0TjxEPs.png").raise_for_status().content
        ugfx.display_image(
            int((ugfx.width() - 164)/2),
            20,
            "tildr/biglogo.png")
    except:
        pass

    window.text(160, 100, "TILDR", ugfx.WHITE)
    window.text(0, 270, "Find your match @emfcamp ;)", ugfx.WHITE)
    window.text(45, 300, "Press A to begin", ugfx.WHITE)

    state['ui'].append(window)


def actions(state):
    if buttons.is_triggered(Buttons.BTN_A):
        if state['profile'] is None:
            state['next'] = "PROFILE"
        else:
            state['next'] = "NEXT_PERSON"
