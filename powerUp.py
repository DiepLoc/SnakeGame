import pygame
import constants
from pygame.math import Vector2
from collisionComp import *


class PowerUp:
    def __init__(self, x, y, power):
        self.name = "power-up"
        self.collisionComp = CollisionComp(x, y, constants.POWER_UP_SIZE)
        self.power = power
        self.color = (0, 0, 255)

    # return collisionComp containers
    def getCollisionSubjects(self):
        return [self]

    def handleCollision(self, target):
        if target.name == "player":
            self.power(target)
            self.collisionComp.isDead = True

    def update(self, app):
        pass

    def checkIsDead(self):
        return self.collisionComp.isDead

    def draw(self, app):
        pygame.draw.circle(
            app.screen,
            self.color,
            self.collisionComp.getCenter(),
            self.collisionComp.size / 2,
        )
