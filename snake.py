import pygame
import constants
from pygame.math import Vector2
from collisionComp import *


class Snake:
    def __init__(self, x, y):
        self.name = "snake"
        self.head = SnakeHead(x, y)
        self.nodes = []
        for i in range(constants.INIT_NODE_LENGTH):
            self.nodes.append(
                SnakeNode(constants.START_SNAKE_X - i - 1, constants.START_SNAKE_Y)
            )

        self.speed = constants.SNAKE_SPEED  # tiles per second
        self.direction = Vector2(1, 0)
        self.remainingMoveTime = 0

    # return collisionComp containers
    def getCollisionSubjects(self):
        collisionSubs = self.nodes.copy()
        collisionSubs.append(self.head)
        return collisionSubs

    def checkIsDead(self):
        return self.head.collisionComp.isDead

    def reset(self):  # run per frame
        self.head.color = constants.SNAKE_HEAD_COLOR
        for i in self.nodes:
            i.color = constants.SNAKE_NODE_COLOR

    def update(self, app):
        self.reset()
        self.trackingTarget(app.player.collisionComp.position)
        self.remainingMoveTime -= app.dt

        if self.remainingMoveTime <= 0:
            self.remainingMoveTime = 1 / self.speed
            self.onMove()

    def handleCollision(self, target):
        if target.name == "player":
            self.head.color = constants.SNAKE_HEAD_COLOR_2
            for i in self.nodes:
                i.color = constants.SNAKE_HEAD_COLOR_2
            pygame.event.post(pygame.event.Event(constants.PLAYER_DEAD_EVENT))

    def trackingTarget(self, target: Vector2):
        if (self.head.collisionComp.position - target).length() == 0:
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

    def draw(self, app):
        for x in self.nodes:
            x.draw(app.screen)
        self.head.draw(app.screen)


class SnakeNode:
    def __init__(self, x, y, color=constants.SNAKE_NODE_COLOR):
        self.collisionComp = CollisionComp(x, y, constants.SNAKE_SIZE)
        self.color = color
        pass

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
