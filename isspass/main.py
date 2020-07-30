"""App that estimates time until the ISS next passes over head.
Currently hardcoded lat/lon to Eastnor Deer Park.

Influenced by EMF Beer. As all things should be.
"""
___title___        = "ISS Pass"
___license___      = "MIT"
___dependencies___ = ["app", "sleep", "wifi", "http", "ugfx_helper"]
___categories___   = ["Other"]

import wifi, ugfx, http, ujson, app, sleep, utime
from tilda import Buttons, LED

orientation = 270
countdown = 0

def get_data():
    
    try:
        api_url = "http://api.open-notify.org/iss-pass.json?lat=54.251790&lon=-7.169730"
        iss_json = http.get(api_url).raise_for_status().content
        iss = ujson.loads(iss_json)
        if iss['message'] == "success":
            LED(LED.GREEN).on()
        elif iss['message'] == "failure":
            LED(LED.RED).on()
            ugfx.clear(ugfx.BLACK)
            ugfx.text(5, 5, str(iss['reason']), ugfx.RED)
            return
        else:
            LED(LED.RED).on()
    except: 
        print('Something has gone wrong')

    return iss

def get_time(timestamp):
    convtime = utime.localtime(timestamp)
    year = convtime[0]
    # have to subtract 30yrs as different epochs between open-notify and utime
    year = year - 30
    month = convtime[1]
    day = convtime[2]
    hour = convtime[3]
    minute = convtime[4]
    second = convtime[5]
    time_str = "%02i:%02i:%02i %i/%i/%4i UTC" % (hour, minute, second, day, month, year)
    return time_str

def get_seconds(secs):
    day = secs // (24 * 3600)
    time = secs % (24 * 3600)
    hour = secs // 3600
    secs %= 3600
    minutes = secs // 60
    secs %= 60
    seconds = secs
    seconds_str = "%dh %dm %ds" % (hour, minutes, seconds)
    return seconds_str

def get_wait(time1, time2):
    duration = time1 - time2
    wait = get_seconds(duration)
    return wait

def draw_screen():
    iss_data = get_data()
    risetime = iss_data['response'][0]['risetime']
    datetime = iss_data['request']['datetime']
    countdown = datetime
    LED(LED.GREEN).off()
    while countdown < risetime:
        ugfx.clear(ugfx.BLACK)
        ugfx.text(5, 5, "When does the ISS next pass?", ugfx.WHITE)
        ugfx.line(5, 20, ugfx.width(), 20, ugfx.GREY)
        ugfx.text(5, 35, "Rise time: " + str(get_time(risetime)), ugfx.WHITE)
        ugfx.text(5, 50, "Duration: " + str(get_seconds(iss_data['response'][0]['duration'])), ugfx.WHITE)
        countdown +=1
        ugfx.text(5, 65, "Countdown: " + str(get_wait(risetime, countdown)), ugfx.WHITE)
        utime.sleep(1)
    else:
        LED(LED.GREEN).on()
        LED(LED.RED).on()
        utime.sleep(1)
        LED(LED.GREEN).off()
        LED(LED.RED).off()
        draw_screen()

def toggle_orientation():

    global orientation
    if orientation == 90:
        ugfx.orientation(270)
        orientation = 270
        draw_screen()
    else:
        ugfx.orientation(90)
        orientation = 90
        draw_screen()

ugfx.init()
ugfx.clear(ugfx.BLACK)
ugfx.set_default_font(ugfx.FONT_FIXED)

s=ugfx.Style()
s.set_enabled([ugfx.WHITE, ugfx.BLACK, ugfx.BLACK, ugfx.GREY])
s.set_background(ugfx.BLACK)
ugfx.set_default_style(s)

#Buttons.enable_interrupt(Buttons.BTN_A, lambda button_id:draw_screen(), on_press=True, on_release=False)
#Buttons.enable_interrupt(Buttons.BTN_B, lambda button_id:toggle_orientation(), on_press=True, on_release=False)
Buttons.enable_interrupt(Buttons.BTN_Menu, lambda button_id:app.restart_to_default(), on_press=True, on_release=False)

ugfx.text(5, 10, "Estimating position...", ugfx.WHITE)
ugfx.text(5, 30, "Press Menu to exit", ugfx.WHITE)
ugfx.text(5, 45, "Countdown clock can drift.", ugfx.WHITE)

draw_screen()

while True:
    sleep.wfi()

ugfx.clear()
app.restart_to_default()
