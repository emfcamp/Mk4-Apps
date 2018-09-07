"""Pride flag homescreen

Similar to the default homescreen, but the
background is the pride flag.
"""

___title___        = "Pride"
___license___      = "MIT"
___categories___   = ["Homescreens"]
___dependencies___ = ["homescreen", "app", "buttons"]


from app import restart_to_default
import ugfx
import homescreen
from tilda import Buttons
import buttons


homescreen.init()
ugfx.clear(ugfx.html_color(0xFF0000))

# Used for placement around text
name_height = 55
info_height = 20

# Maximum length of name before downscaling
max_name = 8

flags = {
    'LGBT': [0xE70000, 0xFF8C00, 0xFFEF00, 0x00811F, 0x0044FF, 0x760089],
    'Non-Binary': [0xFFF433, 0xFFFFFF, 0x9B59D0, 0x000000],
    'Trans': [0x5BCEFA, 0xF5A9B8, 0xFFFFFF, 0xF5A9B8, 0x5BCEFA],
    'Asexual': [0x000000, 0xA3A3A3, 0xFFFFFF, 0x800080],
    'Bisexual': [0xFF0080, 0xFF0080, 0xA349A4, 0x0000FF, 0x0000FF],
    'Pansexual': [0xFF218E, 0xFCD800, 0x0194FC]
}


def draw_flag(colours):
    # Orientation for other people to see
    ugfx.orientation(90)

    # Draw each "band" of colour in the flag
    colour_width = ugfx.width() / len(colours)
    for num, colour in enumerate(colours):
        width_loc = int(num * colour_width)
        flag_height = ugfx.height() - (name_height + info_height)
        ugfx.area(width_loc, info_height, int(colour_width), flag_height, ugfx.html_color(colour))


def draw_name():
    # Orientation for other people to see
    ugfx.orientation(90)

    ugfx.set_default_font(ugfx.FONT_NAME)

    # Process name
    given_name = homescreen.name("Set your name in the settings app")
    if len(given_name) <= max_name:
        ugfx.set_default_font(ugfx.FONT_NAME)
    else:
        ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
    # Draw name
    ugfx.Label(0, ugfx.height() - name_height, ugfx.width(), name_height, given_name, justification=ugfx.Label.CENTER)


def draw_user_info():
    # Draw for the user to see
    ugfx.orientation(270)
    # Calc width center of screen
    center_width = int(ugfx.width() / 2)
    ugfx.set_default_font(ugfx.FONT_SMALL)

    ugfx.area(0, ugfx.height() - info_height, ugfx.width(), info_height, ugfx.WHITE)

    wifi_strength_value = homescreen.wifi_strength()
    if wifi_strength_value:
        wifi_message = 'WiFi: %s%%' % int(wifi_strength_value)
        ugfx.text(center_width, ugfx.height() - info_height, wifi_message, ugfx.BLACK)

    battery_value = homescreen.battery()
    if battery_value:
        battery_message = 'Battery: %s%%' % int(battery_value)
        ugfx.text(0, ugfx.height() - info_height, battery_message, ugfx.BLACK)


# Set variables for WiFi/Battery loop
selection_change = True
flag_names = list(flags.keys())
selection = flag_names.index('LGBT')

# WiFi/Battery update loop
draw_name()
while True:
    # Buttons will cycle when it reaches either side of the list
    if buttons.is_pressed(Buttons.JOY_Left):
        if selection > 0:
            selection -= 1
        else:
            selection = len(flags) - 1
        selection_change = True

    elif buttons.is_pressed(Buttons.JOY_Right):
        if selection < len(flags) - 1:
            selection += 1
        else:
            selection = 0
        selection_change = True

    # Only triggers if the selection has changed
    if selection_change:
        draw_flag(flags[flag_names[selection]])
        selection_change = False

    # Redraw time-sensitive info on each iteration
    draw_user_info()
    homescreen.sleep_or_exit(1.5)

restart_to_default()
