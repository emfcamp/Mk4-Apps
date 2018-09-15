import sleep
import ugfx
import database
from time import time
from homescreen import time_as_string
from tilda import Buttons
from trains.screen import Screen, S_CONTINUE, S_TO_SETTINGS, S_EXIT
from trains.api import get_trains
from trains.utils import get_departure, get_title, is_red

UPDATE_INTERVAL_SECS = 30

class DepartureScreen(Screen):
    def __init__(self):
        self.station_data = None
        self.has_error = False
        self.last_update = 0
        self.should_redraw = True

        self._names = None
        self._old_names = None

    def enter(self):
        self.next_state = S_CONTINUE
        self.station_code = database.get('trains.station_code', 'LBG')
        self.last_update = 0
        Buttons.enable_interrupt(
            Buttons.BTN_A,
            lambda t: self.set_next_state(S_TO_SETTINGS),
            on_press=True,
            on_release=False
        )
        Buttons.enable_interrupt(
            Buttons.BTN_Menu,
            lambda t: self.set_next_state(S_EXIT),
            on_press=True,
            on_release=False
        )
    
    def set_next_state(self, s):
        self.next_state = s

    def update(self):
        now = time()
        if self.last_update < (now - UPDATE_INTERVAL_SECS):
            print('trains/departure_screen: Updating data')
            new_station_data = get_trains(self.station_code)
            if new_station_data == None:
                self.has_error = True
                self.should_redraw = True
            else:
                self.station_data = new_station_data
                self.has_error = False
                self.should_redraw = True
            self.last_update = now
    
    def tick(self):
        self.update()

        if self.should_redraw:
            if self.station_data == None:
                self.show_error()
            else:
                self.show_trains()
        else:
            self._destroy_old_names()
        
        sleep.sleep_ms(500)
        
        return self.next_state
    
    def _get_names_container(self):
        if self._names != None:
            self._names.hide()
            self._old_names = self._names
        names = ugfx.Container(0, 25, 190, 295)
        self._names = names
        return names
    
    def _destroy_old_names(self):
        if self._old_names != None:
            self._old_names.destroy()
            self._old_names = None
    def _destroy_names(self):
        if self._names != None:
            self._names.destroy()
            self._names = None
    
    def show_trains(self):
        ugfx.clear()
        ugfx.area(0, 0, 240, 25, ugfx.RED if self.has_error else ugfx.GRAY)
        title = get_title(self.station_data['locationName'], self.has_error)
        ugfx.text(5, 5, title, ugfx.WHITE if self.has_error else ugfx.BLACK)
        ugfx.text(195, 5, time_as_string(), ugfx.BLUE)
        
        names = self._get_names_container()
        names.show()
        row_num = 0
        for service in self.station_data['trainServices']:
            departure = get_departure(service)
            if departure:
                names.text(5, 15 * row_num, service['destination'][0]['locationName'], ugfx.BLACK)
                ugfx.text(195, 25 + (15 * row_num), departure,ugfx.RED if is_red(service) else ugfx.BLUE)
                row_num += 1

        ugfx.display_image(0, 300, 'trains/bottom.gif')
        self.should_redraw = False

    def show_error(self):
        ugfx.clear()
        ugfx.text(5, 5, 'Error :(', ugfx.RED)
        self.should_redraw = False

    def exit(self):
        self._destroy_old_names()
        self._destroy_names()
        Buttons.disable_all_interrupt()
