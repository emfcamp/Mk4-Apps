CONTINUE = 1
SWITCH_SCREEN = 2
EXIT_APP = 3

DEPARTURES = 10
SETTINGS = 11

S_CONTINUE = (CONTINUE, None)
S_TO_SETTINGS = (SWITCH_SCREEN, SETTINGS)
S_TO_TRAINS = (SWITCH_SCREEN, DEPARTURES)
S_EXIT = (EXIT_APP, None)


class Screen():
    def __init__(self):
        pass

    def orientation(self):
        return 90

    def enter(self):
        pass
    
    def tick(self):
        return S_CONTINUE
        
    def exit(self):
        pass
