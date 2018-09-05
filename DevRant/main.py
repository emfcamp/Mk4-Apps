"""DevRant Client for TiLDA-MK4
"""
___name___         = "DevRant"
___license___      = "MIT"
___dependencies___ = ["app", "wifi", "http", "ugfx_helper"]
___categories___   = ["Other"]
___launchable___   = True

import ugfx, wifi, http, json, utime, ugfx_helper, dialogs, app

char_ln = 25
ln_pg = 19

def loop():
    skip = 0
    while True:
        ugfx.clear(ugfx.html_color(0x544c6d))
        data= json.loads(http.get("https://devrant.com/api/devrant/rants?app=3&sort=top&range=day&limit=1&skip="+str(skip)).raise_for_status().content)["rants"][0]
        
        text=data["text"].split(" ")
        screens = [[]]
        line = ""
        screen = 0
        for word in text:
            if len(line+word)+1 >= char_ln:
                if len(screens[screen]) >= ln_pg:
                    screen+=1
                    screens.append([])
                screens[screen].append(line)
                line=word
            else:
                line = line + " " + word
        if len(screens[screen]) < ln_pg:
            screens[screen].append(line)
        else:
            screens.append([line])


        hold=True
        page = 0
        while hold:
            ugfx.clear(ugfx.html_color(0x544c6d))
            ugfx.area(0,0,240,35,ugfx.html_color(0x41476d))
            ugfx.text(5,5,str(data["score"])+"++ " + data["user_username"] + ":",ugfx.BLACK)
            
            ugfx.text(5,20,"Page: " + str(page+1) + "/" + str(len(screens)),ugfx.BLACK)
            count = 0
            for line in screens[page]:
                ugfx.text(5,35+count*15,line,ugfx.BLACK)
                count+=1
            hold_btn = True
            while hold_btn:
                if tilda.Buttons.is_pressed(tilda.Buttons.BTN_Menu):
                    return
                if tilda.Buttons.is_pressed(tilda.Buttons.BTN_A):
                    skip += 1
                    hold_btn = False
                    hold = False
                    while tilda.Buttons.is_pressed(tilda.Buttons.BTN_A):
                        utime.sleep_ms(10)
                if tilda.Buttons.is_pressed(tilda.Buttons.JOY_Right):
                    if page <  len(screens)-1:
                        page += 1
                    hold_btn = False
                    while tilda.Buttons.is_pressed(tilda.Buttons.JOY_Right):
                        utime.sleep_ms(10)
                if tilda.Buttons.is_pressed(tilda.Buttons.JOY_Left):
                    if page >  0:
                        page -= 1
                    hold_btn = False
                    while tilda.Buttons.is_pressed(tilda.Buttons.JOY_Left):
                        utime.sleep_ms(10)
                

ugfx_helper.init()
ugfx.clear()
ugfx.text(5,5, "DevRant for the TiLDA Mk4", ugfx.BLACK)
ugfx.text(5, 40, "Connecting To WIFI", ugfx.BLACK)
wifi.connect()
ugfx.text(5, 40, "Connecting To WIFI", ugfx.WHITE)
loop()
app.restart_to_default()
