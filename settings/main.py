"""Settings app for common or shared settings

Currently supports
* Setting name
* Setting wifi
* Pick default app
* Change badgestore repo/branch

"""

___name___         = "Settings"
___license___      = "MIT"
___dependencies___ = ["dialogs", "ugfx_helper", "database"]
___categories___   = ["System"]
___bootstrapped___ = True

import ugfx_helper, os, wifi, app, database

### VIEWS ###

ugfx_helper.init()

title = "Settings"

def clear():
    ugfx.clear(ugfx.html_color(ugfx.WHITE))

def settings_name(state):
    pass

def settings_startup_app(state):
    pass

def settings_wifi(state):
    pass

def settings_badge_store(state):
    pass

def settings_main(state):
    menu_items = [
        {"title": "Change Name", "function": settings_name},
        {"title": "Wifi", "function": settings_wifi},
        {"title": "Set startup app", "function": settings_startup_app},
        {"title": "Change Badge Store", "function": settings_badge_store}
    ]

    return prompt_option(menu_items, none_text="Exit", text="What do you want to do?", title=title)

# Todo: this might be useful in a lib

# A stack-based naviation system.
NEXT_EXIT = "exit" # Leave navigation
NEXT_INIT = "init" # Go to top of stack
def nav(init_fn, init_state={}):
    stack = [(init_fn, init_state)]

    while len(stack):
        (fn, state) = stack[-1] # peek
        next_state = state.clone()
        print(next_state)
        result = fn(next_state)
        if callable(result):
            stack.append((result, next_state))
        elif result == NEXT_INIT:
            stack = [(init_fn, init_state)]
        elif result == NEXT_EXIT:
            break
        else:
            stack.pop()

    print("bye")

# Entry point
nav(settings_main)
#show_app("launcher")
