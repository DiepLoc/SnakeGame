import pygame
import constants
import utilities
import abc  # abstract class module
from pygame.math import Vector2
from collisionComp import *
from player import *
from snake import *


class PowerUp(utilities.GameObject):
    def __init__(
        self,
        x,
        y,
        powerInfo,
        color=(0, 0, 255),
        speed=0,
        direction=Vector2(0, 0),
        lifeTime=None,
    ):
        super().__init__(speed, direction)
        self.name = "power-up"
        self.collisionComp = CollisionComp(x, y, constants.POWER_UP_SIZE)
        self.powerInfo: PowerUpInfo = powerInfo
        self.color = color
        self.remainingLifeTime = lifeTime  # none: infinite life

    # return collisionComp containers
    def getCollisionSubjects(self):
        return [self]

    def handleCollision(self, target):
        if target.name == "player":
            self.collisionComp.isDead = self.powerInfo.onPlayerApply(self, target)
        elif target.name == "snake":
            self.collisionComp.isDead = self.powerInfo.onSnakeApply(self, target)

    def update(self, app):
        self.updateSpeed(app)
        self.collisionComp.onSmoothMove(app.dt, self.speed, self.direction)
        if self.remainingLifeTime is not None:
            self.remainingLifeTime -= app.dt
            if self.remainingLifeTime <= 0:
                self.collisionComp.isDead = True

    def checkIsDead(self):
        return self.collisionComp.isDead

    def draw(self, app):
        pygame.draw.circle(
            app.screen,
            self.color,
            self.collisionComp.getCenter(),
            self.collisionComp.size / 2,
        )

    @staticmethod
    def generateSpeedUpPower(app):
        pos = app.getValidRandomTilePosition()
        app.addObject(PowerUp(pos.x, pos.y, SpeedUpInfo(0.5), "yellow"))

    @staticmethod
    def generateResizePower(app):
        pos = app.getValidRandomTilePosition()
        app.addObject(PowerUp(pos.x, pos.y, ChangeSizeInfo(5), "blue"))

    # @staticmethod
    # def generateAddLengthPower(app):
    #     pos = app.getValidRandomTilePosition()
    #     app.addObject(PowerUp(pos.x, pos.y, AddLengthInfo(), "green"))

    @staticmethod
    def generateFruitPower(app):
        pos = app.getValidRandomTilePosition()
        app.addObject(PowerUp(pos.x, pos.y, FruitInfo(), "red"))

    @staticmethod
    def generateTeleportPower(app):
        teleport1 = TeleportInfo()
        teleport2 = TeleportInfo()
        pos1 = app.getValidRandomTilePosition()
        pos2 = app.getValidRandomTilePosition([pos1])
        randomColor = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        teleportPower1 = PowerUp(pos1.x, pos1.y, teleport1, randomColor)
        teleportPower2 = PowerUp(pos2.x, pos2.y, teleport2, randomColor)
        teleport1.linkTeleport(teleportPower2)
        teleport2.linkTeleport(teleportPower1)
        app.addObject(teleportPower1)
        app.addObject(teleportPower2)

    @staticmethod
    def generateSlowBullet(app, data: utilities.ShootBulletEventData):
        newBullet = PowerUp(
            data.tilePos.x,
            data.tilePos.y,
            SlowBulletInfo(),
            (240, 240, 240),
            constants.SLOW_BULLET_SPEED,
            data.direction,
            2,
        )
        app.addObject(newBullet)


class PowerUpInfo(abc.ABC):
    @abc.abstractmethod
    def onPlayerApply(self, subject, target: Player):
        pass

    @abc.abstractmethod
    def onSnakeApply(self, subject, target: Snake):
        pass


class ChangeSizeInfo(PowerUpInfo):
    def __init__(self, dSize):
        self.changeSizeVal = dSize

    def onPlayerApply(self, subject, target: Player):
        target.collisionComp.changeSize(-self.changeSizeVal)  # downsize for player
        return True

    def onSnakeApply(self, subject, target: Snake):
        target.changeSize(self.changeSizeVal)  # upsize for snake
        return True


# class AddLengthInfo(PowerUpInfo):
#     def __init__(self):
#         pass

#     def onPlayerApply(self, subject, target: Player):
#         return True

#     def onSnakeApply(self, subject, target: Snake):
#         target.addLength(1)
#         return True


class SlowBulletInfo(PowerUpInfo):
    def __init__(self):
        pass

    def onPlayerApply(self, subject, target: Player):
        target.changeSpeed(-0.3)
        return True

    def onSnakeApply(self, subject, target: Snake):
        return False


class TeleportInfo(PowerUpInfo):
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

    def onSnakeApply(self, subject, target: Snake):
        return False


class FruitInfo(PowerUpInfo):
    def __init__(self):
        pass

    def onPlayerApply(self, subject, target: Player):
        pygame.event.post(pygame.event.Event(constants.GOT_FRUIT_EVENT))
        return True

    def onSnakeApply(self, subject, target: Snake):
        target.addLength(1)
        return True


class SpeedUpInfo(PowerUpInfo):
    def __init__(self, speedUpVal):
        self.speedUp = speedUpVal

    def onPlayerApply(self, subject, target: Player):
        target.changeSpeed(self.speedUp)
        return True

    def onSnakeApply(self, subject, target: Snake):
        target.changeSpeed(self.speedUp)
        return True
