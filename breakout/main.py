"""Breakout!"""

___name___         = "Breakout"
___license___      = "MIT"
___categories___   = ["Games"]
___dependencies___ = ["app", "ugfx_helper", "random", "buttons"]

from tilda import Buttons
import ugfx, ugfx_helper, dialogs
import time
import app
import random
import math

background_colour = ugfx.BLACK
framerate = 60

SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320

class Ball:

    def __init__(self, x = 5.0, y = 5.0, dx = 2, dy = 2):
        self.colour = ugfx.WHITE
        self.diameter = 4
        self.x = x
        self.y = y
        self.dy = dx
        self.dx = dy
    
    def centerX(self):
        return self.x + self.diameter / 2
    
    def centerY(self):
        return self.y + self.diameter / 2
    
    def left(self):
        return self.x
    
    def right(self):
        return self.x + self.diameter
    
    def top(self):
        return self.y
    
    def bottom(self):
        return self.y + self.diameter
    
    def draw(self):
        ugfx.fill_ellipse(int(self.x), int(self.y), self.diameter, self.diameter, self.colour)

    def clear(self):
        ugfx.fill_ellipse(int(self.x), int(self.y), self.diameter, self.diameter, background_colour)

    def bounceX(self):
        self.dx *= -1

    def bounceY(self):
        self.dy *= -1
    
    def bounceUpwards(self, ratioFromMiddle):
        speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
        self.dx = math.sin(ratioFromMiddle) * speed
        self.dy = math.cos(ratioFromMiddle) * speed * -1

    def tick(self):
        self.x += self.dx
        self.y += self.dy

        if self.x < 0 or self.x + self.diameter > SCREEN_WIDTH:
            self.bounceX()

        if self.y < 0 or self.y + self.diameter > SCREEN_HEIGHT:
            self.bounceY()

    def hasCollidedWith(self, item):
        return self.right() >= item.left() and self.left() <= item.right() and self.top() <= item.bottom() and self.bottom() >= item.top()
    
    def isHorizontalCollision(self, item):
        return self.centerY() >= item.top() and self.centerY() <= item.bottom()

    def isVerticalCollision(self, item):
        return self.centerX() >= item.left() and self.centerX() <= item.right()

    def hasHitTop(self, item):
        return self.y + self.diameter >= item.top()
    
    def horizontalPositionFromMiddle(self, item):
        return min(1, max(0, (self.centerX() - item.left()) / (item.right() - item.left()))) - 1

class Paddle:

    def __init__(self, x = SCREEN_WIDTH / 2, width = SCREEN_WIDTH // 4, dx = 10):
        self.x = x
        self.dx = dx
        self.width = width
        self.height = 4
        self.colour = ugfx.WHITE

    def left(self):
        return self.x - self.width / 2

    def right(self):
        return self.x + self.width / 2

    def top(self):
        return self.bottom() - self.height
    
    def bottom(self):
        return SCREEN_HEIGHT
    
    def draw(self):
        ugfx.area(int(self.left()), int(self.top()), self.width, self.height, self.colour)

    def clear(self):
        ugfx.area(int(self.left()), int(self.top()), self.width, self.height, background_colour)

    def tick(self):
        if Buttons.is_pressed(Buttons.JOY_Right) and self.right() < SCREEN_WIDTH:
            self.x += self.dx
        if Buttons.is_pressed(Buttons.JOY_Left) and self.left() > 0:
            self.x -= self.dx

class Block:

    def __init__(self, x, y, width, height, colour = ugfx.WHITE):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.visible = True
    
    def left(self):
        return self.x
    
    def right(self):
        return self.x + self.width
    
    def top(self):
        return self.y
    
    def bottom(self):
        return self.y + self.height
    
    def draw(self):
        colour = self.colour if self.visible else background_colour
        ugfx.area(int(self.left()), int(self.top()), self.width, self.height, colour)
    
    def clear(self):
        ugfx.area(int(self.left()), int(self.top()), self.width, self.height, background_colour)

    def hide(self):
        self.visible = False
        self.clear()


# Clear LEDs
leds = Neopix()
leds.display([0,0,0])
leds.display([0,0,0])

ugfx_helper.init()
ugfx.clear(background_colour)

def randomColour():
    return random.randint(0, 0xffffff)

def gameEnd(score):
    ugfx.text(5, 5, str(score) + ' POINTS!!!', ugfx.WHITE)
    for i in range(0, 10):
        leds.display([randomColour(), 0])
        time.sleep(0.1)
        leds.display([0, randomColour()])
        time.sleep(0.1)
    leds.display([0, 0])
    time.sleep(1)

def gameOver(score):
    ugfx.text(5, 5, 'GAME OVER', ugfx.WHITE)
    ugfx.text(5, 30, str(score) + ' points', ugfx.WHITE)
    for i in range(0, 5):
        leds.display([0xff0000, 0])
        time.sleep(0.2)
        leds.display([0, 0xff0000])
        time.sleep(0.2)
    leds.display([0, 0])
    time.sleep(1)

def runGame():
    paddle = Paddle()
    direction = random.random() - 0.5
    initial_speed_up = 4
    ball = Ball(x = SCREEN_WIDTH / 2, y = SCREEN_HEIGHT / 2, dx = math.cos(direction) * initial_speed_up, dy = math.sin(direction) * initial_speed_up)
    blocks = \
        [Block(x = x, y = 30, width = 36, height = 10, colour = ugfx.RED) for x in range(24, SCREEN_WIDTH - 24, 40)] + \
        [Block(x = x, y = 44, width = 36, height = 10, colour = ugfx.GREEN) for x in range(24, SCREEN_WIDTH - 24, 40)] + \
        [Block(x = x, y = 58, width = 36, height = 10, colour = ugfx.BLUE) for x in range(24, SCREEN_WIDTH - 24, 40)] + \
        [Block(x = x, y = 72, width = 36, height = 10, colour = ugfx.YELLOW) for x in range(24, SCREEN_WIDTH - 24, 40)] + \
        [Block(x = x, y = 86, width = 36, height = 10, colour = ugfx.ORANGE) for x in range(24, SCREEN_WIDTH - 24, 40)]

    def invisibleBlocks():
        return [block for block in blocks if not(block.visible)]

    for block in blocks:
        block.draw()
    while True:
        paddle.draw()
        ball.draw()
        time.sleep(1.0 / framerate)
        paddle.clear()
        ball.clear()
        paddle.tick()
        ball.tick()
        if Buttons.is_pressed(Buttons.BTN_Menu):
            gameRunning = False
        if all([not(block.visible) for block in blocks]):
            gameEnd(score = 50 + len(invisibleBlocks()))
            break
        if ball.hasHitTop(paddle):
            if ball.hasCollidedWith(paddle):
                ball.bounceUpwards(ball.horizontalPositionFromMiddle(paddle))
            else:
                gameOver(score = len(invisibleBlocks()))
                break
        for block in blocks:
            if block.visible and ball.hasCollidedWith(block):
                block.hide()
                if ball.isHorizontalCollision(block):
                    ball.bounceX()
                if ball.isVerticalCollision(block):
                    ball.bounceY()
        
runGame()
app.restart_to_default()
