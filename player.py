from pygame.math import Vector2
from collisionComp import *
import pygame
import constants
import utilities
import textureManager


class Player(utilities.GameObject):
    def __init__(self):
        super().__init__(
            constants.PLAYER_SPEED,
            Vector2(constants.START_PLAYER_X, constants.START_PLAYER_Y),
        )
        self.name = "player"
        self.collisionComp = CollisionComp(5, 5, constants.PLAYER_SIZE)
        self.color = constants.PLAYER_COLOR
        self.remainingMoveTime = 0

    def update(self, app):
        self.updateSpeedAndLastDirection(app)

        if self.direction.length() == 0:
            return

        if constants.PLAYER_MOVE_TYPE == 1:
            self.moveV1(app.dt)
        else:
            self.moveV2(app.dt)

    def checkIsDead(self):
        return self.collisionComp.isDead

    # return collisionComp containers
    def getCollisionSubjects(self):
        return [self]

    def handleCollision(self, target):
        pass

    def handleInputByEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # for debugging
                a = 1
            if event.key == pygame.K_w:
                self.direction = Vector2(0, -1)
            elif event.key == pygame.K_s:
                self.direction = Vector2(0, 1)
            elif event.key == pygame.K_a:
                self.direction = Vector2(-1, 0)
            elif event.key == pygame.K_d:
                self.direction = Vector2(1, 0)

    def moveV1(self, dt):
        self.collisionComp.onSmoothMove(dt, self.speed, self.direction)

    def moveV2(self, dt):
        self.remainingMoveTime -= dt
        if self.remainingMoveTime > 0:
            return

        self.remainingMoveTime = 1 / self.speed
        self.collisionComp.position += self.direction
        self.collisionComp.position = utilities.clampPosition(
            self.collisionComp.position
        )

    def draw(self, app):
        # pygame.draw.circle(
        #     app.screen,
        #     self.color,
        #     self.collisionComp.getCenter(),
        #     self.collisionComp.size / 2,
        # )
        utilities.drawImage(
            app.screen,
            app.textureManager.getTextureByName(textureManager.TextureName.MOUSE),
            self.collisionComp.size,
            self.collisionComp.getCenter(),
            self.lastDirection,
        )
