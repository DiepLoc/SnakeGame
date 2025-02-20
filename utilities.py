from pygame.math import Vector2


def clamp(val, min, max):
    if min > max:
        raise Exception("invalue args")
    if val < min:
        return min
    if val > max:
        return max
    return val


class ShootBulletEventData:
    def __init__(self, tilePos, direction):
        self.tilePos: Vector2 = tilePos
        self.direction = direction
