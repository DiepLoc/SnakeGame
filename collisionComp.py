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
        return (self.position + Vector2(0.5, 0.5)) * constants.TILE_SIZE.x

    def changeSize(self, changeAmount):
        self.size = utilities.clamp(self.size + changeAmount, 10, 100)

    def onSmoothMove(self, dt, speed, direction: Vector2):
        if direction.length() != 0:
            self.position += dt * speed * direction.normalize()
            self.position = utilities.clampPosition(self.position)

    def checkCollision(self, other):
        selfCenter = self.getCenter()
        targetCenter = other.getCenter()
        dxy = targetCenter - selfCenter
        length = dxy.length()
        return length < self.size / 2 + other.size / 2
