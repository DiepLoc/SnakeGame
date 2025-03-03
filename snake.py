import pygame
import constants
import utilities
import random
from pygame.math import Vector2
from collisionComp import *
import textureManager


class Snake(utilities.GameObject):
    def __init__(self, x, y):
        super().__init__("snake", constants.SNAKE_SPEED, Vector2(1, 0))
        self.head = SnakeHead(x, y, self)
        self.nodes: list[SnakeNode] = []
        for i in range(constants.INIT_NODE_LENGTH):
            self.nodes.append(SnakeNode(x, y, self))

        self.remainingMoveTime = 0
        self.remainingShootTime = 0
        self.trackingPower = None

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

    def shootBullet(self, direction: Vector2):
        data = utilities.ShootBulletEventData(
            self.head.collisionComp.position, direction
        )
        pygame.event.post(
            pygame.event.Event(constants.SNAKE_SHOOT_BULLET_EVENT, {"data": data})
        )

    def shootMultiBullets(self):
        dir1 = utilities.getRandomDirection()
        dir2 = utilities.getRotated90DegreesVector(dir1)
        dir3 = utilities.getRotated90DegreesVector(dir2)
        dir4 = utilities.getRotated90DegreesVector(dir3)
        self.shootBullet(dir1)
        self.shootBullet(dir2)
        self.shootBullet(dir3)
        self.shootBullet(dir4)

    def updateShoot(self, app):
        import main

        self.remainingShootTime -= app.dt
        gameState = app.getGameState()
        if (
            gameState != main.GameState.Easy
            and self.remainingShootTime <= 0
            and random.randint(0, 180) == 0  # 180 frames ~ 3 seconds
        ):
            if gameState == main.GameState.Medium:
                self.shootBullet(self.direction)
            elif gameState == main.GameState.Hard:
                self.shootMultiBullets()
            self.remainingShootTime = constants.SNAKE_SHOOT_DELAY_TIME

    def update(self, app):
        self.reset()
        self.updateTracking(app)
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

    def updateTracking(self, app):
        if (
            self.trackingPower == None
            and random.randint(0, int(constants.SNAKE_FIND_FRUIT_RANDOM_TIME * 60)) == 0
        ):
            self.trackingPower = self.tryGetTrackingFruit(app)

        if self.trackingPower != None and self.trackingPower.checkIsDead():
            self.trackingPower = None

        collisionCompTarget = (
            app.player.collisionComp
            if self.trackingPower == None
            else self.trackingPower.collisionComp
        )
        self.trackingTarget(collisionCompTarget)

    def tryGetTrackingFruit(self, app) -> utilities.GameObject:
        import powerUp

        isAttactSnakeFruit = (
            lambda obj: obj.name == "power-up" and obj.checkIsAttactSnake()
        )
        fruits: list[powerUp.PowerUp] = app.getObjByCondition(isAttactSnakeFruit)

        minDistance = app.player.collisionComp.getDistance(self.head.collisionComp)
        trackingFruit = None

        for fruit in fruits:
            distance = fruit.collisionComp.getDistance(self.head.collisionComp)
            if (
                distance < minDistance
                and distance <= constants.MAX_SNAKE_TRACKING_FRUIT_DISTANCE
            ):
                trackingFruit = fruit
                minDistance = distance

        return trackingFruit

    def trackingTarget(self, collisionCompTarget: CollisionComp):
        targetPos = collisionCompTarget.position
        if (self.head.collisionComp.position - targetPos).length() == 0:
            return

        dx = targetPos.x - self.head.collisionComp.position.x
        dy = targetPos.y - self.head.collisionComp.position.y

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

    def update(self, nextNode):
        self.updatePosition(nextNode.collisionComp.position)

    def updatePosition(self, newPos):
        self.collisionComp.position = newPos

    def draw(self, app):
        utilities.drawImage(
            app.screen,
            app.textureManager.getTextureByName(textureManager.TextureName.SNAKE_NODE),
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
            app.textureManager.getTextureByName(textureManager.TextureName.SNAKE_HEAD),
            self.collisionComp.size,
            self.collisionComp.getCenter(),
            self.snake.lastDirection,
        )
