import database, ujson, sim800, dialogs, http


def get_profile():
    profile_json = database.get("tildr_profile")
    if profile_json is None:
        return {}

    profile = ujson.loads(profile_json)
    return profile

def create_profile(state):
    try:
        http.post(state['api']+'/create_user', json=state['profile']).raise_for_status().close()
    except Exception as ex:
        print(ex)
        return False

    profile_json = ujson.dumps(state['profile'])
    database.set("tildr_profile", profile_json)

    return True

def screen(state):

    if state['profile'] is None:
        state['profile'] = {
            'unique_identifier': "",
            'username': "",
            'age': "",
            'tag_line': "",
            'looking_for': "",
            'contact': ""
        }

    ds = [
        ["username", "What's your name?"],
        ["age", "What's your age?"],
        ["tag_line", "Tell us your tagline"],
        ["looking_for", "And what you're looking for"],
        ["contact", "And your twitter username"],
    ]

    i = 0

    while i < len(ds):
        res = dialogs.prompt_text(ds[i][1], init_text=state['profile'][ds[i][0]])
        if res is None:
            i -= 1
            if i < 0:
                state['next'] = "SPLASH"
                return
        elif res != "":
            state['profile'][ds[i][0]] = res
            i += 1

    state['profile']['unique_identifier'] = sim800.imei()

    if not create_profile(state):
        state['next'] = "ERROR"
        return

    state['next'] = "NEXT_PERSON"

def actions(state):
    return
