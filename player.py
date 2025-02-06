from pygame.math import Vector2
from collisionComp import *
import pygame
import constants


class Player:
    def __init__(self):
        self.collisionComp = CollisionComp(5, 5, constants.PLAYER_SIZE)
        self.speed = constants.PLAYER_SPEED
        self.direction = Vector2(0, 0)
        self.color = constants.PLAYER_COLOR
        self.remainingMoveTime = 0
        self.last_direction_key = None

    def update(self, dt, pressed_keys):
        if self.direction.length() == 0:
            return

        if constants.PLAYER_MOVE_TYPE == 1:
            self.moveV1(dt)
        else:
            self.moveV2(dt)

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # for debugging
                a = 1
            if event.key == pygame.K_w and self.last_direction_key != pygame.K_s:
                self.direction = Vector2(0, -1)
                self.last_direction_key = pygame.K_w
            elif event.key == pygame.K_s and self.last_direction_key != pygame.K_w:
                self.direction = Vector2(0, 1)
                self.last_direction_key = pygame.K_s
            elif event.key == pygame.K_a and self.last_direction_key != pygame.K_d:
                self.direction = Vector2(-1, 0)
                self.last_direction_key = pygame.K_a
            elif event.key == pygame.K_d and self.last_direction_key != pygame.K_a:
                self.direction = Vector2(1, 0)
                self.last_direction_key = pygame.K_d

    def moveV1(self, dt):
        self.collisionComp.position += dt * self.speed * self.direction.normalize()

    def moveV2(self, dt):
        self.remainingMoveTime -= dt
        if self.remainingMoveTime > 0:
            return

        self.remainingMoveTime = 1 / self.speed
        self.collisionComp.position += self.direction

    def draw(self, window):
        pygame.draw.circle(
            window,
            self.color,
            self.collisionComp.getCenter(),
            self.collisionComp.size / 2,
        )
