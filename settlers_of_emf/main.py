"""Settlers of EMF

After a long voyage and great deprivation of wifi, your vehicles have finally reached the edge of an uncharted field at the foot of a great castle. The Electromagnetic Field!

But you are not the only discoverer. Other fearless voyagers have also arrived at the foot the castle; the race to settle the Electricmagnetic Field has begun!

Settlers of EMF is a pass-and-play game of ruthless strategy for up to 4 players of all ages."""

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
RESOURCE_KINDS = [ SHEEP, WHEAT, WOOD, BRICK, ORE ]

# Set this to true to enable a "cheat code" to get more resources for testing
# When in the main game running state, press 5 five times to get five more of
# every resource
TEST_MODE = False


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

    def __init__(self, question, choices, clear_title=True):
        self.question = question
        self.choices = choices
        self.clear_title = clear_title
        if self.question:
            if isinstance(self.question, list):
                self.menu_offset = 100 + (20 * len(self.question))
            else:
                self.question = [question]
                self.menu_offset = 120
        else:
            self.menu_offset = 100
        self.back = -1

    def is_choice_enabled(self, num):
        c = self.choices[num]
        return 'disabled' not in c or not c['disabled']

    def get_selected_choice(self):
        return self.choices[self.selection].copy()

    def draw(self):
        # Draw the menu on screen
        if self.clear_title:
            ugfx.clear(ugfx.BLACK)
            ugfx.display_image(0, 0, 'settlers_of_emf/title.png')
        else:
            ugfx.area(0, 95, 240, 225, ugfx.BLACK)
        if self.question:
            for i in range(len(self.question)):
                ugfx.text(2, 95 + (i * 20), self.question[i], ugfx.WHITE)
        offset = 0
        for i in range(len(self.choices)):
            self._draw_choice(i, offset)
            offset = offset + 20
            if 'cost' in self.choices[i]:
                offset = offset + 20

        # Set the initial selection
        if self.is_choice_enabled(self.selection):
            self._set_selection(self.selection)
        else:
            self._set_selection(self._next_valid_selection(self.selection))

    def _draw_choice(self, i, offset):
        c = self.choices[i]
        col = ugfx.WHITE
        if 'colour' in c:
            col = c['colour']
        if not self.is_choice_enabled(i):
            col = ugfx.html_color(0x676767)
        if len(self.choices) == 1:
            text = "{} ".format(c['name'])
        else:
            if c['name'] == "Back":
                text = "B - {} ".format(c['name'])
                self.back = i
            else:
                text = "{} - {} ".format(i + 1, c['name'])
        ugfx.text(18, offset + self.menu_offset, text, col)
        if 'cost' in c:
            for j in range(len(c['cost'])):
                cost = c['cost'][j]
                if 'cost_or' in c and c['cost_or']:
                    cost_text = "x{}  / ".format(cost['amount'])
                    if j == len(c['cost']) - 1:
                        cost_text = "x{} ".format(cost['amount'])
                    ugfx.area((63 * j) + 45, 21 + offset + self.menu_offset, 16, 16, cost['resource']['col'])
                    ugfx.text((63 * j) + 61, 20 + offset + self.menu_offset, cost_text, col)
                else:
                    ugfx.area((42 * j) + 45, 21 + offset + self.menu_offset, 16, 16, cost['resource']['col'])
                    ugfx.text((42 * j) + 61, 20 + offset + self.menu_offset, "x{} ".format(cost['amount']), col)

    def initialise(self):
        # Register callbacks
        Buttons.enable_interrupt(Buttons.BTN_A, self._button_callback)
        Buttons.enable_interrupt(Buttons.BTN_B, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Up, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Down, self._button_callback)
        for i in range(len(self.choices)):
            if self.is_choice_enabled(i):
                Buttons.enable_interrupt(BUTTONS[i], self._button_callback)

    def deinitialise(self):
        # Unregister callbacks
        Buttons.disable_interrupt(Buttons.BTN_A)
        Buttons.disable_interrupt(Buttons.BTN_B)
        Buttons.disable_interrupt(Buttons.JOY_Up)
        Buttons.disable_interrupt(Buttons.JOY_Down)
        for i in range(len(self.choices)):
            if self.is_choice_enabled(i):
                Buttons.disable_interrupt(BUTTONS[i])

    def _button_callback(self, btn):
        if btn == Buttons.BTN_A:
            self.done = True
        elif btn == Buttons.BTN_B:
            if self.back > -1:
                self._set_selection(self.back)
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
        size = 2 if 'cost' in self.choices[self.selection] and len(self.choices[self.selection]['cost']) > 0 else 1
        ugfx.box(0, self._get_offset_for_selection(self.selection) + self.menu_offset, 240, 20 * size, ugfx.BLACK)
        self.selection = new_selection
        size = 2 if 'cost' in self.choices[self.selection] and len(self.choices[self.selection]['cost']) > 0 else 1
        ugfx.box(0, self._get_offset_for_selection(self.selection) + self.menu_offset, 240, 20 * size, ugfx.WHITE)

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

    options = [
        {'name': "Start New Game"},
        {'name': "Continue Game"},
        {'name': "Exit"},
        ]

    NEW_GAME = 0
    CONTINUE_GAME = 1
    EXIT = 2

    def __init__(self, disable_continue_option=True, clear_title=True):
        MainMenu.options[MainMenu.CONTINUE_GAME]['disabled'] = disable_continue_option
        super().__init__('Welcome!', MainMenu.options, clear_title)


class TeamMenu(Menu):

    options = [
        {'name': "Scottish Consulate",
         'colour': ugfx.html_color(0x0000ff)},
        {'name': "Camp Holland",
         'colour': ugfx.html_color(0xff8c00)},
        {'name': "Sheffield Hackspace",
         'colour': ugfx.html_color(0x26c6da)},
        {'name': "Milliways",
         'colour': ugfx.html_color(0xff00ff)},
        {'name': "Robot Arms",
         'colour': ugfx.html_color(0xeaeaea)},
        {'name': "Null Sector",
         'colour': ugfx.html_color(0x9c27b0),
         'cost': []},
        {'name': "Start Game"},
        {'name': "Back"},
        ]

    TEAM_MAX = len(options) - 3
    START_GAME = len(options) - 2
    BACK = len(options) - 1

    def __init__(self, teams):
        # Disable team options based on which have already been chosen
        for option in TeamMenu.options:
            if 'colour' not in option:
                continue
            option['disabled'] = option['name'] in [team['name'] for team in teams]
        TeamMenu.options[TeamMenu.START_GAME]['disabled'] = len(teams) == 0
        super().__init__('Player {}, choose a team:'.format(len(teams) + 1), TeamMenu.options, False)


class ActionMenu(Menu):

    options = [
        {'name': "Build"},
        {'name': "Trade"},
        {'name': "End Turn"},
        {'name': "Exit Game"},
        {'name': "Back"},
        ]

    BUILD = 0
    TRADE = 1
    END_TURN = 2
    EXIT_GAME = 3
    BACK = 4

    def __init__(self, dice_roll, clear_title=True):
        # Rolling the dice is mandatory, so don't let the turn end unless it happened
        ActionMenu.options[ActionMenu.END_TURN]['disabled'] = dice_roll == 0
        super().__init__('Do a thing:', ActionMenu.options, clear_title)


class BuildMenu(Menu):

    options = [
        {'name': "Build Road (0 points)",
         'cost': [{'resource': BRICK, 'amount': 1},
                  {'resource': WOOD, 'amount': 1}]},
        {'name': "Build Town (1 point)",
         'cost': [{'resource': BRICK, 'amount': 1},
                  {'resource': WOOD, 'amount': 1},
                  {'resource': SHEEP, 'amount': 1},
                  {'resource': WHEAT, 'amount': 1}]},
        {'name': "Upgrade to City (2 points)",
         'cost': [{'resource': WHEAT, 'amount': 2},
                  {'resource': ORE, 'amount': 3}]},
        {'name': "Back"},
        ]

    ROAD = 0
    TOWN = 1
    CITY = 2
    BACK = 3

    def __init__(self, resources):
        # Disable build options based on whether the player can afford them
        for option in BuildMenu.options:
            if 'cost' not in option:
                continue
            option['disabled'] = False
            for cost in option['cost']:
                for resource in resources:
                    if resource.resource == cost['resource']:
                        if resource.quantity < cost['amount']:
                            option['disabled'] = True
        super().__init__(None, BuildMenu.options, False)


class TradeMenu(Menu):

    BACK = len(RESOURCE_KINDS)

    def __init__(self, resources):
        # Disable trade options based on whether the player can afford them
        options = []
        for i in range(len(RESOURCE_KINDS)):
            option = {'name': "Buy a", 'resource': RESOURCE_KINDS[i], 'cost': [], 'cost_or': True}
            option['disabled'] = True
            for resource_kind in RESOURCE_KINDS:
                if resource_kind['kind'] != i:
                    for resource in resources:
                        if resource.resource == resource_kind and resource.quantity >= 4:
                            option['cost'].append({'resource': resource_kind, 'amount': 4})
                            option['disabled'] = False
            options.append(option)
        options.append({'name': "Back"})
        super().__init__(None, options, False)

    def _draw_choice(self, i, offset):
        super()._draw_choice(i, offset)
        if i < len(RESOURCE_KINDS):
            ugfx.area(93, 1 + offset + self.menu_offset, 16, 16, RESOURCE_KINDS[i]['col'])


class NextPlayer(Menu):

    def __init__(self, team):
        super().__init__('Pass the badge to next team:', [team], False)


class GameOver(Menu):

    def __init__(self, team):
        super().__init__(['Game over!', 'Congrats to the winning team:'], [team], False)


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
                if self.resource != DESERT:
                    ugfx.text(round(self.centre[0] - text_offset), round(self.centre[1] - text_offset), "{} ".format(self.number['roll']), text_colour)


class Selectable:

    EMPTY = 0

    def __init__(self, data):
        # Screen coords that define the selectable object
        self.data = data

        # The list of hexes next to which this selectable object is adjacent
        self.hexes = []

        # What is built here and who owns it
        self.team = None
        self.contents = Selectable.EMPTY

        # Whether to draw selection indicator
        self.selected = False

    def is_empty(self):
        return self.contents == Selectable.EMPTY

    def set_selection(self, selected):
        self.selected = selected
        # Notify the surrounding hexes that they need to redraw themselves
        for h in self.hexes:
            h.changed = True


class Settlement(Selectable):
    """A node at which it is possible to build a settlement."""

    # Possible things this location may contain, the values here are the number of
    # victory points that the building is worth to the player who built it
    TOWN = 1
    CITY = 2

    def prob_score(self):
        """The probability score of the location is the sum of the probability of all adjacent hexes"""
        score = 0
        for h in self.hexes:
            score = score + h.number['prob']
        return score

    def build_town(self, team):
        assert self.contents == Selectable.EMPTY, 'Town can only be built in empty location'
        self.team = team
        self.contents = Settlement.TOWN

    def build_city(self, team):
        assert self.contents == Settlement.TOWN and self.team['name'] == team['name'], 'City can only be built in place of one of your own towns'
        self.contents = Settlement.CITY

    def draw(self):
        if self.contents == Settlement.TOWN:
            ugfx.fill_circle(self.data[0], self.data[1], 4, self.team['colour'])
            ugfx.circle(self.data[0], self.data[1], 4, ugfx.WHITE)
        elif self.contents == Settlement.CITY:
            ugfx.fill_circle(self.data[0], self.data[1], 8, self.team['colour'])
            ugfx.circle(self.data[0], self.data[1], 8, ugfx.WHITE)
        # A selection highlight
        if self.selected:
            # We can't draw circle primitives with thick lines, so need to draw it twice
            ugfx.circle(self.data[0], self.data[1], 10, ugfx.WHITE)
            ugfx.circle(self.data[0], self.data[1], 9, ugfx.WHITE)


class Road(Selectable):
    """An edge along which it is possible to build a road."""

    ROAD = 1

    def build_road(self, team):
        assert self.contents == Selectable.EMPTY, 'Road can only be built in empty location'
        self.team = team
        self.contents = Road.ROAD

    def draw(self):
        x0, y0 = (self.data[0][0], self.data[0][1])
        x1, y1 = (self.data[1][0], self.data[1][1])
        if self.contents == Road.ROAD:
            ugfx.thickline(x0, y0, x1, y1, ugfx.WHITE, 6, False)
            ugfx.thickline(x0, y0, x1, y1, self.team['colour'], 4, False)
        # A selection highlight
        if self.selected:
            # We can't draw a rectangle at an angle, so lets calculate the points for an
            # appropriate polygon manually for drawing the selection box...

            # Get the vector and a normal, we'll use the magnitude of the normal for the
            # width of the selection box, so make it half the size for a long narrow box
            vx, vy = (x1 - x0, y1 - y0)
            nx, ny = (int(vy / 2), -(int(vx / 2)))

            # Draw with an origin that is offset by half the width of the box to straddle
            # the two adjacent hexes
            x = x0 - int(nx / 2)
            y = y0 - int(ny / 2)

            # It would be more efficient to call polygon directly like this:
            #   ugfx.polygon(x, y, [[0, 0], [nx, ny], [vx + nx, vy + ny], [vx, vy]], ugfx.WHITE)
            # But we can't draw polygon primitives with thick lines, so draw them individually
            ugfx.thickline(x, y, x + nx, y + ny, ugfx.WHITE, 2, False)
            ugfx.thickline(x + nx, y + ny, x + nx + vx, y + ny + vy, ugfx.WHITE, 2, False)
            ugfx.thickline(x + nx + vx, y + ny + vy, x + vx, y + vy, ugfx.WHITE, 2, False)
            ugfx.thickline(x + vx, y + vy, x, y, ugfx.WHITE, 2, False)


class Resource():

    def __init__(self, resource):
        self.resource = resource
        self.quantity = 0

    def increment(self, num=1):
        self.quantity = self.quantity + num

    def decrement(self, num=1):
        self.quantity = self.quantity - num
        if self.quantity < 0:
            self.quantity = 0


class Player:
    """The player's hand of resource cards and their score and what not."""

    STATUS_ACTIONS_DICE = "menu = actions / # = roll dice "
    STATUS_ACTIONS = "menu = actions "
    STATUS_MOVE_ROBBER = "Move the robber! "
    STATUS_MUST_MOVE_ROBBER = "Robber MUST be moved! "
    STATUS_BUILD = "Select a build location. "
    STATUS_NO_BUILD = "No valid build locations. "

    def __init__(self, team, roads, settlements):
        # Player team details
        self.team = team

        # All the buildable game board locations
        self.roads = roads
        self.settlements = settlements

        # Player's hand of resources
        self.resources = []
        for kind in RESOURCE_KINDS:
            r = Resource(kind)
            self.resources.append(r)

        # Turn number
        self.turn = 0
        self.status = Player.STATUS_ACTIONS_DICE

    def score(self):
        points = 0
        for s in [x for x in self.settlements if x.team == self.team]:
            points = points + s.contents
        return points

    def increment_turn(self):
        self.turn = self.turn + 1
        self.status = Player.STATUS_ACTIONS_DICE

    def num_resources(self):
        """Total number of all resources the player has"""
        return sum([x.quantity for x in self.resources])

    def collect_starting(self):
        """Execute resource collection for our starting towns"""
        # Find the hexes adjacent to our settlements
        for s in [x for x in self.settlements if x.team == self.team]:
            for h in s.hexes:
                # Increment the appropriate resource
                for r in self.resources:
                    if r.resource == h.resource:
                        r.increment()

    def collect(self, num):
        """Execute resource collection or loss for a given dice roll"""
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
                            if r.resource == h.resource:
                                if s.contents == Settlement.TOWN:
                                    r.increment()
                                elif s.contents == Settlement.CITY:
                                    r.increment(2)

    def trade(self, buy_kind, sell_kind, sell_amount):
        """Executes a simple resource trade"""
        for r in self.resources:
            if r.resource == buy_kind:
                r.increment()
            if r.resource == sell_kind:
                r.decrement(sell_amount)

    def pay(self, cost):
        for c in cost:
            for r in self.resources:
                if c['resource'] == r.resource:
                    r.decrement(c['amount'])

    def build_road_candidates(self):
        """Return the list of all roads that are valid candidates for building"""
        candidates = []
        # Road segments that belong to us
        for r in [x for x in self.roads if x.team == self.team]:
            # Settlement spaces that these road segments connect
            for s in [x for x in self.settlements if x.data in r.data]:
                # Empty road segments connecting those settlement spaces
                for road in [x for x in self.roads if x.is_empty() and s.data in x.data]:
                    if road not in candidates:
                        candidates.append(road)
        return candidates

    def can_build_town_at(self, settlement):
        """Determines whether a town can be built at the given settlement according to proximity rules"""
        # Find the road segments connecting the given settlement
        for road in [x for x in self.roads if settlement.data in x.data]:
            # Get adjacent settlements (those at the other end of the road segments)
            for s in [x for x in self.settlements if x.data in road.data and x != settlement]:
                # If all adjacent settlements are empty, it means that we are at least two road
                # segments from any other built settlement, which is the required distance
                if not s.is_empty():
                    return False
        return True

    def build_town_candidates(self):
        """Return the list of all settlements that are valid candidates for towns to be built"""
        candidates = []
        # Road segments that belong to us
        for r in [x for x in self.roads if x.team == self.team]:
            # Empty settlement spaces at each end of the road segments
            for s in [x for x in self.settlements if x.is_empty() and x.data in r.data]:
                # Settlement is a candidate if we can build there
                if self.can_build_town_at(s) and s not in candidates:
                    candidates.append(s)
        return candidates

    def build_city_candidates(self):
        """Return the list of all settlements that are valid candidates for being upgraded to city"""
        candidates = []
        # Settlement spaces that belong to us and contain a town
        for s in [x for x in self.settlements if x.team == self.team and x.contents == Settlement.TOWN]:
            candidates.append(s)
        return candidates

    def draw(self):
        # Blank out the score in case it changed
        ugfx.area(60, 28, 25, 18, ugfx.BLACK)

        # Player's team and score
        ugfx.text(5, 8, "{} ".format(self.team['name']), self.team['colour'])
        ugfx.text(5, 28, "Points: {} ".format(self.score()), ugfx.WHITE)
        ugfx.text(5, 48, "Turn: {} ".format(self.turn), ugfx.WHITE)

        # Blank out the status/resource area
        ugfx.area(0, 275, 240, 50, ugfx.BLACK)

        # Status line
        ugfx.text(5, 275, self.status, ugfx.WHITE)

        # Player's resources
        offset = int(ugfx.width() / len(self.resources))
        square = int(offset / 3)
        for i in range(len(self.resources)):
            ugfx.area((offset * i) + 1, 295, square, 20, self.resources[i].resource['col'])
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
    MENU = 0

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

    # Interactivity modes for allowing the the user to navigate and select things on the game board
    ROBBER_MODE = 1
    ROAD_MODE = 2
    TOWN_MODE = 3
    CITY_MODE = 4

    def __init__(self, teams):
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
        self.robber_hex = self.get_robber_hex()

        # The mode that dictates how we are interpreting button presses
        self.interactive_mode = None

        # Generate lists of unique valid locations for building settlements and roads
        self.roads = []
        self.settlements = []
        for h in self.hexes:
            for edge in h.edges:
                already_got = False
                for r in self.roads:
                    if r.data == edge:
                        already_got = True
                        r.hexes.append(h)
                if not already_got:
                    r = Road(edge)
                    r.hexes.append(h)
                    self.roads.append(r)
            for node in h.nodes:
                already_got = False
                for s in self.settlements:
                    if s.data == node:
                        already_got = True
                        s.hexes.append(h)
                if not already_got:
                    s = Settlement(node)
                    s.hexes.append(h)
                    self.settlements.append(s)

        # Create a player for each team and give the team starting towns in the two settlements
        # with the highest probability score that not already taken
        # Each team gets a settlement in player order, then again but in reverse, so the last
        # player gets the first pick of the second settlements
        self.players = []
        for team in teams:
            self.players.append(Player(team, self.roads, self.settlements))
        self.player = self.players[-1]
        for team in teams:
            self.pick_starting_settlement(team)
        teams.reverse()
        for team in teams:
            self.pick_starting_settlement(team)
        teams.reverse()

        # Each player can now collect their starting resources
        for p in self.players:
            p.collect_starting()

        # The dice roller
        self.dice = Dice()

        # Cheat code counter
        self.cheat = 0

    def get_roads_for_settlement(self, settlement):
        """Return a list of roads that connect to the given settlement"""
        roads = []
        for road in self.roads:
            if settlement.data in road.data:
                roads.append(road)
        return roads

    def pick_starting_settlement(self, team):
        """Choose a starting settlement for the given team, and place a town and a connecting road there"""

        # Sort the settlements by highest dice roll probability
        sorted_settlements = sorted(self.settlements, key=lambda s: s.prob_score())
        sorted_settlements.reverse()

        # Build at the highest probability settlement that is still available
        for s in sorted_settlements:
            if s.is_empty() and self.player.can_build_town_at(s):
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
        Buttons.enable_interrupt(Buttons.BTN_Hash, self._button_callback)
        # For moving the robber and building selections
        Buttons.enable_interrupt(Buttons.JOY_Up, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Down, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Left, self._button_callback)
        Buttons.enable_interrupt(Buttons.JOY_Right, self._button_callback)
        # Cheat code button
        Buttons.enable_interrupt(Buttons.BTN_5, self._button_callback)

    def deinitialise(self):
        # Unregister callbacks
        Buttons.disable_interrupt(Buttons.BTN_Menu)
        Buttons.disable_interrupt(Buttons.BTN_A)
        Buttons.disable_interrupt(Buttons.BTN_B)
        Buttons.disable_interrupt(Buttons.BTN_Hash)
        # For moving the robber and building selections
        Buttons.disable_interrupt(Buttons.JOY_Up)
        Buttons.disable_interrupt(Buttons.JOY_Down)
        Buttons.disable_interrupt(Buttons.JOY_Left)
        Buttons.disable_interrupt(Buttons.JOY_Right)
        # Cheat code button
        Buttons.disable_interrupt(Buttons.BTN_5)

        # Ensure all hexes are drawn next time we enter this state
        for h in self.hexes:
            h.changed = True

    def _button_callback(self, btn):
        if not self.interactive_mode:
            if btn == Buttons.BTN_Menu:
                self.selection = GameBoard.MENU
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
                    # All players collect resources corresponding with the dice roll
                    for p in self.players:
                        p.collect(num)
                    # Activate the robber on a seven
                    if num == 7:
                        self.interactive_mode = GameBoard.ROBBER_MODE
                        self.player.status = Player.STATUS_MOVE_ROBBER
                    else:
                        self.player.status = Player.STATUS_ACTIONS
                    self.redraw = True
            # Cheat code to get more resources for testing
            if btn == Buttons.BTN_5 and TEST_MODE:
                self.cheat = self.cheat + 1
                if self.cheat == 5:
                    self.cheat = 0
                    for r in self.player.resources:
                        r.increment(5)
                    self.redraw = True
        elif self.interactive_mode == GameBoard.ROBBER_MODE:
            h_current = self.get_robber_hex()
            if btn == Buttons.BTN_A:
                self.redraw = True
                # The robber may not stay in the same hex, ensure it moved
                if h_current != self.robber_hex:
                    self.robber_hex = h_current
                    self.robber_hex.set_highlight(False)
                    self.interactive_mode = None
                    self.player.status = Player.STATUS_ACTIONS
                    # TODO: Steal a card from a player at this hex
                else:
                    self.player.status = Player.STATUS_MUST_MOVE_ROBBER
            if btn == Buttons.JOY_Up:
                self._move_robber(h_current, 4)
            if btn == Buttons.JOY_Down:
                self._move_robber(h_current, 1)
            if btn == Buttons.JOY_Left:
                self._move_robber(h_current, 0 if h_current.coords[0] % 2 == 0 else 5)
            if btn == Buttons.JOY_Right:
                self._move_robber(h_current, 2 if h_current.coords[0] % 2 == 0 else 3)
        elif self.interactive_mode in (GameBoard.ROAD_MODE, GameBoard.TOWN_MODE, GameBoard.CITY_MODE):
            if btn == Buttons.BTN_A:
                for candidate in self.build_candidates:
                    if candidate.selected:
                        # Build a road on the selected road segment
                        if self.interactive_mode == GameBoard.ROAD_MODE:
                            candidate.build_road(self.player.team)
                        # Build a town on the selected settlement
                        if self.interactive_mode == GameBoard.TOWN_MODE:
                            candidate.build_town(self.player.team)
                        # Upgrade a town on the selected settlement to a city
                        if self.interactive_mode == GameBoard.CITY_MODE:
                            candidate.build_city(self.player.team)
                        candidate.set_selection(False)
                self.player.pay(self.build_cost)
                self.interactive_mode = None
                self.redraw = True
                if self.dice.total():
                    self.player.status = Player.STATUS_ACTIONS
                else:
                    self.player.status = Player.STATUS_ACTIONS_DICE
            if btn == Buttons.JOY_Left or btn == Buttons.JOY_Up:
                self._select_prev_build_candidate(self.build_candidates)
            if btn == Buttons.JOY_Right or btn == Buttons.JOY_Down:
                self._select_next_build_candidate(self.build_candidates)

    def _move_robber(self, h_current, direction):
        coords = Hex.get_neighbouring_hex_coords(h_current.coords, direction)
        h_next = self.get_hex_for_coords(coords)
        self.move_robber(h_current, h_next)
        self.redraw = True

    def _select_prev_build_candidate(self, candidates):
        if len(candidates) > 1:
            for i in range(len(candidates)):
                if candidates[i].selected:
                    candidates[i].set_selection(False)
                    if i == 0:
                        candidates[len(candidates) - 1].set_selection(True)
                    else:
                        candidates[i - 1].set_selection(True)
                    break
        self.redraw = True

    def _select_next_build_candidate(self, candidates):
        if len(candidates) > 1:
            for i in range(len(candidates)):
                if candidates[i].selected:
                    candidates[i].set_selection(False)
                    if i == len(candidates) - 1:
                        candidates[0].set_selection(True)
                    else:
                        candidates[i + 1].set_selection(True)
                    break
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
        """Called from the state machine to reset the board for the next player"""
        for i in range(len(self.players)):
            if self.player == self.players[i]:
                if i + 1 == len(self.players):
                    self.player = self.players[0]
                else:
                    self.player = self.players[i + 1]
                break
        self.player.increment_turn()
        self.dice.reset()
        for h in self.hexes:
            h.set_highlight(False)

    def build_mode(self, mode, cost):
        """Called from the state machine to enter building selection mode"""
        if mode == GameBoard.ROAD_MODE:
            self.build_candidates = self.player.build_road_candidates()
        if mode == GameBoard.TOWN_MODE:
            self.build_candidates = self.player.build_town_candidates()
        if mode == GameBoard.CITY_MODE:
            self.build_candidates = self.player.build_city_candidates()
        if self.build_candidates:
            self.build_candidates[0].set_selection(True)
            self.build_cost = cost
            self.interactive_mode = mode
            self.player.status = Player.STATUS_BUILD
        else:
            self.player.status = Player.STATUS_NO_BUILD


class Settlers:
    """A lean mean state machine"""

    # Game states
    EXIT = 0
    MAIN_MENU = 1
    TEAM_MENU = 2
    GAME = 3
    ACTION_MENU = 4
    ACTION_TRADE_MENU = 5
    ACTION_BUILD_MENU = 6
    ACTION_END_TURN = 7

    def __init__(self):
        self.old_state = None
        self.state = Settlers.MAIN_MENU
        self.game = None
        self.teams = []

    def enter_state(self, state):
        self.old_state = self.state
        self.state = state

    def run(self):
        while self.state != Settlers.EXIT:

            if self.state == Settlers.MAIN_MENU:
                menu = MainMenu(self.game is None, self.old_state != Settlers.TEAM_MENU and self.old_state != Settlers.ACTION_END_TURN)
                x = menu.run()
                if x == MainMenu.NEW_GAME:
                    self.teams = []
                    self.enter_state(Settlers.TEAM_MENU)
                if x == MainMenu.CONTINUE_GAME:
                    self.enter_state(Settlers.GAME)
                if x == MainMenu.EXIT:
                    self.enter_state(Settlers.EXIT)

            elif self.state == Settlers.TEAM_MENU:
                menu = TeamMenu(self.teams)
                x = menu.run()
                if x <= TeamMenu.TEAM_MAX:
                    self.teams.append(menu.get_selected_choice())
                    if len(self.teams) >= 4:
                        x = TeamMenu.START_GAME
                if x == TeamMenu.BACK:
                    self.enter_state(Settlers.MAIN_MENU)
                if x == TeamMenu.START_GAME:
                    self.game = GameBoard(self.teams)
                    self.game.next_player()
                    self.enter_state(Settlers.GAME)

            elif self.state == Settlers.GAME:
                x = self.game.run()
                if x == GameBoard.MENU:
                    self.enter_state(Settlers.ACTION_MENU)

            elif self.state == Settlers.ACTION_MENU:
                menu = ActionMenu(self.game.dice.total(), self.old_state != Settlers.ACTION_BUILD_MENU and self.old_state != Settlers.ACTION_TRADE_MENU)
                x = menu.run()
                if x == ActionMenu.BUILD:
                    self.enter_state(Settlers.ACTION_BUILD_MENU)
                if x == ActionMenu.TRADE:
                    self.enter_state(Settlers.ACTION_TRADE_MENU)
                if x == ActionMenu.END_TURN:
                    self.enter_state(Settlers.ACTION_END_TURN)
                if x == ActionMenu.EXIT_GAME:
                    self.enter_state(Settlers.MAIN_MENU)
                if x == ActionMenu.BACK:
                    self.enter_state(Settlers.GAME)

            elif self.state == Settlers.ACTION_BUILD_MENU:
                menu = BuildMenu(self.game.player.resources)
                x = menu.run()
                if x == BuildMenu.BACK:
                    self.enter_state(Settlers.ACTION_MENU)
                else:
                    choice = menu.get_selected_choice()
                    if x == BuildMenu.ROAD:
                        self.game.build_mode(GameBoard.ROAD_MODE, choice['cost'])
                    if x == BuildMenu.TOWN:
                        self.game.build_mode(GameBoard.TOWN_MODE, choice['cost'])
                    if x == BuildMenu.CITY:
                        self.game.build_mode(GameBoard.CITY_MODE, choice['cost'])
                    self.enter_state(Settlers.GAME)

            elif self.state == Settlers.ACTION_TRADE_MENU:
                menu = TradeMenu(self.game.player.resources)
                x = menu.run()
                if x == TradeMenu.BACK:
                    self.enter_state(Settlers.ACTION_MENU)
                else:
                    trade_choice = menu.get_selected_choice()
                    # TODO: ask user which resource to trade when they have >= 4 of more than one kind of resource
                    # TODO: for now, just trade the first one in the cost list
                    cost = trade_choice['cost'][0]
                    self.game.player.trade(trade_choice['resource'], cost['resource'], cost['amount'])
                    self.enter_state(Settlers.GAME)

            elif self.state == Settlers.ACTION_END_TURN:
                if self.game.player.score() >= 10:
                    menu = GameOver(self.game.player.team)
                    menu.run()
                    self.game = None
                    self.enter_state(Settlers.MAIN_MENU)
                else:
                    self.game.next_player()
                    menu = NextPlayer(self.game.player.team)
                    menu.run()
                    self.enter_state(Settlers.GAME)

        # User chose exit, a machine reset is the easiest way :-)
        restart_to_default()


game = Settlers()
game.run()
