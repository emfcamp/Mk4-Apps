
def render_splash_screen():
    ugfx.clear(ugfx.html_color(0x000000))
    try:
        logo = http.get("https://i.imgur.com/0TjxEPs.png").raise_for_status().content
        ugfx.display_image(
            int((ugfx.width() - 164)/2),
            20,
            bytearray(logo))
    except:
        pass

    ugfx.text(160, 100, "TILDR", ugfx.WHITE)
    ugfx.text(0, 270, "Find your match @emfcamp ;)", ugfx.WHITE)
    ugfx.text(45, 300, "Press A to begin", ugfx.WHITE)


def run_splash_screen():
    while True:
        if buttons.is_triggered(Buttons.BTN_Menu):
            return False
        if buttons.is_triggered(Buttons.BTN_A):
            return True

def create_profile(my_profile):
    ugfx.clear(ugfx.html_color(0x000000))

    name, age = "", ""
    while name == "":
        name = dialogs.prompt_text("What's your name?")
    while age == "":
        age = dialogs.prompt_text("What's your age?")
    tag_line = dialogs.prompt_text("Tell us your tagline:")
    looking_for = dialogs.prompt_text("And what you're looking for:")
    contact = dialogs.prompt_text("And your twitter username?")
    imei = sim800.imei()

    top_left_logo()
    ugfx.text(5, 100, "Working...", ugfx.BLACK)

    profile = {
        'unique_identifier': imei,
        'username': name,
        'age': age,
        'tag_line': tag_line,
        'looking_for': looking_for,
        'contact': contact
    }

    profile_json = ujson.dumps(profile)

    try:
        http.post(api_url+'/create_user', json=profile).raise_for_status().close()
    except:
        ugfx.clear()
        ugfx.text(5, 100, "Error. Try again later. :(", ugfx.BLACK)
        return False

    database.set("tildr_profile", profile_json)

    return True


def main_screen(my_profile):
    while True:
        next_person(my_profile)
        while True:
            if buttons.is_triggered(Buttons.BTN_Menu):
                return False
            if buttons.is_triggered(Buttons.BTN_B) or buttons.is_triggered(Buttons.JOY_Right):
                break
            # if buttons.is_triggered(Buttons.BTN_A) or buttons.is_triggered(Buttons.JOY_Left):
            #     create_profile(my_profile)
            #     break


def next_person(my_profile):
    ugfx.clear(ugfx.html_color(0x000000))
    ugfx.text(5, 100, "Loading...", ugfx.WHITE)
    try:
        resp = http.get(api_url+'/get_user/'+my_profile['unique_identifier']).json()
    except:
        ugfx.clear()
        ugfx.text(5, 100, "Error. Try again later. :(", ugfx.BLACK)
        return

    if resp['success']:
        display_person(resp['value'])
    else:
        no_more(my_profile)


def display_person(person):
    top_left_logo()

    ugfx.set_default_font(ugfx.FONT_TITLE)
    ugfx.Label(5, 90, 230, 40, person["username"], justification=ugfx.Label.LEFTTOP)
    ugfx.set_default_font(ugfx.FONT_SMALL)
    ugfx.text(200, 92, person["age"], ugfx.WHITE)

    ugfx.Label(5, 120, 230, 60, person["tag_line"])

    ugfx.Label(5, 200, 230, 40, person["looking_for"])
    ugfx.text(5, 190, "Looking for...", ugfx.RED)

    ugfx.text(5, 245, person["contact"], ugfx.BLUE)

    # ugfx.Button(0, 280, 100, 40, "< Edit profile", parent=None, shape=ugfx.Button.RECT, style=None)
    ugfx.Button(160, 280, 100, 40, "Swipe >", parent=None, shape=ugfx.Button.RECT, style=None)


def no_more(my_profile):
    top_left_logo()

    ugfx.set_default_font(ugfx.FONT_TITLE)
    ugfx.Label(5, 90, 230, 50, "You've swiped everybody!", justification=ugfx.Label.CENTERTOP)
    ugfx.set_default_font(ugfx.FONT_SMALL)
    ugfx.Label(5, 160, 230, 20, "Soz "+my_profile["username"], justification=ugfx.Label.CENTERTOP)
    ugfx.Label(5, 180, 230, 20, "Come back later ;)", justification=ugfx.Label.CENTERTOP)

    # ugfx.Button(0, 280, 100, 40, "< Edit profile", parent=None, shape=ugfx.Button.RECT, style=None)
    ugfx.Button(160, 280, 100, 40, "Try again >", parent=None, shape=ugfx.Button.RECT, style=None)




def top_left_logo():
    ugfx.clear(ugfx.html_color(0x000000))
    try:
        logo = http.get("https://i.imgur.com/5HXmXBU.png").raise_for_status().content
        ugfx.display_image(0, 5, bytearray(logo))
    except:
        pass


def quit_loop():
    while True:
        if buttons.is_triggered(Buttons.BTN_Menu):
            return False


while True:

    profile = get_profile()

    if profile is None:
        render_splash_screen()
        if not run_splash_screen():
            break
        profile = {
            'username': "",
            'age': "",
            'tag_line': "",
            'looking_for': "",
            'contact': ""
        }
        if not create_profile(profile):
            continue

    main_screen(profile)
    if not quit_loop():
        break

