# Term project deliverable 2
# Daniel Wen (lanhaow)
# 15-112 Section L

import pygame
from pygamegame import PygameGame
from ball import Ball
from texttools import drawText, Menu
from maps import Maps
from terrain import Terrain
from progress import Progress
from stopwatch import Stopwatch

class Struct(object):
    pass

class Game(PygameGame):
    def __init__(self):
        width = 800
        height = 500
        fps = 40
        fullCh = 255
        bgColor = (fullCh, fullCh, fullCh)
        title = "Bouncy Bouncy Revamped"
        super().__init__(width, height, fps, title, bgColor)

    def initStyles(self):
        assert(pygame.font.get_init())
        assert(pygame.image.get_extended())
        self.font = Struct()
        textSize = 16
        self.font.text = pygame.font.SysFont("Arial", textSize)
        titleSize = 30
        self.font.title = pygame.font.SysFont("Arial", titleSize)
        self.font.titleEmph = pygame.font.SysFont("Arial", titleSize,
            bold=True, italic=True)
        self.margin = 10

    def initMaps(self):
        self.maps = Maps(self.margin + 100, self.margin,
            self.width - 2*self.margin, self.height - 2*self.margin)
        self.progress = Progress(self.maps.levels, self)

    def initMainMenu(self):
        top = 130
        left = 80
        entries = ["Play", "Level select", "Instructions", "Turn sound off"]
        actions = [self.playLevel, self.doLevelMenu,
            self.doHelp, self.toggleSound]
        self.mainMenu = Menu(left, top, entries, actions)

    def initLevelMenu(self):
        top = 60
        left = 130
        entries = []
        actions = []
        for i, level in enumerate(self.maps.levels):
            prevLevel = self.maps.levels[i - 1]
            if i > 0 and self.progress[prevLevel]["score"] == None:
                entries.append("Level %s    Locked" % level)
                actions.append(None)
                continue
            elif self.progress[level]["score"] == None:
                entries.append("Level %s    Unlocked" % level)
            else:
                entries.append("Level %s    Highscore: %d    Best time: %s" %
                    (level, self.progress[level]["score"],
                        Stopwatch.secToMin(self.progress[level]["time"])))
            # Locally scope level
            actions.append(lambda level=level: self.playLevel(level))
        entries += ["Return to main menu", "Clear progress"]
        actions += [self.doMainMenu, self.progress.clear]
        self.levelMenu = Menu(left, top, entries, actions)

    def initPauseMenu(self):
        def play():
            self.mode = "play"
        top = 200
        left = 300
        width = 140
        height = 80
        entries = ["Continue", "Main menu", "Turn sound off"]
        actions = [play,
                   self.doMainMenu,
                   self.toggleSound]
        self.pauseMenu = Menu(left, top, entries, actions)
        background = pygame.Surface((width + self.margin, height + self.margin))
        background.fill(self.bgColor)
        pygame.draw.rect(background, (0, 0, 0), background.get_rect(), 2)
        self.pauseMenu.background = background

    def initMenus(self):
        self.initMainMenu()
        self.initLevelMenu()
        self.initPauseMenu()

    def init(self):
        self.initStyles()
        self.initMaps()
        Terrain.initImages()
        Terrain.initSounds()
        self.initMenus()
        self.stopwatch = Stopwatch()
        self.initHelp()
        self.mode = "menu"
        self.menu = self.mainMenu

    def loadLevel(self):
        terrain, self.startpos = self.maps.load(self.level)
        self.terrain = pygame.sprite.Group(*terrain)
        self.ball = Ball(*self.startpos)
        self.score = 0
        self.stopwatch.restart()
        highscore = self.progress[self.level]["score"]
        self.highscoreText = str(highscore) if highscore != None else "---"
        bestTime = self.progress[self.level]["time"]
        if bestTime != None:
            self.bestTimeText = Stopwatch.secToMin(bestTime)
        else:
            self.bestTimeText = "---"

    def nextLevel(self):
        # Update and save progress
        saved = self.progress[self.level]
        if saved["score"] == None or self.score > saved["score"]:
            saved["score"] = self.score
        duration = self.stopwatch.getSeconds()
        if saved["time"] == None or duration < saved["time"]:
            saved["time"] = duration
        self.progress.save()
        # Load next level
        Terrain.playSound("happy")
        index = self.maps.levels.index(self.level) + 1
        if index >= len(self.maps.levels):
            self.mode = "win"
        else:
            self.level = self.maps.levels[index]
            self.loadLevel()

    def initGame(self, level):
        self.level = level
        self.loadLevel()

    def killBall(self):
        Terrain.playSound("sad")
        self.loadLevel()

    def keyPressed(self, keyCode, modifier):
        #print(keyCode)
        if self.mode == "menu":
            self.menu.key(keyCode)
        elif self.mode == "play":
            if keyCode == 27:
                self.mode = "pause"
                self.menu = self.pauseMenu
        elif self.mode == "pause":
            self.menu.key(keyCode)
            if keyCode == 27:
                self.mode = "play"
        elif self.mode == "levelMenu":
            self.menu.key(keyCode)
            if keyCode == 27:
                self.mode = "menu"
                self.menu = self.mainMenu
        elif self.mode == "win":
            if keyCode == 13:
                self.mode = "menu"
        elif self.mode == "help":
            if keyCode == 27:
                self.mode = "menu"

    def ballFly(self, ball, cannon):
        ball.flying = True
        ball.vy = 0
        ball.vx = cannon.direction*ball.flyvx
        # Reposition the ball
        ball.y = cannon.y + ball.realR
        if cannon.direction > 0:
            ball.x = cannon.x + cannon.width + ball.realR
        else:
            ball.x = cannon.x - ball.realR

    def timerFiredPlay(self):
        if (self.ball.x < self.maps.left
                or self.ball.x > self.maps.left + self.maps.width or
                self.ball.y < self.maps.top
                or self.ball.y > self.maps.top + self.maps.height):
            # Ball off map
            self.killBall()

        collided = pygame.sprite.spritecollide(self.ball, self.terrain, False,
            Terrain.collidedFn)
        if len(collided) > 0:
            elements = Terrain.manageCollision(self.ball, collided)
            for element, direction in elements:
                result = element.interactFromDir(self.ball, direction)
                if result == "score":
                    self.score += element.points
                elif result == "win":
                    self.nextLevel()
                elif result == "fly":
                    self.ballFly(self.ball, element)
                elif result == "kill":
                    self.killBall()

        self.ball.update(self.isKeyPressed)

    def timerFired(self, dt):
        if self.mode == "play":
            self.timerFiredPlay()
            self.stopwatch.tick(dt)

    def drawMenu(self, screen):
        titleTop = 70
        titleLeft = 60
        x = drawText(screen, titleLeft, titleTop,
            text="Bouncy Bouncy ", font=self.font.title, anchor="nw")
        space = 8
        drawText(screen, x + space, titleTop, text="Revamped",
            font=self.font.titleEmph, anchor="nw")
        self.mainMenu.draw(screen, self.font.text)

    def drawGame(self, screen):
        self.terrain.draw(screen)
        self.ball.draw(screen)
        pos = 30
        drawText(screen, self.margin, pos,
            text="Level %s" % self.level, font=self.font.text, anchor="nw")
        pos = 80
        drawText(screen, self.margin, pos,
            text="Score: %d" % self.score, font=self.font.text, anchor="nw")
        pos = 110
        drawText(screen, self.margin, pos, text="Highscore:",
            font=self.font.text, anchor="nw")
        pos = 130
        drawText(screen, self.margin, pos, text=self.highscoreText,
            font=self.font.text, anchor="nw")
        self.drawGameTime(screen)

    def drawGameTime(self, screen):
        pos = 180
        drawText(screen, self.margin, pos,
            text=str(self.stopwatch), font=self.font.text, anchor="nw")
        pos = 210
        drawText(screen, self.margin, pos, text="Best time:",
            font=self.font.text, anchor="nw")
        pos = 230
        drawText(screen, self.margin, pos, text=self.bestTimeText,
            font=self.font.text, anchor="nw")

    def drawPause(self, screen):
        screen.blit(self.pauseMenu.background,
            (self.pauseMenu.x - self.margin, self.pauseMenu.y - self.margin))
        self.pauseMenu.draw(screen, self.font.text)

    def drawLevelMenu(self, screen):
        titleTop = 60
        titleLeft = 30
        drawText(screen, titleLeft, titleTop,
            text="Level select", font=self.font.text, anchor="nw")
        self.levelMenu.draw(screen, self.font.text)

    def drawWin(self, screen):
        space = 24
        screen.blit(self.pauseMenu.background,
            (self.pauseMenu.x - self.margin, self.pauseMenu.y - self.margin))
        drawText(screen, self.pauseMenu.x, self.pauseMenu.y,
            text="Congratulations!", font=self.font.text, anchor="nw")
        drawText(screen, self.pauseMenu.x, self.pauseMenu.y + space,
            text="Press Enter...", font=self.font.text, anchor="nw")

    def drawHelp(self, screen):
        top = 50
        left = 40
        drawText(screen, left, top,
            text="Instructions", font=self.font.text, anchor="nw")
        top = 80
        lineHeight = 24
        for line, text in enumerate(self.helpText):
            drawText(screen, left, top + line*lineHeight,
                text=text, font=self.font.text, anchor="nw")
        top = 350
        drawText(screen, left, top, text="Press Escape now for the main menu",
            font=self.font.text, anchor="nw")

    def redrawAll(self, screen):
        if self.mode == "menu":
            self.drawMenu(screen)
        elif self.mode == "play":
            self.drawGame(screen)
        elif self.mode == "pause":
            self.drawGame(screen)
            self.drawPause(screen)
        elif self.mode == "levelMenu":
            self.drawLevelMenu(screen)
        elif self.mode == "win":
            self.drawGame(screen)
            self.drawWin(screen)
        elif self.mode == "help":
            self.drawHelp(screen)

    def playLevel(self, level="1"):
        self.mode = "play"
        self.initGame(level)

    def doMainMenu(self):
        self.mode = "menu"
        self.menu = self.mainMenu

    def doLevelMenu(self):
        self.mode = "levelMenu"
        self.initLevelMenu()
        self.menu = self.levelMenu

    def doHelp(self):
        self.mode = "help"

    def toggleSound(self):
        if Terrain.soundsOn:
            Terrain.soundsOn = False
            return "sound off"
        else:
            Terrain.soundsOn = True
            return "sound on"

    def initHelp(self):
        self.helpText = ["Use Left/Right arrow keys to move.",
            "Avoid pits and spikes.",
            "Hold both Left/Right arrow keys to wall jump!",
            "Cannons make you fly. Hit the opposite arrow key to stop flying.",
            "Press Escape in game to pause."]

Game().run()
