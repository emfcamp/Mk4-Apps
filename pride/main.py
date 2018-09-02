"""Pride flag homescreen

Similar to the default homescreen, but the
background is the pride flag.
"""

___name___         = "Pride"
___license___      = "MIT"
___categories___   = ["Homescreens"]
___dependencies___ = ["homescreen", "app"]
___launchable___   = False
___bootstrapped___ = False


from app import restart_to_default
import ugfx
import homescreen


homescreen.init()
ugfx.clear(ugfx.html_color(0xFF0000))

# Used for placement around text
name_height = 55
info_height = 20

# Maximum length of name before downscaling
max_name = 8

# Orientation for other people to see
ugfx.orientation(90)

# Pride flag colours
colours = [0xE70000, 0xFF8C00, 0xFFEF00, 0x00811F, 0x0044FF, 0x760089]

# Draw each "band" of colour in the flag
colour_width = ugfx.width() / len(colours)
for num, colour in enumerate(colours):
    width_loc = int(num * colour_width)
    ugfx.area(width_loc, 0, int(colour_width), 320, ugfx.html_color(colour))

# Message to display
prefix_message = "Hi I'm"

ugfx.set_default_font(ugfx.FONT_NAME)

# Calc center of screen
center = (int(ugfx.width() / 2), int(ugfx.height() / 2))
# Can't use label since the background covers the flag
ugfx.text(50, center[1] + name_height, prefix_message, ugfx.WHITE)

# Process name
given_name = homescreen.name("Set your name in the settings app")
if len(given_name) <= max_name:
    ugfx.set_default_font(ugfx.FONT_NAME)
else:
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
# Draw name
ugfx.Label(0, ugfx.height() - name_height, ugfx.width(), name_height, given_name, justification=ugfx.Label.CENTER)


# Draw for the user to see
ugfx.orientation(270)
ugfx.set_default_font(ugfx.FONT_SMALL)

# WiFi/Battery update loop
while True:
    ugfx.area(0, ugfx.height() - info_height, ugfx.width(), info_height, ugfx.WHITE)

    wifi_strength_value = homescreen.wifi_strength()
    if wifi_strength_value:
        wifi_message = 'WiFi: %s%%' % int(wifi_strength_value)
        wifi_text = ugfx.text(center[0], ugfx.height() - info_height, wifi_message, ugfx.BLACK)

    battery_value = homescreen.battery()
    if battery_value:
        battery_message = 'Battery: %s%%' % int(battery_value)
        battery_text = ugfx.text(0, ugfx.height() - info_height, battery_message, ugfx.BLACK)

    homescreen.sleep_or_exit(1.5)

restart_to_default()
