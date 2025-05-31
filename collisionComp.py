from __future__ import annotations
import constants
import utilities
from pygame.math import Vector2


class CollisionComp:
    def __init__(self, x, y, size):
        self.position = Vector2(x, y)
        self.size: int = size
        self.isDead = False

    def getCenter(self):
        return (self.position + Vector2(0.5, 0.5)) * constants.TILE_SIZE.x

    def changeSize(self, changeAmount):
        self.size = utilities.clamp(
            self.size + changeAmount,
            constants.TILE_SIZE.x / 2,
            constants.TILE_SIZE.x * 5,
        )

    def isMinSize(self):
        return self.size <= constants.TILE_SIZE.x / 2

    def onSmoothMove(self, dt, speed, direction: Vector2, isScreenLimit=True):
        if direction.length() != 0:
            self.position += dt * speed * direction.normalize()
            # limit the movement of objects on the screen
            if isScreenLimit:
                self.position = utilities.clampPosition(self.position)

    def getDistance(self, other: CollisionComp):
        vec = self.position - other.position
        return vec.length()

    def checkCollision(self, other):
        selfCenter = self.getCenter()
        targetCenter = other.getCenter()
        dxy = targetCenter - selfCenter
        length = dxy.length()
        return length < self.size / 2 + other.size / 2
