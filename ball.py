# Ball class

import pygame

class Ball(pygame.sprite.Sprite):
    def initSpeeds(self):
        self.maxvx = 4
        self.flyvx = 10
        self.jumpvx = 6
        self.maxvy = 10.2
        self.bounciness = 6.6
        self.jumpvy = 4.8

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.ax = 1
        self.ay = 0.54

        self.initSpeeds()

        self.r = 4
        self.realR = 10

        self.flying = False
        self.jumping = False

        self.color = (31, 73, 191)
        self.getImage()
        self.getRect()

    def getImage(self):
        # Smooth image by drawing at 2x resolution
        scaled = 2*self.r
        image = pygame.Surface((2 * scaled, 2 * scaled),
            pygame.SRCALPHA).convert_alpha()
        pygame.draw.circle(image, self.color, (scaled, scaled), scaled)
        self.image = pygame.transform.smoothscale(image,
            (2*self.r, 2*self.r))

    def getRect(self):
        self.rect = pygame.Rect(self.x - self.realR, self.y - self.realR,
            2*self.realR, 2*self.realR)

    def playerInput(self, keysDown):
        if keysDown(pygame.K_LEFT) and keysDown(pygame.K_RIGHT):
            self.jumping = True
        else:
            self.jumping = False
            keyDir = 0
            if keysDown(pygame.K_LEFT):
                keyDir = -1
                if self.flying and self.vx > 0:
                    self.flying = False
            elif keysDown(pygame.K_RIGHT):
                keyDir = 1
                if self.flying and self.vx < 0:
                    self.flying = False
            self.vx += keyDir*self.ax

    def update(self, keysDown):
        # Displacement
        self.x += self.vx
        self.y += self.vy
        # Horizontal acceleration
        if self.flying:
            maxvx = self.flyvx
        elif self.jumping:
            maxvx = self.jumpvx
        else:
            maxvx = self.maxvx
        selfDir = -1 if self.vx < 0 else 1
        self.playerInput(keysDown)
        if abs(self.vx) > maxvx:
            self.vx = selfDir*maxvx
        # Vertical acceleration
        if self.flying:
            self.vy = 0
        else:
            self.vy += self.ay
            if self.vy > self.maxvy:
                self.vy = self.maxvy
        # Update rectangle
        self.getRect()

    def draw(self, screen):
        screen.blit(self.image, (self.x - self.r, self.y - self.r))
