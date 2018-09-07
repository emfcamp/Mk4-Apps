"""Pong!"""

___name___         = "Pong"
___license___      = "WTFPL"
___categories___   = ["Games"]
___dependencies___ = ["dialogs", "app", "ugfx_helper", "sleep", "buttons"]

import math, ugfx, ugfx_helper, random, sleep, buttons, time
from tilda import Buttons

ugfx_helper.init()

SCREEN_WIDTH = ugfx.width()
SCREEN_HEIGHT = ugfx.height()

bgColor = ugfx.BLACK
ballColor = ugfx.html_color(0x00FF00)
paddleColor = ugfx.html_color(0x00FF00)
netColor = ugfx.html_color(0x00FF00)

class Paddle():
    height = 6
    width = 60

    moveSpeed = 4

    needsRedraw = True

    def __init__(self, type):
        self.type = type

        self.x = SCREEN_WIDTH/2
        self.previousX = self.x

        if type == 0:
            self.y = self.height/2
        else:
            self.y = SCREEN_HEIGHT - (self.height/2)

    def draw(self):
        if self.needsRedraw:
            ugfx.area(int(self.previousX-self.width/2),int(self.y-self.height/2),int(self.width),int(self.height),bgColor)
            self.needsRedraw = False

        ugfx.area(int(self.x-self.width/2),int(self.y-self.height/2),int(self.width),int(self.height),paddleColor)

    def update(self):
        if self.type == 1:
            if Buttons.is_pressed(Buttons.BTN_Hash):
                self.needsRedraw = True
                self.previousX = self.x
                self.x += self.moveSpeed

            if Buttons.is_pressed(Buttons.BTN_Star):
                self.needsRedraw = True
                self.previousX = self.x
                self.x -= self.moveSpeed
        if self.type == 0:
            if Buttons.is_pressed(Buttons.BTN_3):
                self.needsRedraw = True
                self.previousX = self.x
                self.x += self.moveSpeed
            if Buttons.is_pressed(Buttons.BTN_1):
                self.needsRedraw = True
                self.previousX = self.x
                self.x -= self.moveSpeed

        if self.x + self.width/2 > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width/2

        if self.x -self.width/2 < 0:
            self.x = self.width/2

class Ball():
    size = 10

    x = 0
    y = 0

    yDeathOffset = 5+3

    def __init__(self):
        self.x = random.randint(30,SCREEN_WIDTH-30)

        self.y = SCREEN_HEIGHT/2

        self.vX = 3

        if random.randrange(2) == 1:
            self.vY = 3
        else:
            self.vY = -3

        self.previousX = self.x
        self.previousY = self.y

        self.dead = False

    def draw(self):
        ugfx.area(int(self.previousX-self.size/2),int(self.previousY-self.size/2),int(self.size),int(self.size),bgColor)
        ugfx.area(int(self.x-self.size/2),int(self.y-self.size/2),int(self.size),int(self.size),ballColor)

    def update(self, topPaddle, bottomPaddle):
        self.previousX = self.x
        self.previousY = self.y

        self.x += self.vX
        self.y += self.vY

        if self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH
            self.vX = -self.vX

        if self.x < 0:
            self.x = 0
            self.vX = -self.vX

        if self.y > (SCREEN_HEIGHT - self.yDeathOffset):
            if (self.x > (bottomPaddle.x - bottomPaddle.width/2)) and (self.x < (bottomPaddle.x + bottomPaddle.width/2)):
                self.y = SCREEN_HEIGHT - self.yDeathOffset
                self.vY = -self.vY
                bottomPaddle.needsRedraw = True
            else:
                self.dead = True


        if self.y < self.yDeathOffset:
            if (self.x > (topPaddle.x - topPaddle.width/2)) and (self.x < (topPaddle.x + topPaddle.width/2)):
                self.y = self.yDeathOffset
                self.vY = -self.vY
                topPaddle.needsRedraw = True
            else:
                self.dead = True

    def isDead(self):
        return self.dead

def one_round():
    ball = Ball()
    topPaddle = Paddle(0)
    bottomPaddle = Paddle(1)

    ugfx.clear(bgColor)
    ugfx.backlight(100)

    ugfx.set_default_font(ugfx.FONT_TITLE)

    while True:
        topPaddle.update()
        bottomPaddle.update()
        ball.update(topPaddle, bottomPaddle)

        if ball.isDead():
            if(ball.y > SCREEN_HEIGHT/2):
                return [1,0]
            else:
                return [0,1]

        topPaddle.draw()
        bottomPaddle.draw()
        ball.draw()

        #draw the net
        for i in range(0,7):
            ugfx.area(int(i*2*SCREEN_WIDTH/13), int(SCREEN_HEIGHT/2-1), int(SCREEN_WIDTH/13), 3, netColor)

        ugfx.orientation(0)
        ugfx.text(130, 0, "%d " % (points[0]),netColor)
        ugfx.text(170, 0, "%d " % (points[1]),netColor)
        ugfx.orientation(270)

        time.sleep_ms(1)

minScore = 9

points = [0,0]
playing = 1
while playing:
    points[0] = 0
    points[1] = 0

    while (points[0] < minScore) and (points[1] < minScore):
        score = one_round()

        points[0] = points[0] + score[0]
        points[1] = points[1] + score[1]

    ugfx.area(0,0,ugfx.width(),ugfx.height(),0)

    ugfx.orientation(90)
    ugfx.set_default_font(ugfx.FONT_TITLE)
    ugfx.text(30, 138, "GAME ",ballColor)
    ugfx.text(30, 158, "OVER ",ballColor)

    ugfx.set_default_font(ugfx.FONT_SMALL)
    ugfx.text(70, 220, "Score: %d - %d " % (points[0], points[1]), ballColor)
    ugfx.text(36, 260, "Press A to play again ", ballColor)
    ugfx.text(40, 280, "Press MENU to quit " , ballColor)

    ugfx.orientation(270)
    ugfx.set_default_font(ugfx.FONT_TITLE)
    ugfx.text(30, 138, "GAME ",ballColor)
    ugfx.text(30, 158, "OVER ",ballColor)

    ugfx.set_default_font(ugfx.FONT_SMALL)
    ugfx.text(70, 220, "Score: %d - %d " % (points[1], points[0]), ballColor)
    ugfx.text(36, 260, "Press A to play again ", ballColor)
    ugfx.text(40, 280, "Press MENU to quit ", ballColor)

    while True:
        sleep.wfi()
        if buttons.is_triggered(Buttons.BTN_A):
            break

        if buttons.is_triggered(Buttons.BTN_Menu):
            playing = 0
            break

app.restart_to_default()

