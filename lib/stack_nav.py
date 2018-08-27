"""A stack-based naviation system.

Maintains a stack of states through which a user can navigate.
Think Android's back button model.

Every screen is modeled as a function that takes one argument "state".
It can modify state and should either return
* None (which means go back one level)
* A new function (which adds to the stack)
* A keyword like NEXT_EXIT (exit nav) or NEXT_TOP (go to top of stack)

Children get a a shallow clone of the current state, going back will
lead to a screen with the original state.
"""

___dependencies___ = ["dialogs", "database"]
___license___ = "MIT"

import dialogs, database

NEXT_EXIT = "exit" # Leave navigation
NEXT_TOP = "init" # Go to top of stack
def nav(init_fn, init_state={}):
    stack = [(init_fn, init_state)]
    while stack:
        (fn, state) = stack[-1] # peek
        next_state = state.copy()
        result = fn(next_state)
        if callable(result):
            stack.append((result, next_state))
        elif result == NEXT_TOP:
            stack = [(init_fn, init_state)]
        elif result == NEXT_EXIT:
            break
        else:
            stack.pop()

# A simple menu. Format of items is [{"foo":fn}, ...]
def selection(items, title="Settings", none_text="Back"):
    items = [{"title": t, "function": fn} for (t, fn) in items.items()]
    selection = dialogs.prompt_option(items, none_text=none_text, title=title)
    if selection:
        return selection["function"]
    else:
        return None

# A wrapper for a simple string menu
def change_string(title, getter_setter_function):
    def inner(state):
        value = getter_setter_function()
        value = dialogs.prompt_text(title, init_text=value, true_text="Change", false_text="Back")
        if value:
            getter_setter_function(value)
    return inner

# A wrapper for a database key
def change_database_string(title, key, default=""):
    def inner(state):
        value = database.get(key, default)
        value = dialogs.prompt_text(title, init_text=value, true_text="Change", false_text="Back")
        if value:
            database.set(key, value)
    return inner
