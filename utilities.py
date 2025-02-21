from pygame.math import Vector2
import abc
import constants
import pygame


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


direction_to_angle = {"right": 0, "down": 90, "left": 180, "up": 270}
direction_map = {
    (1, 0): 0,
    (-1, 0): 180,
    (0, 1): 90,
    (0, -1): 270,
}


def getAngleBy4DVector(vec: Vector2) -> int:
    match tuple(vec):
        case (1, 0):
            return 0
        case (-1, 0):
            return 180
        case (0, 1):
            return 90
        case (0, -1):
            return 270
    raise Exception("invalid vector")


def drawImage(
    screen: pygame.Surface,
    img: pygame.Surface,
    targetSize: int,
    center,
    direction: Vector2,
    color=None,
):
    angle = getAngleBy4DVector(direction) - 90
    rotated_img = pygame.transform.rotate(
        img, -angle
    )  # Pygame rotates counterclockwise
    scaled_img = pygame.transform.scale(rotated_img, (targetSize, targetSize))
    new_rect = scaled_img.get_rect(center=center)
    recolorImg = scaled_img if color == None else tint_image(scaled_img, color)
    screen.blit(recolorImg, new_rect.topleft)


def tint_image(image, tint_color):
    """Tints an image while keeping transparency and shading."""
    tinted = image.copy()  # Copy original image
    tinted.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)  # Multiply color
    return tinted


def recolor_image(image, new_color):
    """Completely recolors an image while keeping transparency."""
    colored = pygame.Surface(image.get_size(), pygame.SRCALPHA)  # Transparent surface
    colored.fill(new_color)  # Fill with new color
    image.blit(colored, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)  # Apply color
    return image


class ShootBulletEventData:
    def __init__(self, tilePos, direction):
        self.tilePos: Vector2 = tilePos
        self.direction = direction


class GameObject(abc.ABC):
    def __init__(self, speed, direction: Vector2):
        super().__init__()
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

    @abc.abstractmethod
    def checkIsDead(self):
        pass

    @abc.abstractmethod
    def getCollisionSubjects(self):
        pass

    @abc.abstractmethod
    def handleCollision(self, target):
        pass
