# Terrain elements

import pygame

class Terrain(pygame.sprite.Sprite):
    soundsOn = True

    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.canCollide = True

    @staticmethod
    def initImages():
        margin = 1
        size = 50
        images = {"Bomb" : "img/spike.png",
                  "Rubble" : "img/cracked.png",
                  "Trampoline" : "img/trampoline.png",
                  "Exit" : "img/exit.png",
                  "Cannon" : "img/cannon.png",
                  "CannonLeft" : "img/cannonleft.png"}
        Terrain.images = {}
        for image in images:
            path = images[image]
            data = pygame.image.load(path)
            Terrain.images[image] = data.convert_alpha().subsurface(
                (margin, margin, size, size))

    @staticmethod
    def initSounds():
        sounds = {"bounce" : "sound/bounce.wav",
                  "boing" : "sound/boing.wav",
                  "whoosh" : "sound/whoosh.wav",
                  "smash" : "sound/smash.wav",
                  "ninja" : "sound/ninja.wav",
                  "happy" : "sound/happy.wav",
                  "sad" : "sound/sad.wav"}
        Terrain.sounds = {}
        for sound in sounds:
            path = sounds[sound]
            Terrain.sounds[sound] = pygame.mixer.Sound(path)

    @staticmethod
    def getClassFromCode(code):
        codes = {"w" : Wall,
                 "f" : Finish,
                 "x" : Exit,
                 "r" : Rubble,
                 "c" : Cannon,
                 "C" : CannonLeft,
                 "t" : Trampoline,
                 "b" : Bomb}
        return codes[code]

    @staticmethod
    def collidedFn(ball, element):
        if element.canCollide:
            return pygame.sprite.collide_rect(ball, element)
        return False

    @staticmethod
    def collideSingle(ball, element):
        dirDists = {
            # Distance from ball center to edge of element
            "left" : element.x - ball.x,
            "top" : element.y - ball.y,
            "right" : ball.x - (element.x + element.width),
            "bottom" : ball.y - (element.y + element.height)
        }
        bestDirection = None
        # Find direction with greatest distance
        for direction in dirDists:
            if (bestDirection == None or
                    dirDists[direction] > dirDists[bestDirection]):
                bestDirection = direction
        return element, bestDirection

    @staticmethod
    def collideDouble(ball, elements):
        if elements[0].x == elements[1].x:
            # Vertical pair
            if (abs(elements[0].rect.centery - ball.y) <
                    abs(elements[1].rect.centery - ball.y)):
                element = elements[0]
            else:
                element = elements[1]
            if ball.x < elements[0].rect.centerx:
                direction = "left"
            else:
                direction = "right"
        elif elements[0].y == elements[1].y:
            # Horizontal pair
            if (abs(elements[0].rect.centerx - ball.x) <
                    abs(elements[1].rect.centerx - ball.x)):
                element = elements[0]
            else:
                element = elements[1]
            if ball.y < elements[0].rect.centery:
                direction = "top"
            else:
                direction = "bottom"
        else:
            # Staircase
            f = Terrain.collideSingle
            return [f(ball, elements[0]), f(ball, elements[1])]
        return [(element, direction)]

    @staticmethod
    def collideTriple(ball, elements):
        # Act on the two elements that are not adjacent to each other
        f = Terrain.collideSingle
        if elements[0].isAdjacent(elements[1]):
            if elements[0].isAdjacent(elements[2]):
                return [f(ball, elements[1]), f(ball, elements[2])]
            else:
                return [f(ball, elements[0]), f(ball, elements[2])]
        else:
            return [f(ball, elements[0]), f(ball, elements[1])]

    @staticmethod
    def manageCollision(ball, elements):
        # Determine which element to process if more than one was collided.
        # Figure out direction from which ball collided.
        assert(len(elements) <= 3)

        if len(elements) == 1:
            return [Terrain.collideSingle(ball, elements[0])]
        elif len(elements) == 2:
            return Terrain.collideDouble(ball, elements)
        else:
            return Terrain.collideTriple(ball, elements)

    def interactFromDir(self, ball, direction):
        assert(direction != None)

        ball.flying = False
        if ball.jumping:
            if direction == "left" or direction == "right":
                ball.vy = -1*ball.jumpvy
                Terrain.playSound("ninja")
            else:
                ball.jumping = False
                Terrain.playSound("bounce")
        else:
            Terrain.playSound("bounce")

        if direction == "left":
            if ball.jumping:
                ball.vx = -1*ball.jumpvx
            else:
                ball.vx = -1*abs(ball.vx)
        elif direction == "right":
            if ball.jumping:
                ball.vx = ball.jumpvx
            else:
                ball.vx = abs(ball.vx)
        elif direction == "top":
            ball.vy = -1*ball.bounciness
        elif direction == "bottom":
            ball.vy = abs(ball.vy)


    def isAdjacent(self, other):
        return self.x == other.x or self.y == other.y

    @staticmethod
    def playSound(sound):
        if Terrain.soundsOn:
            Terrain.sounds[sound].play()

class Wall(Terrain):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        grey1 = 220
        grey2 = 240
        self.image = pygame.Surface((self.width,
            self.height)).convert_alpha()
        rect = self.image.fill((grey1, grey1, grey1))
        pygame.draw.rect(self.image, (grey2, grey2, grey2), rect, 1)

class Finish(Terrain):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        self.image = pygame.Surface((self.width, self.height),
            pygame.SRCALPHA).convert_alpha()

    def interactFromDir(self, ball, direction):
        return "win"

class Exit(Terrain):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.canCollide = False

        self.image = pygame.transform.smoothscale(self.images["Exit"],
            (self.width, self.height))

    def interactFromDir(self, ball, direction):
        return None

class Rubble(Terrain):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.points = 1

        self.image = pygame.transform.smoothscale(self.images["Rubble"],
            (self.width, self.height))

    def interactFromDir(self, ball, direction):
        super().interactFromDir(ball, direction)
        if direction == "top":
            self.kill()
            Terrain.playSound("smash")
            return "score"

class Cannon(Terrain):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.direction = 1

        self.image = pygame.transform.smoothscale(self.images["Cannon"],
            (self.width, self.height))

    def interactFromDir(self, ball, direction):
        if direction == "top":
            Terrain.playSound("whoosh")
            return "fly"
        else:
            super().interactFromDir(ball, direction)

class CannonLeft(Cannon):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.direction = -1

        self.image = pygame.transform.smoothscale(self.images["CannonLeft"],
            (self.width, self.height))

class Trampoline(Terrain):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        self.image = pygame.transform.smoothscale(self.images["Trampoline"],
            (self.width, self.height))

    def interactFromDir(self, ball, direction):
        if direction == "top":
            ball.vy = (-1)*ball.maxvy
            Terrain.playSound("boing")
        else:
            super().interactFromDir(ball, direction)

class Bomb(Terrain):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        self.image = pygame.transform.smoothscale(self.images["Bomb"],
            (self.width, self.height))

    def interactFromDir(self, ball, direction):
        return "kill"
