"""A Sequencer!

Annoy your friends! Annoy your enemies! Annoy yourself! Maybe (maybe) make music!
"""

___name___         = "Sequencer"
___license___      = "MIT"
___categories___   = ["Sound"]
___dependencies___ = ["speaker", "buttons", "ugfx_helper", "app", "shared/sequencer_info.png"]

import ugfx, speaker, ugfx_helper
from tilda import Buttons
from buttons import *
from app import restart_to_default

ugfx_helper.init()
speaker.enabled(True)

rows_per_block = 4
cols_per_block = 3
num_v_blocks = 2
num_h_blocks = 4
total_rows = rows_per_block*num_v_blocks
total_cols = cols_per_block*num_h_blocks
line_width = 5
row_height = int(ugfx.height() / (rows_per_block*num_v_blocks))
col_width = int(ugfx.width() / (cols_per_block*num_h_blocks))
block_height = row_height*rows_per_block
block_width = col_width*cols_per_block

active = True

notes = [
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B"]

active_colour = ugfx.html_color(0x800080)
inactive_colour = ugfx.html_color(0xd29cd1)
current_active_colour = ugfx.html_color(0x00cf3a)
current_inactive_colour = ugfx.html_color(0x88c89a)

start_time = time.ticks_ms()
time_per_row = 500 # mS
previous_current_row = 0 # TODO: find less stupid variable name

debounce_time = 100
active_states = [[False for col in range(total_cols)] for row in range(total_rows)]
last_pressed = [[time.ticks_ms() for col in range(total_cols)] for row in range(total_rows)]
joy_last_pressed = [time.ticks_ms() for col in range(6)]

active_v_block = 0
active_h_block = 0

def mode_buttons():
    global previous_current_row
    global active_states
    global active
    global start_time
    global active_v_block
    global active_h_block

    print("mode: buttons")
    coords = {
        Buttons.BTN_1: (0,0),
        Buttons.BTN_2: (0,1),
        Buttons.BTN_3: (0,2),
        Buttons.BTN_4: (1,0),
        Buttons.BTN_5: (1,1),
        Buttons.BTN_6: (1,2),
        Buttons.BTN_7: (2,0),
        Buttons.BTN_8: (2,1),
        Buttons.BTN_9: (2,2),
        Buttons.BTN_Star: (3,0),
        Buttons.BTN_0: (3,1),
        Buttons.BTN_Hash: (3,2),
    }
    render_ui()

    alive = True
    while alive:
        ui_changed = False
        row_changed = False

        current_row = int((time.ticks_ms() - start_time) / time_per_row) % total_rows
        if current_row != previous_current_row:
            previous_current_row = current_row
            row_changed = True

        for btn, coord in coords.items():
            if is_pressed(btn):
                row = active_v_block*rows_per_block + coord[0]
                col = active_h_block*cols_per_block + coord[1]
                if (last_pressed[row][col] + debounce_time < time.ticks_ms()):
                    last_pressed[row][col] = time.ticks_ms()
                    active_states[row][col] = not active_states[row][col]

                    # only one note per frame
                    if active_states[row][col]:
                        for check_col in range(total_cols):
                            if check_col != col:
                                active_states[row][check_col] = False

                    ui_changed = True
                    break

        if is_triggered(Buttons.JOY_Center):
            if (joy_last_pressed[5] + debounce_time < time.ticks_ms()):
                joy_last_pressed[5] = time.ticks_ms()
                active = not active
                if not active:
                    speaker.stop()
                else:
                    start_time = time.ticks_ms()
                ui_changed = True
        if is_triggered(Buttons.JOY_Up):
            if (joy_last_pressed[0] + debounce_time < time.ticks_ms()):
                joy_last_pressed[0] = time.ticks_ms()
                active_v_block -= 1
                if active_v_block < 0:
                    active_v_block += num_v_blocks
                ui_changed = True
        if is_triggered(Buttons.JOY_Down):
            if (joy_last_pressed[1] + debounce_time < time.ticks_ms()):
                joy_last_pressed[1] = time.ticks_ms()
                active_v_block += 1
                active_v_block %= num_v_blocks
                ui_changed = True
        if is_triggered(Buttons.JOY_Left):
            if (joy_last_pressed[2] + debounce_time < time.ticks_ms()):
                joy_last_pressed[2] = time.ticks_ms()
                active_h_block -= 1
                if active_h_block < 0:
                    active_h_block += num_h_blocks
                ui_changed = True
        if is_triggered(Buttons.JOY_Right):
            if (joy_last_pressed[3] + debounce_time < time.ticks_ms()):
                joy_last_pressed[3] = time.ticks_ms()
                active_h_block += 1
                active_h_block %= num_h_blocks
                ui_changed = True
        if is_triggered(Buttons.BTN_B):
            if (joy_last_pressed[4] + debounce_time < time.ticks_ms()):
                joy_last_pressed[4] = time.ticks_ms()
                for row in range(total_rows):
                    for col in range(total_cols):
                        active_states[row][col] = False
                ui_changed = True
        if is_triggered(Buttons.BTN_A):
            if (joy_last_pressed[5] + debounce_time < time.ticks_ms()):
                joy_last_pressed[5] = time.ticks_ms()
                speaker.stop()
                display_help()
                ui_changed = True
        if is_triggered(Buttons.BTN_Menu):
            break

        if ui_changed or (active and row_changed):
            render_ui()
        if active and row_changed:
            play_notes(current_row)

def render_ui():
    ugfx.clear(ugfx.html_color(0xffffff))
    # draw squares
    current_row = int((time.ticks_ms() - start_time) / time_per_row) % total_rows

    for row in range(total_rows):
        for col in range(total_cols):
            colour = inactive_colour
            if active and row == current_row:
                if active_states[row][col] == True:
                    colour = current_active_colour
                else:
                    colour = current_inactive_colour
            elif active_states[row][col] == True:
                colour = active_colour

            ugfx.area(col_width*col + line_width, row_height*row + line_width, col_width - line_width, row_height - line_width, colour)

    # highlight working area
    ugfx.area(active_h_block*block_width, active_v_block*block_height, line_width, block_height, ugfx.RED)
    ugfx.area((active_h_block+1)*block_width, active_v_block*block_height, line_width, block_height, ugfx.RED)
    ugfx.area(active_h_block*block_width, active_v_block*block_height, block_width, line_width, ugfx.RED)
    ugfx.area(active_h_block*block_width, (active_v_block+1)*block_height, block_width+line_width, line_width, ugfx.RED)

def play_notes(row):
    note = ""
    for col in range(total_cols):
        if active_states[row][col] == True:
            note = notes[col]

    if note == "":
        speaker.stop()
    else:
        speaker.stop()
        speaker.note("{}{}".format(note, 5))

def display_help():
    global start_time
    ugfx.display_image(0, 0, "shared/sequencer_info.png")
    wait_until = time.ticks_ms() + 5000
    while time.ticks_ms() < wait_until:
        time.sleep(0.1)
        if Buttons.is_pressed(Buttons.BTN_A) or Buttons.is_pressed(Buttons.BTN_B) or Buttons.is_pressed(Buttons.BTN_Menu):
            break

    start_time = time.ticks_ms()

display_help()
mode_buttons() # Todo: Allow different modes and allow users to switch between them via joystick or something
restart_to_default()
