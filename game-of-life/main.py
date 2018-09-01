"""Game of Life"""

___name___         = "Conway game of life"
___license___      = "MIT"
___categories___   = ["Games"]
___dependencies___ = ["app", "ugfx_helper", "random", "sleep", "buttons"]

import app, ugfx, ugfx_helper, buttons, sleep, time, random
from tilda import Buttons


# the game of life logic
class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [random.randint(0,1) for x in range(width * height)]

    def __str__(self):
        res  = "w: {}  h: {}".format(self.width, self.height)
        for j in range(0, self.height):
            row = [self.value(i, j) for i in range(self.width)]
            res = res + "\n" + row
        return res

    def value(self, x, y):
        return self.data[x * self.width + y]

    def neighbours(self, x, y):
        neighbCoords = [(i, j) 
            for i in range(x - 1, x + 2) if i >= 0 and i < self.width
            for j in range(y - 1, y + 2) if j >= 0 and j < self.height
        ]

        return [self.value(neighbCoord[0], neighbCoord[1]) 
                for neighbCoord in neighbCoords if neighbCoord != (x, y) ]

    # returns the new value of a given cell
    def nextValue(self, x, y):
        neighbsArr = self.neighbours(x, y)
        liveNeighbs = 0
        for neighb in neighbsArr:
            if (neighb):
                liveNeighbs = liveNeighbs + 1

        if(self.value(x, y)):
            if (liveNeighbs <= 1):
                return 0    # underpopulation
            else:
                if (liveNeighbs <= 3):
                    return 1    # lives
                else:
                    return 0    # overpopulation
        else:
            if (liveNeighbs == 3):
                return 1    # reproduction
            else:
                return 0    # dies
        
    # update the board data in place
    def step(self):
        self.data = [self.nextValue(x, y) for x in range(self.width) for y in range(self.height)]



# now the displaying part

ugfx_helper.init()
ugfx.clear()


grid_size = 5
grid_width = round(ugfx.width() / grid_size)
grid_height = round(ugfx.height() / grid_size)
alive_colours = [ugfx.WHITE, ugfx.GRAY, ugfx.BLUE, ugfx.RED, ugfx.GREEN, ugfx.YELLOW, ugfx.ORANGE]
dead_colour = ugfx.BLACK

def displayCell(x, y, alive):
    if(alive):
        colour = alive_colours[random.randrange(len(alive_colours))]
    else:
        colour = dead_colour
    ugfx.area(x*grid_size, y*grid_size, grid_size, grid_size, colour)


def displayBoard(board):
    coords = [(x, y) for x in range(board.width) for y in range(board.height)]
    for (x, y) in coords:
        displayCell(x, y, board.value(x, y))
    



board = Board(grid_width, grid_height)
while True:
    displayBoard(board)
    board.step()
    #time.sleep(1)

    sleep.wfi()
    if buttons.is_triggered(Buttons.BTN_Menu):
        break


ugfx.clear()
app.restart_to_default()
