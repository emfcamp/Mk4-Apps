"""Read stories from twentythreemillionstories.org"""

___title___        = "twenty-three million stories"
___license___      = "MIT"
___categories___   = ["Other"]
___dependencies___ = [ "app", "dialogs", "http", "ugfx_helper", "sleep" ]
___bootstrapped___ = False


from app import *
from dialogs import *

import ugfx_helper, ugfx, http, sleep, os, json
from tilda import Buttons


_STORY_URL = "http://twentythreemillionstories.org/api/story/generate"
_LOADING_TEXT = "Fetching a story..."
_FAIL_TEXT = "An artist wants to write all the stories in the world. She meets a cartographer and an inventor. The inventor makes a machine to make old stories new. The new stories are stranger than the originals, but the machine needs an internet connection. This is a great pity and the reader is sad."

_LABEL = None


def fetch_story():

    # use for testing when wifi fails
    # return "A man falls in love with two twin sisters and is unable to decide which one to marry. Only the children survive. Through the window, the boy can see two big cranes in a construction site. But he loves her so much by now that he goes on with the marriage and then, he just waits."

    # print( "fetch_story" )
    story = None

    with http.get( _STORY_URL ) as response:
        if response.status != 200:
            return _FAIL_TEXT
        story = response.raise_for_status().json()
    
    # {
    #     number: "61,957",
    #     story: "A man falls in love with two twin sisters and is unable to decide which one to marry. Only the children survive. Through the window, the boy can see two big cranes in a construction site. But he loves her so much by now that he goes on with the marriage and then, he just waits."
    # }

    return story["story"]


def draw_furniture():
    ugfx.display_image( 0, 0, "stories/header.gif" )
    ugfx.display_image( 0, 320-29, "stories/footer.gif" )


def display_story( story ):
    global _LABEL
    #_LABEL = init_label( win ) 
    # print( "display_story: %s" % story )
    ugfx.clear( ugfx.WHITE )
    draw_furniture()
    _LABEL.text( story )
    


def fetch_and_display():
    display_story( _LOADING_TEXT )
    story = fetch_story()
    display_story( story )
    

def init_label():
    
    ugfx.set_default_font( ugfx.FONT_MEDIUM )

    margin_v = 29
    margin_h = 18

    screen_w = 240
    screen_h = 320
    
    return ugfx.Label(
        margin_h, margin_v, #x, y
        screen_w - (margin_h*2) , screen_h - (margin_v*2), # width, height
        _LOADING_TEXT
    )


def init():
    # Background stuff
    ugfx_helper.init()
    ugfx.clear( ugfx.WHITE )

    # Colour stuff
    color = ugfx.html_color(333333)
    style = ugfx.Style()
    # [text_colour, edge_colour, fill_colour, progress_colour]
    style.set_enabled([color,color,ugfx.WHITE,ugfx.GREY])
    style.set_background( ugfx.WHITE )
    ugfx.set_default_style( style )


_CONFIG_FILE = "stories/stories.json"


def write_config( config ):
    with open( _CONFIG_FILE, "wt") as file:
        file.write( json.dumps(config) )
        file.flush()
    os.sync()


def read_config():
    config = None
    with open( _CONFIG_FILE, "rt") as file:
        r = file.read()
        print( r )
        config = json.loads( r )
    return config


def check_warning():
    config = read_config()
    
    if config["has_warned"]:
        return config["is_ok"]
    
    content_ok = prompt_boolean(
        """Some (not many) of the Twenty-three million stories contain potentially triggering content.\n
If that's OK by you, press A to start reading.""",
        title="Content Warning"
    )

    config = {
        "has_warned" : True,
        "is_ok" : content_ok
    }

    write_config( config )

    return content_ok


##
# MAIN RUNLOOP
#

init()

if check_warning():


    _LABEL = init_label()
    fetch_and_display()

    while True:
        
        sleep.wfi()
        
        if Buttons.is_pressed( Buttons.BTN_A ):
            fetch_and_display()
        
        elif Buttons.is_pressed( Buttons.BTN_Menu ) or \
            Buttons.is_pressed( Buttons.BTN_B ) or \
            Buttons.is_pressed( Buttons.JOY_Center):
            break

    # print ("Stories ded...")
    if _LABEL:
        _LABEL.destroy()

ugfx.clear()

