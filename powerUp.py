import pygame
import constants
import utilities
from pygame.math import Vector2
from collisionComp import *
from player import *
from snake import *


class PowerUp:
    def __init__(self, x, y, powerInfo, speed=0, direction=Vector2(0, 0)):
        self.name = "power-up"
        self.collisionComp = CollisionComp(x, y, constants.POWER_UP_SIZE)
        self.powerInfo = powerInfo
        self.speed = speed
        self.direction = direction
        self.color = (0, 0, 255)

    # return collisionComp containers
    def getCollisionSubjects(self):
        return [self]

    def handleCollision(self, target):
        if target.name == "player":
            self.collisionComp.isDead = self.powerInfo.onPlayerApply(self, target)
        elif target.name == "snake-node":
            self.collisionComp.isDead = self.powerInfo.onSnakeNodeApply(self, target)

    def update(self, app):
        self.collisionComp.onSmoothMove(app.dt, self.speed, self.direction)

    def checkIsDead(self):
        return self.collisionComp.isDead

    def draw(self, app):
        pygame.draw.circle(
            app.screen,
            self.color,
            self.collisionComp.getCenter(),
            self.collisionComp.size / 2,
        )


# for both player and snake
class ChangeSizeInfo:
    def __init__(self, dSize):
        self.changeSizeVal = dSize

    def onPlayerApply(self, subject, target: Player):
        target.collisionComp.changeSize(self.changeSizeVal)
        return True

    def onSnakeNodeApply(self, subject, target: SnakeNode):
        target.snake.changeSize(self.changeSizeVal)
        return True


# for snake
class AddLengthInfo:
    def __init__(self):
        pass

    def onPlayerApply(self, subject, target: Player):
        return False

    def onSnakeNodeApply(self, subject, target: SnakeNode):
        target.snake.addLength(1)
        return True


class SlowBulletInfo:
    def __init__(self):
        pass

    def onPlayerApply(self, subject, target: Player):
        target.speed -= 2
        return True

    def onSnakeNodeApply(self, subject, target: SnakeNode):
        return False


# for player
class TeleportInfo:
    def __init__(self):
        self.telePosition = None
        self.linkedPower = None

    def linkTeleport(self, otherTelePower):
        self.telePosition = otherTelePower.collisionComp.position
        self.linkedPower = otherTelePower

    def onPlayerApply(self, subject, target: Player):
        target.collisionComp.position = self.telePosition
        self.linkedPower.collisionComp.isDead = True
        return True

    def onSnakeNodeApply(self, subject, target: SnakeNode):
        return False


# for both playe and snake
class SpeedUpInfo:
    def __init__(self):
        self.speedUp = 5

    def onPlayerApply(self, subject, target: Player):
        target.speed += 5
        return True

    def onSnakeNodeApply(self, subject, target: SnakeNode):
        target.snake.speed += 5
        return True
