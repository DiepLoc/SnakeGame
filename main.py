# Import and initialize the pygame library
import pygame
import random
import constants
from snake import *
from player import *
from powerUp import *

pygame.init()
pygame.font.init()  # you have to call this at the start,
# if you want to use this module.
my_font = pygame.font.SysFont("Comic Sans MS", 30)


class App:
    def __init__(self):
        self.dt = 0  # delta time - seconds
        self.screen = pygame.display.set_mode(
            [constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT]
        )
        self.clock = pygame.time.Clock()
        self.objs = []
        self.player = None  # for Player reference
        self.remaningSpawnPowerTime = 5
        self.events = []
        self.isGameOver = False
        self.pressed_keys = []
        self.pressed_mouses = []

    def reset(self):
        self.objs = []
        snake = Snake(constants.START_SNAKE_X, constants.START_SNAKE_Y)
        player = Player()
        self.player = player
        self.objs.append(player)
        self.objs.append(snake)
        self.isGameOver = False

    @staticmethod
    def checkAndHandleCollision(a, b):
        collisionSubjectsA = a.getCollisionSubjects()
        collisionSubjectsB = b.getCollisionSubjects()

        for i in collisionSubjectsA:
            for k in collisionSubjectsB:
                if (
                    not i.collisionComp.isDead
                    and not k.collisionComp.isDead
                    and i.collisionComp.checkCollision(k.collisionComp)
                ):
                    a.handleCollision(b)
                    b.handleCollision(a)
                    return

    def run(self):
        self.reset()
        running = True
        while running:
            # Did the user click the window close button?
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

                if event.type == constants.PLAYER_DEAD_EVENT:
                    self.isGameOver = True

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE
                    and self.isGameOver
                ):
                    running = False

                self.player.handleEvent(event)

            self.pressed_keys = pygame.key.get_pressed()
            self.pressed_mouses = pygame.mouse.get_pressed()

            ## Update
            self.update()

            ## Draw
            self.draw()

            pygame.display.flip()
            self.dt = self.clock.tick(60) / 1000 * constants.GAME_SPEED_SCALE

        self.run()

    def update(self):
        if self.isGameOver:
            return
        self.powerUpUpdate()

        # update objs
        for x in self.objs:
            x.update(self)

        # detect and handle collision
        for x in range(0, len(self.objs) - 1):
            for y in range(x + 1, len(self.objs)):
                App.checkAndHandleCollision(self.objs[x], self.objs[y])

        # remove destroyed objs
        for x in self.objs:
            if x.checkIsDead():
                self.objs.remove(x)

    def powerUpUpdate(self):
        self.remaningSpawnPowerTime -= self.dt
        if self.remaningSpawnPowerTime <= 0:
            self.remaningSpawnPowerTime = 5
            self.objs.append(PowerUp(6, 5, self.generatePlayerPowerUp()))

    def generatePlayerPowerUp(self):
        def speedUp(p):
            p.speed += 5

        return speedUp

    def draw(self):
        self.screen.fill((0, 0, 0))  # clean screen
        # game over
        if self.isGameOver:
            text_surface = my_font.render(
                "You Lose! Hit 'SPACE' to play new game", False, (255, 255, 0)
            )
            self.screen.blit(text_surface, (0, 0))
            return

        # draw objs
        for x in self.objs:
            x.draw(self)


App().run()
