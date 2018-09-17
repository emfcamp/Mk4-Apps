import database
import ugfx
from dialogs import prompt_text
from trains.screen import Screen, S_CONTINUE, S_TO_TRAINS

class SettingsScreen(Screen):
    def __init__(self):
        self.next_state = S_TO_TRAINS
    
    def orientation(self):
        return 270
    
    def tick(self):
        with database.Database() as db:
            crs = prompt_text('Enter your station\'s CRS code', db.get('trains.station_code', ''))
            db.set('trains.station_code', crs)

        return self.next_state
    