""" library to display icons

http://glyph.smarticons.co/
"""

___license___ = "MIT"
___dependencies___ = ["ospath", "shared/icons/unknown.gif", "buttons"]

import ugfx, ospath

_icon_size = 50;
_half_icon_size = _icon_size // 2
_padding = 5
_padded_size = _icon_size + _padding * 2
_text_height = 30

_icon_container_style = ugfx.Style()
_icon_container_style.set_disabled([ugfx.BLACK, ugfx.WHITE, ugfx.WHITE, ugfx.RED])
_icon_container_style.set_enabled([ugfx.BLACK, ugfx.RED, ugfx.WHITE, ugfx.RED])
#_icon_container_style.set_background(ugfx.html_color(ugfx.WHITE))

class Icon:
    def __init__(self, x, y, title, path_to_icon = None):
        if path_to_icon == None or not ospath.isfile(path_to_icon):
            path_to_icon = "shared/icons/unknown.gif"
        self._selected = False
        self._init_container(x, y, title, path_to_icon)


    def _init_container(self, x, y, title, path_to_icon):
        self.container = ugfx.Container(
            x - _half_icon_size - _padding, y - _half_icon_size - _padding,
            _padded_size, _padded_size + _text_height,
            style=_icon_container_style
        )

        #This doesn't work reliably at the moment
        #ugfx.Imagebox(
        #    _padding - 2, _padding - 2,
        #    _icon_size, _icon_size,
        #    parent=self.container, text=path_to_icon
        #)

        self.label = ugfx.Label(
            0, _padded_size,
            _padded_size, _text_height,
            title, parent=self.container, justification=ugfx.Label.CENTERTOP
        )

        self.container.enabled(self._selected)

    def show(self):
        self.container.show()
        self.refresh_image()

    def refresh_image(self):
        self.container.area(_padding, _padding, _icon_size, _icon_size, ugfx.BLACK)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        self.container.enabled(value)
        self.refresh_image()

    def __del__(self):
        self.label.destroy()
        self.container.destroy()

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

class IconGrid:
    def __init__(self, x, y, items, controls):
        self._x = x
        self._y = y
        self._pages = list(chunks(items, 9))
        self._current_page_index = 0
        self._current_cursor_x = 0
        self._current_cursor_y = 0
        self._last_state = None
        self._refresh_page()

    def _refresh_page(self):
        state = (self._current_page_index, self._current_cursor_x, self._current_cursor_y)
        if self._last_state == state:
            return # nothing to do
        self._last_state = state

        self._current_icons = []
        for i, item in enumerate(self._pages[self._current_page_index]):
            x = i % 3
            y = i // 3
            icon = Icon(
                self._x + x * 60 + 30, self._y + y * 90 + 30,
                item['title'], item.get('icon', None)
            )
            icon.selected = (x == self._current_cursor_x) and (y == self._current_cursor_y)
            icon.show()
            self._current_icons.append(icon)

    def __del__(self):
        del self._current_icons

