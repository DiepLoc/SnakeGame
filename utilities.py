from pygame.math import Vector2
import abc
import math
import random
import numbers
import constants
import pygame
import utilities


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


def getRandomDirection() -> Vector2:
    return Vector2(random.random() * 2 - 1, random.random() * 2 - 1).normalize()


direction_map = {
    (1, 0): 0,
    (-1, 0): 180,
    (0, 1): 90,
    (0, -1): 270,
}


def getAngleByVector(vec: Vector2) -> int:
    if vec.length() == 0:
        return 0

    return math.atan2(vec.y, vec.x) * 180 / math.pi


def sumDegreeAngles(a: float, b: float):
    return (a + b + 360) % 360


def getRotated90DegreesVector(vec: Vector2) -> Vector2:
    return Vector2(-vec.y, vec.x)


def getAngleBy4DVector(vec: Vector2) -> int:
    return direction_map[tuple(vec)]


def drawImage(
    screen: pygame.Surface,
    img: pygame.Surface,
    targetSize,  # int or tuple
    center=None,
    direction: Vector2 = Vector2(0, 1),
    color=None,
):
    angle = sumDegreeAngles(
        getAngleByVector(direction), -90
    )  # getAngleBy4DVector(direction) - 90
    rotated_img = pygame.transform.rotate(
        img, -angle
    )  # Pygame rotates counterclockwise
    targetSizeVec = (
        (targetSize, targetSize)
        if isinstance(targetSize, numbers.Number)
        else targetSize
    )
    scaled_img = pygame.transform.scale(rotated_img, targetSizeVec)
    center = center if center != None else (targetSizeVec[0] / 2, targetSizeVec[1] / 2)
    new_rect = scaled_img.get_rect(center=center)
    recolorImg = scaled_img if color == None else tint_image(scaled_img, color)
    screen.blit(recolorImg, new_rect.topleft)


def tint_image(image, tint_color):
    """Tints an image while keeping transparency and shading."""
    tinted = image.copy()  # Copy original image
    tinted.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)  # Multiply color
    return tinted


def lerpColors(start, end, ratio):
    if ratio == 0:
        return start
    if ratio == 1:
        return end

    dR = end[0] - start[0]
    dG = end[1] - start[1]
    dB = end[2] - start[2]
    dA = end[3] - start[3]
    return (
        clamp(start[0] + dR * ratio, 0, 255),
        clamp(start[1] + dG * ratio, 0, 255),
        clamp(start[2] + dB * ratio, 0, 255),
        clamp(start[3] + dA * ratio, 0, 255),
    )


class ShootBulletEventData:
    def __init__(self, tilePos, direction):
        self.tilePos: Vector2 = tilePos
        self.direction = direction


class GameObject(abc.ABC):
    def __init__(self, name, speed, direction: Vector2):
        super().__init__()
        self.name = name
        self.speed = speed
        self.baseSpeed = speed
        self.direction: Vector2 = direction
        self.lastDirection: Vector2 = (
            Vector2(0, 1) if direction.length() == 0 else direction
        )

    def updateSpeedAndLastDirection(self, app):
        if self.direction.length() > 0:
            self.lastDirection = self.direction

        dSpeed = self.speed - self.baseSpeed
        if dSpeed == 0:
            return
        if abs(dSpeed) < 0.1:
            self.speed = self.baseSpeed
            return
        # Adjust speed to base speed each frame
        self.speed -= dSpeed / 400

    def changeSpeed(self, val):
        self.speed = utilities.clamp(
            self.speed + val, constants.MIN_SPEED_OBJ, constants.MAX_SPEED_OBJ
        )

    def upgradeBaseSpeed(self):
        currentBonus = self.baseSpeed - constants.PLAYER_SPEED
        self.baseSpeed += 0.1 * (1 - (currentBonus) / (currentBonus + 0.1))

    def updateBaseSpeed(self, newVal):
        self.baseSpeed = newVal

    @abc.abstractmethod
    def checkIsDead(self):
        pass

    @abc.abstractmethod
    def getCollisionSubjects(self):
        pass

    @abc.abstractmethod
    def handleCollision(self, target):
        pass


# listen events
class Observer(abc.ABC):
    @abc.abstractmethod
    def onNotify(self, event):
        pass
