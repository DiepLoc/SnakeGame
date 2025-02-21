from pygame.math import Vector2
import abc
import constants


def clamp(val, min, max):
    if min > max:
        raise Exception("invalue args")
    if val < min:
        return min
    if val > max:
        return max
    return val


def clampPosition(position) -> Vector2:
    newX = clamp(position.x, 0, constants.GRID_SIZE.x - 1)
    newY = clamp(position.y, 0, constants.GRID_SIZE.y - 1)
    return Vector2(newX, newY)


class ShootBulletEventData:
    def __init__(self, tilePos, direction):
        self.tilePos: Vector2 = tilePos
        self.direction = direction


class GameObject(abc.ABC):
    def __init__(self, speed, direction):
        super().__init__()
        self.speed = speed
        self.baseSpeed = speed
        self.direction = direction

    def updateSpeed(self, app):
        dSpeed = self.speed - self.baseSpeed
        if dSpeed == 0:
            return
        if abs(dSpeed < 0.1):
            self.speed = self.baseSpeed
            return
        # Adjust speed to base speed each frame
        self.speed -= dSpeed / 400

    @abc.abstractmethod
    def checkIsDead(self):
        pass

    @abc.abstractmethod
    def getCollisionSubjects(self):
        pass

    @abc.abstractmethod
    def handleCollision(self, target):
        pass
