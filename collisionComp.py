import pygame
import constants
import utilities
from pygame.math import Vector2


class CollisionComp:
    def __init__(self, x, y, size):
        self.position = Vector2(x, y)
        self.size = size
        self.isDead = False

    def getCenter(self):
        return self.position * constants.TILE_SIZE.x + Vector2(
            self.size / 2, self.size / 2
        )

    def changeSize(self, changeAmount):
        self.size = utilities.clamp(self.size + changeAmount, 5, 30)

    def onSmoothMove(self, dt, speed, direction: Vector2):
        if direction.length() != 0:
            self.position += dt * speed * direction.normalize()

    def checkCollision(self, other):
        selfCenter = self.getCenter()
        targetCenter = other.getCenter()
        dxy = targetCenter - selfCenter
        length = dxy.length()
        return length < self.size / 2 + other.size / 2
