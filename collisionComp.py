import pygame
import constants
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

    def checkCollision(self, other):
        selfCenter = self.getCenter()
        targetCenter = other.getCenter()
        dxy = targetCenter - selfCenter
        length = dxy.length()
        return length < self.size / 2 + other.size / 2
