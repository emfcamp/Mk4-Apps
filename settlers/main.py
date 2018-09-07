"""Settlers of Catan game board generator"""

___name___ = "settlers"
___license___ = "MIT"
___dependencies___ = ["ugfx_helper", "sleep"]
___categories___ = ["Games"]
___bootstrapped___ = False

import random, ugfx, ugfx_helper, math, time, buttons
from app import App, restart_to_default
from tilda import Buttons

ugfx_helper.init()
ugfx.clear(ugfx.BLACK)

"""
This was an experiment in drawing hexagons. Some notes:

Screen coords are x,y values that locate pixels on the physical display:

0,0 → → 240,0
 ↓         ↓
0,320 → 240,320

Hex coords are x,y,z values that locate the relative positions of hexagons:

         0,1,-1
-1,1,0 ↖  ↑    ↗ 1,0,-1
         0,0,0
-1,0,1 ↙  ↓    ↘ 1,-1,0
         0,-1,1

Converting between the two systems can be done by multiplying the x and y
coordinates against a matrix. When converting to hex coords, the z value
can be computed from the new x and y values because x + y + z must always
equal zero.
 
"""

class Hex:
    # Constant matrix used to convert from hex coords to screen coords
    matrix = [3.0 * 0.5, 0.0, math.sqrt(3.0) * 0.5, math.sqrt(3.0)]

    # The screen coordinate to use as the origin for hex coordinates,
    # the centre of hex 0,0,0 will be at this coordinate
    origin = [math.ceil(ugfx.width() / 2), math.ceil(ugfx.height() / 2)]

    # Size in pixels of the hex, from the centre point to each corner
    size = 22

    # Possible kinds of resource and the colour it should be rendered
    kinds = {
        0: ugfx.html_color(0xd4e157),  # Sheep
        1: ugfx.html_color(0xffc107),  # Wheat
        2: ugfx.html_color(0x993300),  # Wood
        3: ugfx.html_color(0xff0000),  # Brick
        4: ugfx.html_color(0x757575),  # Ore
        5: ugfx.html_color(0xffee55),  # Desert (nothing)
        }
    
    # Transformations for how to get to the neighbouring hexes
    directions = {
        0: [-1, 1, 0],  # South West
        1: [0, 1, -1],  # South
        2: [1, 0, -1],  # South East
        3: [1, -1, 0],  # North East
        4: [0, -1, 1],  # North
        5: [-1, 0, 1],  # North West
        }
    
    def __init__(self, coords, kind, number, robber):
        """Create a new hex at the given hex coordinates, of the given kind of resource"""
        # Validate coords
        assert len(coords) == 3, 'Invalid number of hexagon coordinates'
        assert coords[0] + coords[1] + coords[2] == 0, 'Invalid hexagon coordinate values'
        self.coords = coords
        
        # The kind of resource hosted by this hex
        self.kind = kind
        
        # The dice roll required to win this resource
        self.number = number

        # Whether this hex contains the robber
        self.robber = robber

        # Compute the screen coordinates of the centre of the hex
        self.centre = Hex.to_screen_coords(self.coords[0], self.coords[1])

        # Generate screen coordinates for each of the corners of the hex
        self.corners = []
        for i in range(0, 6):
            angle = 2.0 * math.pi * (0 - i) / 6
            offset = [Hex.size * math.cos(angle), Hex.size * math.sin(angle)]
            self.corners.append([round(self.centre[0] + offset[0]), round(self.centre[1] + offset[1])])

    @staticmethod
    def to_screen_coords(x, y):
        """Returns screen coordinates computed from the given hex coordinates"""
        newX = (Hex.matrix[0] * x + Hex.matrix[1] * y) * Hex.size
        newY = (Hex.matrix[2] * x + Hex.matrix[3] * y) * Hex.size
        return [newX + Hex.origin[0], newY + Hex.origin[1]]

    @staticmethod
    def get_neighbouring_hex_coords(coords, direction):
        return [a + b for a, b in zip(coords, Hex.directions[direction])]

    def draw(self):
        """Draw the hexagon to the screen"""
        ugfx.fill_polygon(0, 0, self.corners, Hex.kinds[self.kind])
        text_offset = Hex.size * 0.5
        if self.robber:
            ugfx.text(round(self.centre[0] - text_offset), round(self.centre[1] - text_offset), "Rb ", ugfx.BLACK)
        else:
            if self.kind != 5:
                ugfx.text(round(self.centre[0] - text_offset), round(self.centre[1] - text_offset), "{} ".format(self.number), ugfx.BLACK)

    def clear(self):
        ugfx.fill_polygon(0, 0, self.corners, ugfx.BLACK)


def board_setup(resources, numbers):
    """Generate a random game board"""

    # Two rings of hexes around the centre
    radius = 2
    # Choose a starting hex on the outermost ring of hexes
    choice = random.randrange(0, 6)
    coords = [0, 0, 0]
    for i in range(radius):
        coords = [a + b for a, b in zip(coords, Hex.directions[choice])]

    # Copy lists so we can edit them with impunity
    r_copy = resources.copy()
    n_copy = numbers.copy()

    hexes = []
    while radius > 0:
        # From the starting hex, go radius hexes in each of the 6 directions
        for i in list(range((choice + 2) % 6, 6)) + list(range(0, (choice + 2) % 6)):
            for j in range(radius):
                # The resources are picked at random from the list
                resource = r_copy.pop(random.randrange(0, len(r_copy)))
                # But the dice roll numbers are picked in order, unless it's
                # the desert in which case that is always 7
                if resource == 5:
                    number = 7
                else:
                    number = n_copy.pop(0)
                hexes.append(Hex(coords, resource, number, number == 7))
                coords = Hex.get_neighbouring_hex_coords(coords, i)

        # Go into the next ring of hexes (opposite direction of starting choice)
        coords = Hex.get_neighbouring_hex_coords(coords, (choice + 3) % 6)
        radius = radius - 1
    resource = r_copy.pop()
    if resource == 5:
        number = 7
    else:
        number = n_copy.pop(0)
    hexes.append(Hex(coords, resource, number, number == 7))
    return hexes


# List of resources (pre-randomised to combat the not-very random number
# generator) and dice rolls (these have a strict order) for 2-4 player games
resources = [4, 0, 1, 4, 4, 2, 5, 3, 2, 1, 2, 2, 1, 0, 3, 0, 3, 1, 0]
numbers = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]

def draw():
    hexes = board_setup(resources, numbers)
    for h in hexes:
        h.clear()
        time.sleep_ms(100)
        h.draw()

ugfx.text(5, 5, 'Press A to generate another ', ugfx.WHITE)
draw()

# Main Loop
while True:
    if buttons.is_triggered(tilda.Buttons.BTN_A):
        draw()
    elif buttons.is_triggered(tilda.Buttons.BTN_Menu):
        break
    time.sleep_ms(5)
restart_to_default()
