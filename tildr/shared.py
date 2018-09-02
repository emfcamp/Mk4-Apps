import ugfx, http

def clear():
    ugfx.clear(ugfx.html_color(0x000000))


def top_left_logo():
    try:
        # logo = http.get("https://i.imgur.com/5HXmXBU.png").raise_for_status().content
        ugfx.display_image(1, 5, "tildr/smalllogo.png")
    except:
        pass
