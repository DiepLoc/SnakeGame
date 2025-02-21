import pygame
import constants
import utilities
import random
from pygame.math import Vector2
from collisionComp import *


class Snake(utilities.GameObject):
    def __init__(self, x, y):
        super().__init__(constants.SNAKE_SPEED, Vector2(1, 0))
        self.name = "snake"
        self.head = SnakeHead(x, y, self)
        self.nodes: list[SnakeNode] = []
        for i in range(constants.INIT_NODE_LENGTH):
            self.nodes.append(SnakeNode(x, y, self))

        self.remainingMoveTime = 0
        self.remainingShootTime = 0

    def addLength(self, changeLength=1):
        for i in range(0, changeLength):
            currentLastNode = self.nodes[self.nodes.__len__() - 1]
            self.nodes.append(
                SnakeNode(
                    currentLastNode.collisionComp.position.x,
                    currentLastNode.collisionComp.position.y,
                    self,
                )
            )

    def changeSpeed(self, val):
        self.speed = utilities.clamp(self.speed + val, 0.5, 5)

    def changeSize(self, changeSize):
        self.head.collisionComp.changeSize(changeSize)
        for x in self.nodes:
            x.collisionComp.changeSize(changeSize)

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

    def shootBullet(self):
        data = utilities.ShootBulletEventData(
            self.head.collisionComp.position, self.direction
        )
        pygame.event.post(
            pygame.event.Event(constants.SNAKE_SHOOT_BULLET_EVENT, {"data": data})
        )

    def updateShoot(self, app):
        self.remainingShootTime -= app.dt
        if (
            app.getGameState() >= 1
            and self.remainingShootTime <= 0
            and random.randint(0, 120) == 0
        ):  # 120 frames ~ 2 seconds
            self.shootBullet()
            self.remainingShootTime = constants.SNAKE_SHOOT_DELAY_TIME

    def update(self, app):
        self.reset()
        self.trackingTarget(app.player.collisionComp.position)
        self.updateShoot(app)
        self.updateSpeedAndLastDirection(app)

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
        for x in reversed(self.nodes):
            x.draw(app)
        self.head.draw(app)


class SnakeNode:
    def __init__(self, x, y, snake: Snake, color=constants.SNAKE_NODE_COLOR):
        self.collisionComp = CollisionComp(x, y, constants.SNAKE_SIZE)
        self.color = color
        self.snake = snake
        self.name = "snake-node"

    def update(self, nextNode):
        self.updatePosition(nextNode.collisionComp.position)

    def updatePosition(self, newPos):
        self.collisionComp.position = newPos

    def draw(self, app):
        utilities.drawImage(
            app.screen,
            app.snakeNodeImage,
            self.collisionComp.size,
            self.collisionComp.getCenter(),
            self.snake.lastDirection,
        )


class SnakeHead(SnakeNode):
    def __init__(self, x, y, snake):
        super().__init__(x, y, snake, constants.SNAKE_HEAD_COLOR)

    def update(self, vecDir: Vector2):
        if vecDir.length_squared != 0:
            self.updatePosition(self.collisionComp.position + vecDir.normalize())

    def draw(self, app):
        utilities.drawImage(
            app.screen,
            app.snakeHeadImage,
            self.collisionComp.size,
            self.collisionComp.getCenter(),
            self.snake.lastDirection,
        )
