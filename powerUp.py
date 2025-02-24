import pygame
import constants
import utilities
import random
import abc  # abstract class module
from pygame.math import Vector2
from collisionComp import *
from player import *
import snake as sn
from textureManager import TextureName


class PowerUp(utilities.GameObject):
    def __init__(
        self,
        image: TextureName,
        x,
        y,
        powerInfo,
        color="white",
        speed=0,
        direction=Vector2(0, 1),
        lifeTime=None,
    ):
        super().__init__(speed, direction)
        self.image: TextureName = image
        self.name = "power-up"
        self.collisionComp = CollisionComp(x, y, constants.POWER_UP_SIZE)
        self.powerInfo: PowerUpInfo = powerInfo
        self.color = color
        self.remainingLifeTime = lifeTime  # none: infinite life

    # return collisionComp containers
    def getCollisionSubjects(self):
        return [self]

    def checkIsAttactSnake(self):
        return self.powerInfo.isSnakeAttactor()

    def handleCollision(self, target):
        if target.name == "player":
            self.collisionComp.isDead = self.powerInfo.onPlayerApply(self, target)
        elif target.name == "snake":
            self.collisionComp.isDead = self.powerInfo.onSnakeApply(self, target)

    def update(self, app):
        self.updateSpeedAndLastDirection(app)
        self.collisionComp.onSmoothMove(app.dt, self.speed, self.direction)
        if self.remainingLifeTime is not None:
            self.remainingLifeTime -= app.dt
            if self.remainingLifeTime <= 0:
                self.collisionComp.isDead = True

    def checkIsDead(self):
        return self.collisionComp.isDead

    def draw(self, app):
        utilities.drawImage(
            app.screen,
            app.textureManager.getTextureByName(self.image),
            self.collisionComp.size,
            self.collisionComp.getCenter(),
            self.lastDirection,
            self.color,
        )

    @staticmethod
    def generateSpeedUpPower(app):
        pos = app.getValidRandomTilePosition()
        app.addObject(
            PowerUp(
                TextureName.LEMON,
                pos.x,
                pos.y,
                SpeedUpInfo(constants.PLAYER_LEMON_SPEED_CHANGE),
            )
        )

    @staticmethod
    def generateResizePower(app):
        pos = app.getValidRandomTilePosition()
        app.addObject(PowerUp(TextureName.CHOCOLATE, pos.x, pos.y, ChangeSizeInfo(5)))

    # @staticmethod
    # def generateAddLengthPower(app):
    #     pos = app.getValidRandomTilePosition()
    #     app.addObject(PowerUp(pos.x, pos.y, AddLengthInfo(), "green"))

    @staticmethod
    def generateApplePower(app):
        pos = app.getValidRandomTilePosition()
        app.addObject(PowerUp(TextureName.APPLE, pos.x, pos.y, AppleInfo()))

    @staticmethod
    def generateTeleportPower(app):
        teleport1 = TeleportInfo()
        teleport2 = TeleportInfo()
        pos1 = app.getValidRandomTilePosition()
        pos2 = app.getValidRandomTilePosition([pos1])
        randomColor = (
            random.randint(0, 200),
            random.randint(0, 200),
            random.randint(0, 200),
        )
        teleportPower1 = PowerUp(
            TextureName.TELEPORT, pos1.x, pos1.y, teleport1, randomColor
        )
        teleportPower2 = PowerUp(
            TextureName.TELEPORT, pos2.x, pos2.y, teleport2, randomColor
        )
        teleport1.linkTeleport(teleportPower2)
        teleport2.linkTeleport(teleportPower1)
        app.addObject(teleportPower1)
        app.addObject(teleportPower2)

    @staticmethod
    def generateSlowBullet(app, data: utilities.ShootBulletEventData):
        newBullet = PowerUp(
            TextureName.SLOW_BULLET,
            data.tilePos.x,
            data.tilePos.y,
            SlowBulletInfo(),
            "white",
            constants.SLOW_BULLET_SPEED,
            data.direction,
            2,
        )
        app.addObject(newBullet)


class PowerUpInfo(abc.ABC):
    @abc.abstractmethod
    # return True -> power up consumed, False -> power up ignored
    def onPlayerApply(self, subject, target: Player) -> bool:
        pass

    @abc.abstractmethod
    # return True -> power up consumed, False -> power up ignored
    def onSnakeApply(self, subject, target: sn.Snake) -> bool:
        pass

    @abc.abstractmethod
    # return True -> attract snake AI
    def isSnakeAttactor(self) -> bool:
        pass


class ChangeSizeInfo(PowerUpInfo):
    def __init__(self, dSize):
        self.changeSizeVal = dSize

    def onPlayerApply(self, subject, target: Player):
        target.collisionComp.changeSize(-self.changeSizeVal)  # downsize for player
        pygame.event.post(pygame.event.Event(constants.PLAYER_GET_CHOCOLATE_EVENT))
        return True

    def onSnakeApply(self, subject, target: sn.Snake):
        target.changeSize(self.changeSizeVal)  # upsize for snake
        return True

    def isSnakeAttactor(self) -> bool:
        return True


class SlowBulletInfo(PowerUpInfo):
    def __init__(self):
        pass

    def onPlayerApply(self, subject, target: Player):
        target.changeSpeed(constants.HIT_SLOW_BULLET_SPEED_REDUCTION)
        pygame.event.post(pygame.event.Event(constants.PLAYER_HIT_SLOW_BULLET_EVENT))
        return True

    def onSnakeApply(self, subject, target: sn.Snake):
        return False

    def isSnakeAttactor(self) -> bool:
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
        pygame.event.post(pygame.event.Event(constants.PLAYER_GET_TELEPORT_EVENT))
        return True

    def onSnakeApply(self, subject, target: sn.Snake):
        return False

    def isSnakeAttactor(self) -> bool:
        return False


class AppleInfo(PowerUpInfo):
    def __init__(self):
        pass

    def onPlayerApply(self, subject, target: Player):
        pygame.event.post(pygame.event.Event(constants.PLAYER_GET_APPLE_EVENT))
        return True

    def onSnakeApply(self, subject, target: sn.Snake):
        target.addLength(2)
        return True

    def isSnakeAttactor(self) -> bool:
        return True


class SpeedUpInfo(PowerUpInfo):
    def __init__(self, speedUpVal):
        self.speedUp = speedUpVal

    def onPlayerApply(self, subject, target: Player):
        target.changeSpeed(self.speedUp)
        pygame.event.post(pygame.event.Event(constants.PLAYER_GET_LEMON_EVENT))
        return True

    def onSnakeApply(self, subject, target: sn.Snake):
        target.changeSpeed(self.speedUp / 4)
        return True

    def isSnakeAttactor(self) -> bool:
        return True
