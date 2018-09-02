"""Some basic UGFX powered dialogs"""

___license___ = "MIT"
___dependencies___ = ["buttons", "sleep"]

import ugfx, buttons, sleep
from buttons import Buttons
import time

default_style_badge = ugfx.Style()
default_style_badge.set_focus(ugfx.RED)
default_style_badge.set_enabled([ugfx.WHITE, ugfx.html_color(0x3C0246), ugfx.GREY, ugfx.RED])
default_style_badge.set_background(ugfx.html_color(0x3C0246))

default_style_dialog = ugfx.Style()
default_style_dialog.set_enabled([ugfx.BLACK, ugfx.html_color(0xA66FB0), ugfx.html_color(0xdedede), ugfx.RED])
default_style_dialog.set_background(ugfx.html_color(0xFFFFFF))


TILDA_COLOR = ugfx.html_color(0x7c1143);
FONT_SMALL = 0 #todo: find correct values
FONT_MEDIUM_BOLD = 0

def notice(text, title="TiLDA", close_text="Close", font=FONT_SMALL, style=None):
    prompt_boolean(text, title = title, true_text = close_text, false_text = None, font=font, style=style)

def prompt_boolean(text, title="TiLDA", true_text="Yes", false_text="No", font=FONT_SMALL, style=None):
    """A simple one and two-options dialog

    if 'false_text' is set to None only one button is displayed.
    If both 'true_text' and 'false_text' are given a boolean is returned
    """
    global default_style_dialog
    if style == None:
        style = default_style_dialog
    ugfx.set_default_font(FONT_MEDIUM_BOLD)

    width = ugfx.width() - 10
    height = ugfx.height() - 10

    window = ugfx.Container(5, 5,  width, height)
    window.show()
    ugfx.set_default_font(font)
    window.text(5, 10, title, TILDA_COLOR)
    window.line(0, 30, width, 30, ugfx.BLACK)

    if false_text:
        true_text = "A: " + true_text
        false_text = "B: " + false_text

    ugfx.set_default_font(font)
    label = ugfx.Label(5, 30, width - 10, height - 80, text = text, parent=window)
    ugfx.set_default_font(FONT_MEDIUM_BOLD)
    button_yes = ugfx.Button(5, height - 40, width // 2 - 15 if false_text else width - 15, 30 , true_text, parent=window)
    button_no = ugfx.Button(width // 2 + 5, height - 40, width // 2 - 15, 30 , false_text, parent=window) if false_text else None

    try:
        #button_yes.attach_input(ugfx.BTN_A,0) # todo: re-enable once working
        #if button_no: button_no.attach_input(ugfx.BTN_B,0)

        window.show()

        while True:
            sleep.wfi()
            if buttons.is_triggered(buttons.Buttons.BTN_A): return True
            if buttons.is_triggered(buttons.Buttons.BTN_B): return False

    finally:
        window.hide()
        window.destroy()
        button_yes.destroy()
        if button_no: button_no.destroy()
        label.destroy()

def prompt_text(description, init_text="", true_text="OK", false_text="Back", font=FONT_MEDIUM_BOLD, style=default_style_badge, numeric=False):
    """Shows a dialog and keyboard that allows the user to input/change a string

    Returns None if user aborts with button B
    """

    window = ugfx.Container(0, 0, ugfx.width(), ugfx.height())

    if false_text:
        true_text = "A: " + true_text
        false_text = "B: " + false_text

    ugfx.set_default_font(FONT_MEDIUM_BOLD)
    kb = ugfx.Keyboard(0, ugfx.height()//2, ugfx.width(), ugfx.height()//2, parent=window)
    edit = ugfx.Textbox(2, ugfx.height()//2-60, ugfx.width()-7, 25, text = init_text, parent=window)
    ugfx.set_default_font(FONT_SMALL)
    button_yes = ugfx.Button(2, ugfx.height()//2-30, ugfx.width()//2-6, 25 , true_text, parent=window)
    button_no = ugfx.Button(ugfx.width()//2+2, ugfx.height()//2-30, ugfx.width()//2-6, 25 , false_text, parent=window) if false_text else None
    ugfx.set_default_font(font)
    label = ugfx.Label(ugfx.width()//10, ugfx.height()//10, ugfx.width()*4//5, ugfx.height()*2//5-90, description, parent=window)

    try:
        window.show()
        # edit.set_focus() todo: do we need this?
        while True:
            sleep.wfi()
            ugfx.poll()
            if buttons.is_triggered(buttons.Buttons.BTN_A): return edit.text()
            if buttons.is_triggered(buttons.Buttons.BTN_B): return None
            if buttons.is_triggered(buttons.Buttons.BTN_Menu): return edit.text()
            handle_keypad(edit, numeric)

    finally:
        window.hide()
        window.destroy()
        button_yes.destroy()
        if button_no: button_no.destroy()
        label.destroy()
        kb.destroy()
        edit.destroy();
    return

last_key = None
last_keytime = None
def handle_keypad(edit, numeric):
    global last_key, last_keytime
    threshold = 1000
    keymap = {
        buttons.Buttons.BTN_0: [" ", "0"],
        buttons.Buttons.BTN_1: ["1"],
        buttons.Buttons.BTN_2: ["a", "b", "c", "2"],
        buttons.Buttons.BTN_3: ["d", "e", "f", "3"],
        buttons.Buttons.BTN_4: ["g", "h", "i", "4"],
        buttons.Buttons.BTN_5: ["j", "k", "l", "5"],
        buttons.Buttons.BTN_6: ["m", "n", "o", "6"],
        buttons.Buttons.BTN_7: ["p", "q", "r", "s", "7"],
        buttons.Buttons.BTN_8: ["t", "u", "v", "8"],
        buttons.Buttons.BTN_9: ["w", "x", "y", "9"],
        buttons.Buttons.BTN_Hash: ["#"],
        buttons.Buttons.BTN_Star: ["*", "+"],
    }

    for key, chars in keymap.items():
        if buttons.is_triggered(key):
            if numeric:
                edit.text(edit.text() + chars[-1])
            elif key != last_key:
                edit.text(edit.text() + chars[0])
            else:
                if last_keytime is None or (time.ticks_ms() - last_keytime) > threshold:
                    edit.text(edit.text() + chars[0])
                else:
                    last_char = edit.text()[-1]
                    try:
                        last_index = chars.index(last_char)
                    except ValueError:
                        # not sure how we get here...
                        return
                    next_index = (last_index+1) % len(chars)
                    edit.text(edit.text()[:-1] + chars[next_index])
            last_key = key
            last_keytime = time.ticks_ms()



def prompt_option(options, index=0, text = None, title=None, select_text="OK", none_text=None):
    """Shows a dialog prompting for one of multiple options

    If none_text is specified the user can use the B or Menu button to skip the selection
    if title is specified a blue title will be displayed about the text
    """
    ugfx.set_default_font(FONT_SMALL)
    window = ugfx.Container(5, 5, ugfx.width() - 10, ugfx.height() - 10)
    window.show()

    list_y = 30
    if title:
        window.text(5, 10, title, TILDA_COLOR)
        window.line(0, 25, ugfx.width() - 10, 25, ugfx.BLACK)
        list_y = 30
        if text:
            list_y += 20
            window.text(5, 30, text, ugfx.BLACK)

    else:
        window.text(5, 10, text, ugfx.BLACK)

    options_list = ugfx.List(5, list_y, ugfx.width() - 25, 260 - list_y, parent = window)
    options_list.disable_draw()

    for option in options:
        if isinstance(option, dict) and option["title"]:
            options_list.add_item(option["title"])
        else:
            options_list.add_item(str(option))
    options_list.enable_draw()
    options_list.selected_index(index)

    select_text = "A: " + select_text
    if none_text:
        none_text = "B: " + none_text

    button_select = ugfx.Button(5, ugfx.height() - 50, 105 if none_text else 200, 30 , select_text, parent=window)
    button_none = ugfx.Button(117, ugfx.height() - 50, 105, 30 , none_text, parent=window) if none_text else None

    try:
        while True:
            sleep.wfi()
            ugfx.poll()
            # todo: temporary hack
            #if (buttons.is_triggered(buttons.Buttons.JOY_Up)):
            #    index = max(index - 1, 0)
            #    options_list.selected_index(index)
            #if (buttons.is_triggered(buttons.Buttons.JOY_Down)):
            #    index = min(index + 1, len(options) - 1)
            #    options_list.selected_index(index)

            if buttons.is_triggered(buttons.Buttons.BTN_A) or buttons.is_triggered(buttons.Buttons.JOY_Center):
                return options[options_list.selected_index()]
            if button_none and buttons.is_triggered(buttons.Buttons.BTN_B): return None
            if button_none and buttons.is_triggered(buttons.Buttons.BTN_Menu): return None
            # These are indexes for selected_index, 1 means "First item", ie index 0. 0 is treated as if it were 10
            button_nums = {
                Buttons.BTN_1: 0,
                Buttons.BTN_2: 1,
                Buttons.BTN_3: 2,
                Buttons.BTN_4: 3,
                Buttons.BTN_5: 4,
                Buttons.BTN_6: 5,
                Buttons.BTN_7: 6,
                Buttons.BTN_8: 7,
                Buttons.BTN_9: 8,
                Buttons.BTN_0: 9,
            }
            for key, num in button_nums.items():
                if buttons.is_triggered(key):
                    # No need to check for too large an index; gwinListSetSelected validates this.
                    options_list.selected_index(num)
                    break
            if buttons.is_triggered(Buttons.BTN_Hash):
                # Page down
                idx = options_list.selected_index() + 10
                cnt = options_list.count()
                if idx >= cnt:
                    idx = cnt - 1
                options_list.selected_index(idx)
                continue
            if buttons.is_triggered(Buttons.BTN_Star):
                # Page up
                idx = options_list.selected_index() - 10
                if idx < 0:
                    idx = 0
                options_list.selected_index(idx)
                continue

    finally:
        window.hide()
        window.destroy()
        options_list.destroy()
        button_select.destroy()
        if button_none: button_none.destroy()
        ugfx.poll()

class WaitingMessage:
    """Shows a dialog with a certain message that can not be dismissed by the user"""
    def __init__(self, text="Please Wait...", title="TiLDA"):
        self.window = ugfx.Container(30, 30, ugfx.width() - 60, ugfx.height() - 60)
        self.window.show()
        self.window.text(5, 10, title, TILDA_COLOR)
        self.window.line(0, 30, ugfx.width() - 60, 30, ugfx.BLACK)
        self.label = ugfx.Label(5, 40, self.window.width() - 10, ugfx.height() - 40, text = text, parent=self.window)

        # Indicator to show something is going on
        #self.indicator = ugfx.Label(ugfx.width() - 100, 0, 20, 20, text = "...", parent=self.window)
        #self.timer = machine.Timer(3)
        #self.timer.init(freq=3)
        #self.timer.callback(lambda t: self.indicator.visible(not self.indicator.visible()))
        # todo: enable this once we have a timer somewhere

    def destroy(self):
        #self.timer.deinit()
        self.label.destroy()
        #self.indicator.destroy()
        self.window.destroy()

    @property
    def text(self):
        return self.label.text()

    @text.setter
    def text(self, value):
        self.label.text(value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.destroy()

