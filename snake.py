import pygame
import datetime
import constants
from pygame.math import Vector2
from collisionComp import *


class Snake:
    def __init__(self):
        self.head = SnakeHead(constants.START_SNAKE_X, constants.START_SNAKE_Y)
        self.nodes = []
        for i in range(constants.INIT_NODE_LENGTH):
            self.nodes.append(
                SnakeNode(constants.START_SNAKE_X - i - 1, constants.START_SNAKE_Y)
            )

        self.speed = constants.SNAKE_SPEED  # tiles per second
        self.direction = Vector2(1, 0)
        self.remainingMoveTime = 0

    def checkIsCollided(self, target):
        if self.head.checkIsCollided(target):
            return True
        for x in self.nodes:
            if x.checkIsCollided(target):
                return True
        return False

    def reset(self):  # run per frame
        self.head.color = constants.SNAKE_HEAD_COLOR
        for i in self.nodes:
            i.color = constants.SNAKE_NODE_COLOR

    def update(self, dt, player):
        self.reset()
        self.trackingTarget(player.collisionComp.position)
        self.remainingMoveTime -= dt

        if self.remainingMoveTime <= 0:
            self.remainingMoveTime = 1 / self.speed
            self.onMove()

        self.checkAndHandleCollision(player)

    def checkAndHandleCollision(self, target):
        if self.checkIsCollided(target):
            self.head.color = constants.SNAKE_HEAD_COLOR_2
            for i in self.nodes:
                i.color = constants.SNAKE_HEAD_COLOR_2

    def trackingTarget(self, target: Vector2):
        if len(target) == 0:
            return

        dx = target.x - self.head.collisionComp.position.x
        dy = target.y - self.head.collisionComp.position.y

        if abs(dx) > abs(dy):
            if dx > 0:
                self.direction = Vector2(1, 0)
            else:
                self.direction = Vector2(-1, 0)
        else:
            if dy > 0:
                self.direction = Vector2(0, 1)
            else:
                self.direction = Vector2(0, -1)

    def onMove(self):
        for i in range(len(self.nodes) - 1, 0, -1):
            self.nodes[i].update(self.nodes[i - 1])

        if len(self.nodes) > 0:
            self.nodes[0].update(self.head)
        self.head.update(self.direction)

    def draw(self, window, dt):
        for x in self.nodes:
            x.draw(window)
        self.head.draw(window)


class SnakeNode:
    def __init__(self, x, y, color=constants.SNAKE_NODE_COLOR):
        self.collisionComp = CollisionComp(x, y, constants.SNAKE_SIZE)
        self.color = color
        pass

    def checkIsCollided(self, target):
        return self.collisionComp.checkCollision(target.collisionComp)

    def update(self, nextNode):
        self.updatePosition(nextNode.collisionComp.position)

    def updatePosition(self, newPos):
        self.collisionComp.position = newPos

    def draw(self, window: pygame.surface):
        pygame.draw.circle(
            window,
            self.color,
            self.collisionComp.getCenter(),
            self.collisionComp.size / 2,
        )


class SnakeHead(SnakeNode):
    def __init__(self, x, y):
        super().__init__(x, y, constants.SNAKE_HEAD_COLOR)

    def update(self, vecDir: Vector2):
        if vecDir.length_squared != 0:
            self.updatePosition(self.collisionComp.position + vecDir.normalize())

    def draw(self, window: pygame.surface):
        super().draw(window)
