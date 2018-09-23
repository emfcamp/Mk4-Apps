"""Settlers of EMF

After a long voyage of great deprivation of wifi, your vehicles have finally reached the edge of an uncharted field at the foot of a great castle. The Electromagnetic Field! But you are not the only discoverer. Other fearless voyagers have also arrived at the foot the castle: the race to settle the Electricmagnetic Field has begun! """

___title___ = "Settlers of EMF"
___license___ = "MIT"
___dependencies___ = ["sleep"]
___categories___ = ["Games"]
___bootstrapped___ = False

import random, ugfx, math, time
from app import restart_to_default
from tilda import Buttons

ugfx.init()

# Because the button constants have no kind of order, it's hard to iterate
# through them, so keep a global list here to help us keep the code concise
BUTTONS = [
    Buttons.BTN_1,
    Buttons.BTN_2,
    Buttons.BTN_3,
    Buttons.BTN_4,
    Buttons.BTN_5,
    Buttons.BTN_6,
    Buttons.BTN_7,
    Buttons.BTN_8,
    Buttons.BTN_9,
    Buttons.BTN_0,
    ]

# Kinds of resource
SHEEP = {'kind':0, 'col': ugfx.html_color(0xd4e157)}
WHEAT = {'kind':1, 'col': ugfx.html_color(0xffc107)}
WOOD = {'kind':2, 'col': ugfx.html_color(0x993300)}
BRICK = {'kind':3, 'col': ugfx.html_color(0xff0000)}
ORE = {'kind':4, 'col': ugfx.html_color(0x757575)}
DESERT = {'kind':5, 'col': ugfx.html_color(0xffee55)}  # Not really a resource


class State:

    def run(self):
        """Runs the main loop for this state"""
        self.done = False
        self.redraw = False
        self.selection = 0

        # Render the current screen
        self.draw()

        # Enter the loop and spin until the user makes a choice
        self.initialise()
        while not self.done:
            time.sleep_ms(10)
            if self.redraw:
                self.draw()
                self.redraw = False
        self.deinitialise()

        # Then drop back out into the state machine returning the selected choice
        return self.selection

    def draw(self):
        """Renders the current state to the screen"""
        pass

    def initialise(self):
        """Perform actions that need to happen before we enter the loop"""
        pass

    def deinitialise(self):
        """Perform actions that need to happen after we exit the loop"""
        pass


class Menu(State):

    def __init__(self, question, choices):
        self.question = question
        self.choices = choices

    def is_choice_enabled(self, num):
        c = self.choices[num]
        return 'disabled' not in c or not c['disabled']

    def draw(self):
        # Draw the menu on screen
        ugfx.clear(ugfx.BLACK)
        ugfx.display_image(0, 0, 'settlers_of_emf/title.png')
        ugfx.text(5, 100, self.question, ugfx.WHITE)
        offset = 0
        for i in range(len(self.choices)):
            c = self.choices[i]
            col = ugfx.WHITE
            if 'colour' in c:
                col = c['colour']
            if not self.is_choice_enabled(i):
                col = ugfx.html_color(0x676767)
            text = "{} - {} ".format(i + 1, c['name'])
            ugfx.text(20, offset + 125, text, col)
            offset = offset + 20
            if 'cost' in c:
                for j in range(len(c['cost'])):
                    cost = c['cost'][j]
                    ugfx.area((42 * j) + 48, offset + 125, 18, 18, cost['resource']['col'])
                    ugfx.text((42 * j) + 66, offset + 125, "x{} ".format(cost['amount']), col)
                offset = offset + 20

        # Set the initial selection
        if self.is_choice_enabled(self.selection):
            self._set_selection(self.selection)
        else:
            self._set_selection(self._next_valid_selection(self.selection))

    def initialise(self):
        # Register callbacks
        Buttons.enable_interrupt(Buttons.BTN_A, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Up, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Down, self._button_callback)
        for i in range(len(self.choices)):
            if self.is_choice_enabled(i):
                Buttons.enable_interrupt(BUTTONS[i], self._button_callback)

    def deinitialise(self):
        # Unregister callbacks
        Buttons.disable_interrupt(Buttons.BTN_A)
        Buttons.disable_interrupt(Buttons.JOY_Up)
        Buttons.disable_interrupt(Buttons.JOY_Down)
        for i in range(len(self.choices)):
            if self.is_choice_enabled(i):
                Buttons.disable_interrupt(BUTTONS[i])

    def _button_callback(self, btn):
        if btn == Buttons.BTN_A:
            self.done = True
        else:
            if btn == Buttons.JOY_Up:
                new_selection = self._prev_valid_selection(self.selection)
            elif btn == Buttons.JOY_Down:
                new_selection = self._next_valid_selection(self.selection)
            else:
                for i in range(len(self.choices)):
                    if btn == BUTTONS[i]:
                        new_selection = i
            self._set_selection(new_selection)

    def _prev_valid_selection(self, sel):
        # Calculate the next enabled option going upwards
        if sel == 0:
            next_sel = len(self.choices) - 1
        else:
            next_sel = sel - 1
        while True:
            if self.is_choice_enabled(next_sel):
                break
            if next_sel == 0:
                next_sel = len(self.choices) - 1
            else:
                next_sel = next_sel - 1
        return next_sel

    def _next_valid_selection(self, sel):
        # Calculate the next enabled option going downwards
        if sel == len(self.choices) - 1:
            next_sel = 0
        else:
            next_sel = sel + 1
        while True:
            if self.is_choice_enabled(next_sel):
                break
            if next_sel == len(self.choices) - 1:
                next_sel = 0
            else:
                next_sel = next_sel + 1
        return next_sel

    def _set_selection(self, new_selection):
        # Redraws the selection box
        size = 2 if 'cost' in self.choices[self.selection] else 1
        ugfx.box(0, self._get_offset_for_selection(self.selection) + 125, 240, 20 * size, ugfx.BLACK)
        self.selection = new_selection
        size = 2 if 'cost' in self.choices[self.selection] else 1
        ugfx.box(0, self._get_offset_for_selection(self.selection) + 125, 240, 20 * size, ugfx.WHITE)

    def _get_offset_for_selection(self, sel):
        # Menu items are double height if they need to show a cost, so iterate
        # through the choices to find out exactly what the offset should be
        offset = 0
        for i in range(len(self.choices)):
            if i == sel:
                return offset
            offset = offset + 20
            if 'cost' in self.choices[i]:
                offset = offset + 20


class MainMenu(Menu):
    NEW_GAME = 0
    CONTINUE_GAME = 1
    EXIT = 2

    options = [
        {'name': "Start New Game"},
        {'name': "Continue Game"},
        {'name': "Exit"},
        ]

    def __init__(self, disable_continue_option=True):
        MainMenu.options[1]['disabled'] = disable_continue_option
        super().__init__('Main menu:', MainMenu.options)


class TeamMenu(Menu):

    options = [
        {'name': "Scottish Consulate",
         'colour': ugfx.html_color(0x0000ff)},
        {'name': "Camp Holland",
         'colour': ugfx.html_color(0xff8c00)},
        {'name': "Sheffield Hackers",
         'colour': ugfx.html_color(0x26c6da)},
        {'name': "Milliways",
         'colour': ugfx.html_color(0xff00ff)},
        {'name': "Robot Arms",
         'colour': ugfx.html_color(0xeaeaea)},
        {'name': "Null Sector",
         'colour': ugfx.html_color(0x9c27b0)},
        {'name': "Back"},
        ]

    BACK = len(options) - 1

    def __init__(self):
        super().__init__('Choose your team:', TeamMenu.options)

    def get_selected_team(self):
        return TeamMenu.options[self.selection].copy()


class BuildMenu(Menu):

    options = [
        {'name': "Road (0 points)",
         'cost': [{'resource': BRICK, 'amount': 1},
                  {'resource': WOOD, 'amount': 1}]},
        {'name': "Town (1 point)",
         'cost': [{'resource': BRICK, 'amount': 1},
                  {'resource': WOOD, 'amount': 1},
                  {'resource': SHEEP, 'amount': 1},
                  {'resource': WHEAT, 'amount': 1}]},
        {'name': "City (2 points)",
         'cost': [{'resource': WHEAT, 'amount': 2},
                  {'resource': ORE, 'amount': 3}]},
        {'name': "Back"},
        ]

    BACK = len(options) - 1

    def __init__(self, resources):
        # Disable options based on whether the player can afford them
        for option in BuildMenu.options:
            option['disabled'] = False
            if 'cost' not in option:
                continue
            for cost in option['cost']:
                for resource in resources:
                    if resource.resource == cost['resource']:
                        if resource.quantity < cost['amount']:
                            option['disabled'] = True
        super().__init__('Build a thing:', BuildMenu.options)

    def get_selected_build(self):
        return BuildMenu.options[self.selection].copy()


class Hex:
    """Hexes are the games tiles. They have a resource kind, correspond to the value
    of a roll of two D6 and may or may not contain the robber."""

    # Screen coords are x,y values that locate pixels on the physical display:
    #
    # 0,0 → → 240,0
    #  ↓         ↓
    # 0,320 → 240,320
    #
    # Hex coords are x,y,z values that locate the relative positions of hexagons:
    #
    #          0,1,-1
    # -1,1,0 ↖  ↑    ↗ 1,0,-1
    #          0,0,0
    # -1,0,1 ↙  ↓    ↘ 1,-1,0
    #          0,-1,1
    #
    # Converting between the two systems can be done by multiplying the x and y
    # coordinates against a matrix. When converting to hex coords, the z value
    # can be computed from the new x and y values because x + y + z must always
    # equal zero.
    #
    # This is the matrix used to convert from hex coords to screen coords
    matrix = [3.0 * 0.5, 0.0, math.sqrt(3.0) * 0.5, math.sqrt(3.0)]

    # The screen coordinate to use as the origin for hex coordinates,
    # the centre of hex 0,0,0 will be at this coordinate
    origin = [math.ceil(ugfx.width() / 2), math.ceil(ugfx.height() / 2)]

    # Size in pixels of the hex, from the centre point to each corner
    size = 25

    # Transformations for how to get to the neighbouring hexes
    directions = {
        0: [-1, 1, 0],  # South West
        1: [0, 1, -1],  # South
        2: [1, 0, -1],  # South East
        3: [1, -1, 0],  # North East
        4: [0, -1, 1],  # North
        5: [-1, 0, 1],  # North West
        }

    def __init__(self, coords, resource, number, robber):
        """Create a new hex at the given hex coordinates, of the given kind of resource"""
        # Validate coords
        assert len(coords) == 3, 'Invalid number of hexagon coordinates'
        assert coords[0] + coords[1] + coords[2] == 0, 'Invalid hexagon coordinate values'
        self.coords = coords

        # The kind of resource hosted by this hex
        self.resource = resource

        # The dice roll required to win this resource
        self.number = number

        # Whether this hex contains the robber
        self.robber = robber

        # Whether this hex should be highlighted
        self.highlight = False

        # A hex is quite expensive to draw, so keep track of whether the state changed recently
        # to avoid redrawing where possible
        self.changed = True

        # Compute the screen coordinates of the centre of the hex
        x = self.coords[0]
        y = self.coords[1]
        newX = (Hex.matrix[0] * x + Hex.matrix[1] * y) * Hex.size
        newY = (Hex.matrix[2] * x + Hex.matrix[3] * y) * Hex.size
        self.centre = [newX + Hex.origin[0], newY + Hex.origin[1]]

        # Generate the list of screen coordinates for each of the corners of the hex
        self.nodes = []
        for i in range(0, 6):
            angle = 2.0 * math.pi * (0 - i) / 6
            offset = [Hex.size * math.cos(angle), Hex.size * math.sin(angle)]
            self.nodes.append([int(self.centre[0] + offset[0]), int(self.centre[1] + offset[1])])

        # Generate the list of pairs of screen coordinates for each of the sides of the hex
        self.edges = []
        for i in range(0, 6):
            node1 = self.nodes[i]
            if i < 5:
                node2 = self.nodes[i + 1]
            else:
                node2 = self.nodes[0]
            if node1[0] <= node2[0]:
                self.edges.append([node1, node2])
            else:
                self.edges.append([node2, node1])

    def set_highlight(self, highlight):
        if self.highlight != highlight:
            self.highlight = highlight
            self.changed = True

    def kind(self):
        return self.resource['kind']

    @staticmethod
    def get_neighbouring_hex_coords(coords, direction):
        return [a + b for a, b in zip(coords, Hex.directions[direction])]

    def draw(self):
        if self.changed:
            self.changed = False
            ugfx.fill_polygon(0, 0, self.nodes, self.resource['col'])
            if self.highlight:
                text_colour = ugfx.WHITE
            else:
                text_colour = ugfx.BLACK
            text_offset = Hex.size * 0.45
            if self.robber:
                ugfx.text(round(self.centre[0] - Hex.size * 0.75), round(self.centre[1] - text_offset), "Rob ", text_colour)
            else:
                if self.kind() != 5:
                    ugfx.text(round(self.centre[0] - text_offset), round(self.centre[1] - text_offset), "{} ".format(self.number['roll']), text_colour)


class Settlement:
    """A node at which it is possible to build a settlement."""

    # Possible things this location may contain, the values here are the number of
    # victory points that the building is worth to the player who built it
    EMPTY = 0
    TOWN = 1
    CITY = 2

    def __init__(self, node):
        # Screen coords that define the settlement
        self.node = node

        # The list of hexes to which this settlement is adjacent
        self.hexes = []

        # What is built here and who owns it
        self.team = None
        self.contents = Settlement.EMPTY

    def is_empty(self):
        return self.contents == Settlement.EMPTY

    def prob_score(self):
        """The probability score of the location is the sum of the probability of all adjacent hexes"""
        score = 0
        for h in self.hexes:
            score = score + h.number['prob']
        return score

    def build_town(self, team):
        assert self.contents == Settlement.EMPTY, 'Town can only be built in empty location'
        self.team = team
        self.contents = Settlement.TOWN

    def build_city(self, team):
        assert self.contents == Settlement.TOWN and self.team['name'] == team['name'], 'City can only be built in place of one of your own towns'
        self.contents = Settlement.CITY

    def draw(self):
        if self.contents == Settlement.TOWN:
            ugfx.fill_circle(self.node[0], self.node[1], 4, self.team['colour'])
            ugfx.circle(self.node[0], self.node[1], 4, ugfx.WHITE)
        elif self.contents == Settlement.CITY:
            ugfx.fill_circle(self.node[0], self.node[1], 8, self.team['colour'])
            ugfx.circle(self.node[0], self.node[1], 8, ugfx.WHITE)


class Road:
    """An edge along which it is possible to build a road."""

    EMPTY = 0
    ROAD = 1

    def __init__(self, edge):
        # List of screen coords that define the road
        self.edge = edge

        # What is built here and who owns it
        self.team = None
        self.contents = Road.EMPTY

    def is_empty(self):
        return self.contents == Road.EMPTY

    def build_road(self, team):
        assert self.contents == Road.EMPTY, 'Road can only be built in empty location'
        self.team = team
        self.contents = Road.ROAD

    def draw(self):
        if self.contents == Road.ROAD:
            ugfx.thickline(self.edge[0][0], self.edge[0][1], self.edge[1][0], self.edge[1][1], ugfx.WHITE, 6, False)
            ugfx.thickline(self.edge[0][0], self.edge[0][1], self.edge[1][0], self.edge[1][1], self.team['colour'], 4, False)


class Resource():

    def __init__(self, resource):
        self.resource = resource
        self.quantity = 0

    def kind(self):
        return self.resource['kind']

    def colour(self):
        return self.resource['col']

    def increment(self, num=1):
        self.quantity = self.quantity + num

    def decrement(self, num=1):
        self.quantity = self.quantity - num
        if self.quantity < 0:
            self.quantity = 0


class Player:
    """The player's hand of resource cards and their score and what not."""

    def __init__(self, team, roads, settlements):
        # Player team details
        self.team = team

        # All the buildable game board locations
        self.roads = roads
        self.settlements = settlements

        # Player's hand of resources
        self.resources = []
        for kind in [SHEEP, WHEAT, WOOD, BRICK, ORE]:
            r = Resource(kind)
            self.resources.append(r)

            # Collect starting resources from the hexes adjacent to our starting settlements
            for s in [x for x in self.settlements if x.team == self.team]:
                for h in s.hexes:
                    if r.kind() == h.kind():
                        r.increment()

        # Turn number
        self.turn = 0

    def score(self):
        points = 0
        for s in [x for x in self.settlements if x.team == self.team]:
            points = points + s.contents
        return points

    def increment_turn(self):
        self.turn = self.turn + 1

    def num_resources(self):
        return sum([x.quantity for x in self.resources])

    def collect(self, num):
        if num == 7:
            # If total number of resources is over 7, lose half of them (rounded down)
            total = self.num_resources()
            if total > 7:
                lose = int(total / 2)
                while self.num_resources() > total - lose:
                    self.resources[random.randrange(0, len(self.resources))].decrement()
        else:
            # Collect resources for each hex adjacent to our settlements that corresponds
            # with the given dice roll
            for s in [x for x in self.settlements if x.team == self.team]:
                for h in s.hexes:
                    if h.number['roll'] == num and not h.robber:
                        for r in self.resources:
                            if r.kind() == h.kind():
                                if s.contents == Settlement.TOWN:
                                    r.increment()
                                elif s.contents == Settlement.CITY:
                                    r.increment(2)

    def draw(self):
        # Player's team and score
        ugfx.text(5, 8, "{} ".format(self.team['name']), self.team['colour'])
        ugfx.text(5, 28, "Points: {} ".format(self.score()), ugfx.WHITE)
        ugfx.text(5, 48, "Turn: {} ".format(self.turn), ugfx.WHITE)

        # Player's resources
        ugfx.area(0, 290, 240, 30, ugfx.BLACK)
        offset = int(ugfx.width() / len(self.resources))
        square = int(offset / 3)
        for i in range(len(self.resources)):
            ugfx.area((offset * i) + 1, 295, square, 20, self.resources[i].colour())
            ugfx.text((offset * i) + 1 + square, 295, "{} ".format(self.resources[i].quantity), ugfx.WHITE)


class Dice:

    # Size in pixels that the dice will be drawn on screen
    size = 25

    def __init__(self):
        self.reset()

    def roll(self):
        self.die1 = random.randint(1, 6)
        self.die2 = random.randint(1, 6)

    def reset(self):
        self.die1 = 0
        self.die2 = 0

    def total(self):
        return self.die1 + self.die2

    def draw(self):
        self._draw_die(210, 5, self.die1)
        self._draw_die(210, 5 + Dice.size + 5, self.die2)

    def _draw_die(self, x, y, num):
        ugfx.box(x, y, Dice.size, Dice.size, ugfx.html_color(0x676767))
        ugfx.area(x + 1, y + 1, Dice.size - 2, Dice.size - 2, ugfx.BLACK)
        if num == 1:
            self._draw_one_dot(x, y)
        if num == 2:
            self._draw_two_dot(x, y)
        if num == 3:
            self._draw_one_dot(x, y)
            self._draw_two_dot(x, y)
        if num == 4:
            self._draw_four_dot(x, y)
        if num == 5:
            self._draw_one_dot(x, y)
            self._draw_four_dot(x, y)
        if num == 6:
            self._draw_six_dot(x, y)

    def _draw_one_dot(self, x, y):
        ugfx.fill_circle(x + int(Dice.size / 2), y + int(Dice.size / 2), 1, ugfx.WHITE)

    def _draw_two_dot(self, x, y):
        ugfx.fill_circle(1 + x + int(Dice.size / 8), (y - 1) + (Dice.size - int(Dice.size / 8)), 1, ugfx.WHITE)
        ugfx.fill_circle((x - 2) + (Dice.size - int(Dice.size / 8)), 1 + y + int(Dice.size / 8), 1, ugfx.WHITE)

    def _draw_four_dot(self, x, y):
        self._draw_two_dot(x, y)
        ugfx.fill_circle(1 + x + int(Dice.size / 8), 1 + y + int(Dice.size / 8), 1, ugfx.WHITE)
        ugfx.fill_circle((x - 2) + (Dice.size - int(Dice.size / 8)), (y - 1) + (Dice.size - int(Dice.size / 8)), 1, ugfx.WHITE)

    def _draw_six_dot(self, x, y):
        self._draw_four_dot(x, y)
        ugfx.fill_circle(1 + x + int(Dice.size / 8), y + int(Dice.size / 2), 1, ugfx.WHITE)
        ugfx.fill_circle((x - 2) + (Dice.size - int(Dice.size / 8)), y + int(Dice.size / 2), 1, ugfx.WHITE)


class GameBoard(State):
    MAIN_MENU = 0
    BUILD_MENU = 1
    END_TURN = 2

    # List of resources (pre-randomised to combat the not-very random number
    # generator) that make up the hexes on the game board for 4 players
    resources = [ORE, SHEEP, WHEAT, ORE, ORE, WOOD, DESERT, BRICK, SHEEP, WOOD,
                 WHEAT, WOOD, WOOD, WHEAT, SHEEP, BRICK, SHEEP, BRICK, WHEAT]

    # Dice roll probabilities
    TWO = {'roll':2, 'prob':1}
    THREE = {'roll':3, 'prob':2}
    FOUR = {'roll':4, 'prob':3}
    FIVE = {'roll':5, 'prob':4}
    SIX = {'roll':6, 'prob':5}
    SEVEN = {'roll':7, 'prob':0}  # Most probable, but zero because desert
    EIGHT = {'roll':8, 'prob':5}
    NINE = {'roll':9, 'prob':4}
    TEN = {'roll':10, 'prob':3}
    ELEVEN = {'roll':11, 'prob':2}
    TWELVE = {'roll':12, 'prob':1}

    # Dice rolls for (these have a strict order) to be assigned to the resource
    # hexes for 4 player games
    numbers = [FIVE, TWO, SIX, THREE, EIGHT, TEN, NINE, TWELVE, ELEVEN, FOUR,
               EIGHT, TEN, NINE, FOUR, FIVE, SIX, THREE, ELEVEN]

    def __init__(self, team):
        # Two rings of hexes around the centre
        radius = 2

        # Choose a starting hex on the outermost ring of hexes
        choice = random.randrange(0, 6)
        coords = [0, 0, 0]
        for i in range(radius):
            coords = [a + b for a, b in zip(coords, Hex.directions[choice])]

        # Copy lists so we can edit them with impunity
        r_copy = GameBoard.resources.copy()
        n_copy = GameBoard.numbers.copy()

        self.hexes = []
        while radius > 0:
            # From the starting hex, go radius hexes in each of the 6 directions
            for i in list(range((choice + 2) % 6, 6)) + list(range(0, (choice + 2) % 6)):
                for _ in range(radius):
                    # The resources are picked at random from the list
                    resource = r_copy.pop(random.randrange(0, len(r_copy)))
                    # But the dice roll numbers are picked in order, unless it's
                    # the desert in which case that is always 7
                    number = GameBoard.SEVEN
                    if resource['kind'] != 5:
                        number = n_copy.pop(0)
                    self.hexes.append(Hex(coords, resource, number, number['roll'] == 7))
                    coords = Hex.get_neighbouring_hex_coords(coords, i)

            # Go into the next ring of hexes (opposite direction of starting choice)
            coords = Hex.get_neighbouring_hex_coords(coords, (choice + 3) % 6)
            radius = radius - 1
        # The final, centre hex
        resource = r_copy.pop()
        number = GameBoard.SEVEN
        if resource['kind'] != 5:
            number = n_copy.pop(0)
        self.hexes.append(Hex(coords, resource, number, number['roll'] == 7))

        # Note the initial location of the robber to ensure it moves when activated
        self.robber_mode = False
        self.robber_hex = self.get_robber_hex()

        # Generate lists of unique valid locations for building
        self.roads = []
        self.settlements = []
        for h in self.hexes:
            for edge in h.edges:
                already_got = False
                for r in self.roads:
                    if r.edge == edge:
                        already_got = True
                if not already_got:
                    r = Road(edge)
                    self.roads.append(r)
            for node in h.nodes:
                already_got = False
                for s in self.settlements:
                    if s.node == node:
                        already_got = True
                        s.hexes.append(h)
                if not already_got:
                    s = Settlement(node)
                    s.hexes.append(h)
                    self.settlements.append(s)

        # Give the team starting towns in the two settlements with the highest probability score
        # TODO interleave starting town choices for multi-player
        self.pick_starting_settlement(team)
        self.pick_starting_settlement(team)

        # The dice roller
        self.dice = Dice()

        # The player details
        self.player = Player(team, self.roads, self.settlements)

    def get_roads_for_settlement(self, settlement):
        """Return a list of roads that connect to the given settlement"""
        roads = []
        for road in self.roads:
            if settlement.node in road.edge:
                roads.append(road)
        return roads

    def can_build_settlement(self, settlement):
        """Determines if a given settlement is at least two roads from any other settlement"""
        for r in self.get_roads_for_settlement(settlement):
            # Get coords for the settlement at the other end of the road
            for coords in r.edge:
                for s in self.settlements:
                    if s.node == coords and s != settlement:
                        if not s.is_empty():
                            return False
        return True

    def pick_starting_settlement(self, team):
        """Choose a starting settlement for the given team, and place a town and a connecting road there"""

        # Sort the settlements by highest dice roll probability
        sorted_settlements = sorted(self.settlements, key=lambda s: s.prob_score())
        sorted_settlements.reverse()

        # Build at the highest probability settlement that is still available
        for s in sorted_settlements:
            if s.is_empty() and self.can_build_settlement(s):
                s.build_town(team)
                s_roads = self.get_roads_for_settlement(s)
                s_roads[random.randrange(0, len(s_roads))].build_road(team)
                break

    def draw(self):
        if not self.redraw:
            ugfx.clear(ugfx.BLACK)
        self.dice.draw()
        for h in self.hexes:
            h.draw()
        for r in self.roads:
            r.draw()
        for s in self.settlements:
            s.draw()
        self.player.draw()

    def initialise(self):
        # Register callbacks
        Buttons.enable_interrupt(Buttons.BTN_Menu, self._button_callback)
        Buttons.enable_interrupt(Buttons.BTN_A, self._button_callback)
        Buttons.enable_interrupt(Buttons.BTN_B, self._button_callback)
        Buttons.enable_interrupt(Buttons.BTN_Star, self._button_callback)
        Buttons.enable_interrupt(Buttons.BTN_Hash, self._button_callback)
        # For moving the robber
        Buttons.enable_interrupt(Buttons.JOY_Up, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Down, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Left, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Right, self._button_callback)

    def deinitialise(self):
        # Unregister callbacks
        Buttons.disable_interrupt(Buttons.BTN_Menu)
        Buttons.disable_interrupt(Buttons.BTN_A)
        Buttons.disable_interrupt(Buttons.BTN_B)
        Buttons.disable_interrupt(Buttons.BTN_Star)
        Buttons.disable_interrupt(Buttons.BTN_Hash)
        # For moving the robber
        Buttons.disable_interrupt(Buttons.JOY_Up)
        Buttons.disable_interrupt(Buttons.JOY_Down)
        Buttons.disable_interrupt(Buttons.JOY_Left)
        Buttons.disable_interrupt(Buttons.JOY_Right)

        # Ensure all hexes are drawn next time we enter this state
        for h in self.hexes:
            h.changed = True

    def _button_callback(self, btn):
        if not self.robber_mode:
            if btn == Buttons.BTN_Menu:
                self.selection = GameBoard.MAIN_MENU
                self.done = True
            if btn == Buttons.BTN_B:
                self.selection = GameBoard.BUILD_MENU
                self.done = True
            if btn == Buttons.BTN_Star:
                # Can end the turn if dice were rolled
                if self.dice.total() != 0:
                    self.selection = GameBoard.END_TURN
                    self.done = True
            if btn == Buttons.BTN_Hash:
                # Only roll the dice if not already rolled
                if self.dice.total() == 0:
                    self.dice.roll()
                    # Highlight the hexes corresponding with the dice roll
                    num = self.dice.total()
                    for h in self.hexes:
                        if (h.number['roll'] == num and not h.robber) or (num == 7 and h.robber):
                            h.set_highlight(True)
                        else:
                            h.set_highlight(False)
                    # Collect resources corresponding with the dice roll
                    self.player.collect(num)
                    # Activate the robber on a seven
                    if num == 7:
                        self.robber_mode = True
                    self.redraw = True
        else:
            h_current = self.get_robber_hex()
            if btn == Buttons.BTN_A:
                # The robber may not stay in the same hex, ensure it moved
                if h_current != self.robber_hex:
                    self.robber_hex = h_current
                    self.robber_hex.set_highlight(False)
                    self.robber_mode = False
                    self.redraw = True
                    # TODO: Steal a card from a player at this hex
            if btn == Buttons.JOY_Up:
                self._move_robber(h_current, 4)
            if btn == Buttons.JOY_Down:
                self._move_robber(h_current, 1)
            if btn == Buttons.JOY_Left:
                self._move_robber(h_current, 0 if h_current.coords[0] % 2 == 0 else 5)
            if btn == Buttons.JOY_Right:
                self._move_robber(h_current, 2 if h_current.coords[0] % 2 == 0 else 3)

    def _move_robber(self, h_current, direction):
        coords = Hex.get_neighbouring_hex_coords(h_current.coords, direction)
        h_next = self.get_hex_for_coords(coords)
        self.move_robber(h_current, h_next)
        self.redraw = True

    def get_robber_hex(self):
        for h in self.hexes:
            if h.robber:
                return h
        return None

    def get_hex_for_coords(self, coords):
        for h in self.hexes:
            if h.coords == coords:
                return h
        return None

    def move_robber(self, from_hex, to_hex):
        if to_hex:
            from_hex.robber = False
            from_hex.set_highlight(False)
            to_hex.robber = True
            to_hex.set_highlight(True)

    def next_player(self):
        """ Call from the state machine to reset the board for the next player"""
        self.player.increment_turn()
        self.dice.reset()
        for h in self.hexes:
            h.set_highlight(False)

class Settlers:
    """A lean mean state machine"""

    # Game states
    EXIT = 0
    MAIN_MENU = 1
    TEAM_MENU = 2
    GAME = 3
    BUILD_MENU = 4
    END_TURN_MENU = 5

    def __init__(self):
        self.state = Settlers.MAIN_MENU
        self.game = None

    def run(self):
        while self.state != Settlers.EXIT:

            if self.state == Settlers.MAIN_MENU:
                menu = MainMenu(self.game is None)
                x = menu.run()
                if x == MainMenu.NEW_GAME:
                    self.state = Settlers.TEAM_MENU
                if x == MainMenu.CONTINUE_GAME:
                    self.state = Settlers.GAME
                if x == MainMenu.EXIT:
                    self.state = Settlers.EXIT

            if self.state == Settlers.TEAM_MENU:
                menu = TeamMenu()
                x = menu.run()
                if x == TeamMenu.BACK:
                    self.state = Settlers.MAIN_MENU
                else:
                    self.game = GameBoard(menu.get_selected_team())
                    self.game.next_player()
                    self.state = Settlers.GAME

            if self.state == Settlers.GAME:
                x = self.game.run()
                if x == GameBoard.MAIN_MENU:
                    self.state = Settlers.MAIN_MENU
                if x == GameBoard.BUILD_MENU:
                    self.state = Settlers.BUILD_MENU
                if x == GameBoard.END_TURN:
                    self.state = Settlers.END_TURN_MENU

            if self.state == Settlers.BUILD_MENU:
                menu = BuildMenu(self.game.player.resources)
                x = menu.run()
                if x == BuildMenu.BACK:
                    self.state = Settlers.GAME
                else:
                    # TODO initiate building a thing
                    self.state = Settlers.GAME

            if self.state == Settlers.END_TURN_MENU:
                self.game.next_player()
                # TODO: Ask for confirmation
                self.state = Settlers.GAME

        # User chose exit, a machine reset is the easiest way :-)
        restart_to_default()


game = Settlers()
game.run()
